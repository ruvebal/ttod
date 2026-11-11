from __future__ import annotations

import hashlib
import logging
import random
from contextlib import asynccontextmanager
from dataclasses import replace
from typing import Any

import redis
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response, StreamingResponse

from ttod_core.proposals import create_proposal

from .auth import (
    SESSION_COOKIE_NAME,
    AccessTokenClaims,
    AuthService,
    RequireAccessToken,
    RequireSession,
    SessionClaims,
)
from .access_log import install_access_log
from .config import Settings
from .revocation import MemoryTokenRegistry, RedisTokenRegistry, TokenRegistry
from .throttle import MemoryThrottle, RedisThrottle, Throttle
from .favorites import FavoriteStore, MemoryFavoriteStore, RedisFavoriteStore
from .models import (
    AuthLoginRequest,
    AuthLoginResponse,
    AuthRegisterRequest,
    AuthUser,
    FavoriteRequest,
    OracleProposeRequest,
    OracleQueryPayload,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    ProposalCreated,
    ProposalRequest,
    TokenResponse,
)
from .oracle import OracleService
from .proposal_drafts import DualWriteProposalDraftStore, FilesystemProposalDraftStore, ProposalDraftStore
from .redis_client import create_redis_client, redis_ping
from .sessions import MemorySessionStore, RedisSessionStore, SessionStore
from .storage import SnapshotService
from .users import MemoryUserStore, RedisUserStore, UserStore


logger = logging.getLogger(__name__)


def _build_shore(
    settings: Settings,
    *,
    redis_client: Any | None = None,
    users: UserStore | None = None,
    sessions: SessionStore | None = None,
    favorites: FavoriteStore | None = None,
    proposals: ProposalDraftStore | None = None,
) -> tuple[Any | None, UserStore, SessionStore, FavoriteStore, ProposalDraftStore]:
    client = redis_client
    if client is None and settings.redis_url.strip():
        client = create_redis_client(settings.redis_url)

    if users is None:
        users = RedisUserStore(client=client) if client is not None else MemoryUserStore()
    if sessions is None:
        sessions = RedisSessionStore(client=client) if client is not None else MemorySessionStore()
    if favorites is None:
        favorites = (
            RedisFavoriteStore(settings.redis_url, client=client)
            if client is not None
            else MemoryFavoriteStore()
        )
    if proposals is None:
        proposals = (
            DualWriteProposalDraftStore(settings.proposal_dir, client=client)
            if client is not None
            else FilesystemProposalDraftStore(settings.proposal_dir)
        )
    return client, users, sessions, favorites, proposals


def create_app(
    settings: Settings | None = None,
    oracle: OracleService | None = None,
    favorites: FavoriteStore | None = None,
    *,
    users: UserStore | None = None,
    sessions: SessionStore | None = None,
    proposals: ProposalDraftStore | None = None,
    redis_client: Any | None = None,
    throttle: Throttle | None = None,
    registry: TokenRegistry | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    snapshots = SnapshotService(settings.ttod_path, settings.schema_dir)
    oracle = oracle or OracleService(settings, snapshots)
    shore_client, users, sessions, favorites, proposals = _build_shore(
        settings,
        redis_client=redis_client,
        users=users,
        sessions=sessions,
        favorites=favorites,
        proposals=proposals,
    )
    # Throttle and token registry live in Redis when the app built its own client from REDIS_URL.
    # An injected client is a test double, so tests get the in-memory versions unless they pass one.
    real_redis = shore_client is not None and redis_client is None
    throttle = throttle or (RedisThrottle(shore_client) if real_redis else MemoryThrottle())
    registry = registry or (RedisTokenRegistry(shore_client) if real_redis else MemoryTokenRegistry())
    if shore_client is not None and not real_redis:
        logger.info("Injected Redis client: throttle and token registry run in memory (tests only)")
    auth_service = AuthService(
        settings.session_secret,
        settings.session_ttl_seconds,
        settings.admin_email,
        settings.admin_password_hash,
        settings.pat_secret,
        settings.pat_ttl_seconds,
        users=users,
        sessions=sessions,
        registry=registry,
        allow_signed_fallback=settings.allow_signed_session_fallback,
    )
    require_session = RequireSession(auth_service)

    def client_ip(request: Request) -> str:
        if settings.trust_forwarded_for:
            first = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            if first:
                return first
        return request.client.host if request.client else "unknown"

    def guard(bucket: str, key: str) -> None:
        """Count one attempt; 429 with Retry-After once the budget is spent (F3 / F20)."""
        budget = settings.throttle_budgets[bucket]
        if not throttle.hit(bucket, key, budget):
            raise HTTPException(
                status_code=429,
                detail="Too many attempts; try again later",
                headers={"Retry-After": str(budget.window)},
            )

    def auth_user(claims: SessionClaims) -> AuthUser:
        record = users.get_by_id(claims.user_id)
        return AuthUser(
            id=claims.user_id,
            email=claims.email,
            roles=list(claims.roles),
            display_name=getattr(record, "display_name", "") or None,
        )

    require_access_token = RequireAccessToken(auth_service)
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        # El primer `ttod.yml` se lee al arrancar y no en la primera visita: cargarlo y
        # validarlo cuesta ~1 s, y sin esto lo pagaba quien abriese la portada primero.
        # Si falla, el backend arranca igual y la primera petición lo vuelve a intentar.
        try:
            await run_in_threadpool(snapshots.wisdom)
        except Exception:  # noqa: BLE001
            logging.getLogger(__name__).warning("No se pudo precargar ttod.yml al arrancar", exc_info=True)
        yield

    app = FastAPI(title="TTOD Oracle Backend", version="1.0.0", lifespan=lifespan)
    # F48: request id + one JSON access line per request (uvicorn's own access log is off in the image).
    install_access_log(app)

    @app.get("/health")
    def health():
        try:
            payload = snapshots.health()
        except Exception as exc:
            # F47: the reason goes to the log, never to the client (it can name paths and hosts).
            logger.exception("TTOD repository unavailable")
            raise HTTPException(status_code=503, detail="TTOD repository unavailable") from exc
        if settings.redis_url.strip() or shore_client is not None:
            redis_ok = shore_client is not None and redis_ping(shore_client)
            payload = {**payload, "redis": "ok" if redis_ok else "down"}
            if not redis_ok:
                # F27: the shore APIs answer 503 without Redis, so health must too; the
                # Compose healthcheck (urlopen raises on 503) then marks the backend unhealthy.
                return JSONResponse(status_code=503, content={**payload, "status": "degraded"})
        return payload

    @app.get("/api/v1/schema/definitions")
    def definitions():
        return snapshots.definitions()

    @app.get("/api/v1/wisdom/sample")
    def wisdom_sample():
        return snapshots.wisdom()

    @app.post("/api/v1/auth/login", response_model=AuthLoginResponse, response_model_exclude_none=True)
    def login(payload: AuthLoginRequest, request: Request):
        try:
            guard("login-ip", client_ip(request))
            guard("account", payload.email.strip().casefold())
            claims = auth_service.authenticate(payload.email, payload.password)
            if claims is None:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            session_token = auth_service.issue_session(claims)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Session store unavailable") from exc
        return AuthLoginResponse(
            session_token=session_token,
            expires_in=auth_service.session_ttl_seconds,
            user=AuthUser(id=claims.user_id, email=claims.email, roles=list(claims.roles)),
        )

    @app.post("/api/v1/auth/register", status_code=201, response_model=AuthLoginResponse, response_model_exclude_none=True)
    def register(payload: AuthRegisterRequest, request: Request):
        try:
            guard("register-ip", client_ip(request))
            claims = auth_service.register(payload.email, payload.password)
            if claims is None:
                raise HTTPException(status_code=409, detail="Email already registered")
            # Tras el alta la sesión ya queda abierta: no se vuelve a pedir la contraseña.
            session_token = auth_service.issue_session(claims)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="User store unavailable") from exc
        return AuthLoginResponse(
            session_token=session_token,
            expires_in=auth_service.session_ttl_seconds,
            user=AuthUser(id=claims.user_id, email=claims.email, roles=list(claims.roles)),
        )

    @app.get("/api/v1/auth/session", response_model=AuthUser, response_model_exclude_none=True)
    def auth_session(claims: SessionClaims = Depends(require_session)):
        try:
            return auth_user(claims)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="User store unavailable") from exc

    @app.post("/api/v1/auth/logout", status_code=204)
    def logout(
        session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    ):
        try:
            auth_service.revoke_session(session_token or "")
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Session store unavailable") from exc
        return Response(status_code=204)

    @app.post("/api/v1/auth/logout-all", status_code=204)
    def logout_all(claims: SessionClaims = Depends(require_session)):
        """Sign out everywhere: every session row of the user and every PAT they hold."""
        try:
            auth_service.revoke_user_sessions(claims.user_id)
            auth_service.revoke_user_pats(claims.user_id)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Session store unavailable") from exc
        return Response(status_code=204)

    @app.post("/api/v1/auth/password", response_model=AuthLoginResponse, response_model_exclude_none=True)
    def change_password(
        payload: PasswordChangeRequest,
        claims: SessionClaims = Depends(require_session),
        session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    ):
        """F55: verify the current password, store the new one, rotate the caller's sid and,
        by default, revoke every other session and every PAT of the user."""
        try:
            guard("account", claims.email.strip().casefold())
            if not auth_service.verify_password(claims.user_id, payload.current_password):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            auth_service.change_password(claims.user_id, payload.new_password)
            if payload.revoke_others:
                auth_service.revoke_user_sessions(claims.user_id)
                auth_service.revoke_user_pats(claims.user_id)
            else:
                auth_service.revoke_session(session_token or "")
            new_token = auth_service.issue_session(claims)
            user = auth_user(claims)
        except LookupError as exc:
            raise HTTPException(status_code=401, detail="Authentication required") from exc
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Session store unavailable") from exc
        return AuthLoginResponse(session_token=new_token, expires_in=auth_service.session_ttl_seconds, user=user)

    @app.patch("/api/v1/auth/profile", response_model=AuthUser, response_model_exclude_none=True)
    def update_profile(payload: ProfileUpdateRequest, claims: SessionClaims = Depends(require_session)):
        try:
            record = users.get_by_id(claims.user_id)
            if record is None:
                raise HTTPException(status_code=401, detail="Authentication required")
            users.upsert(replace(record, display_name=payload.display_name))
            return auth_user(claims)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="User store unavailable") from exc

    @app.delete("/api/v1/auth/token", status_code=204)
    def revoke_access_token(claims: AccessTokenClaims = Depends(require_access_token)):
        """Revoke the presented PAT before it expires (jti denylist, AA0 D7 b)."""
        try:
            auth_service.revoke_pat(claims)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Token store unavailable") from exc
        return Response(status_code=204)

    @app.post("/api/v1/auth/token", response_model=TokenResponse)
    def issue_access_token(claims: SessionClaims = Depends(require_session)):
        try:
            token = auth_service.issue_pat(claims.user_id)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Token store unavailable") from exc
        return TokenResponse(access_token=token, expires_in=auth_service.pat_ttl_seconds)

    @app.get("/api/v1/wisdom/random")
    def wisdom_random(_claims: AccessTokenClaims = Depends(require_access_token)):
        quotes = snapshots.wisdom()
        if not quotes:
            raise HTTPException(status_code=404, detail="No public wisdom available")
        return random.choice(quotes)

    @app.get("/api/v1/graph")
    def graph(request: Request):
        body = snapshots.graph_bytes()
        # ETag del cuerpo: quien ya lo tiene recibe un 304 vacío en vez de 138 KB.
        # Un minuto de vida (más diez de margen sirviendo el viejo mientras se revalida)
        # deja que Caddy o un CDN lo sirvan sin despertar al backend.
        etag = f'"{hashlib.sha256(body).hexdigest()[:32]}"'
        headers = {"ETag": etag, "Cache-Control": "public, max-age=60, stale-while-revalidate=600"}
        if etag in request.headers.get("if-none-match", ""):
            return Response(status_code=304, headers=headers)
        return Response(content=body, media_type="application/json", headers=headers)

    @app.post("/api/v1/oracle/stream")
    def oracle_stream(payload: OracleQueryPayload, _claims: SessionClaims = Depends(require_session)):
        # F24: the stream costs Ollama time; only signed-in users may start one (quota: AA6, F21).
        return StreamingResponse(oracle.stream(payload), media_type="text/event-stream")

    @app.post("/api/v1/oracle/propose", status_code=201)
    async def oracle_propose(payload: OracleProposeRequest, claims: SessionClaims = Depends(require_session)):
        # F24 + F26: signed in, inside the proposal budget, and saved through the same store as
        # every other proposal (dual-write in Compose).
        try:
            guard("proposal-user", claims.user_id)
            return await oracle.propose(payload, proposals)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Proposal store unavailable") from exc
        except OSError as exc:
            logger.exception("Unable to persist oracle proposal")
            raise HTTPException(status_code=500, detail="Unable to save proposal") from exc

    # El usuario de cada favorito sale siempre de la sesión, nunca del cuerpo de la petición.
    @app.post("/api/v1/favorites", status_code=201)
    def create_favorite(payload: FavoriteRequest, claims: SessionClaims = Depends(require_session)):
        if not any(entry["id"] == payload.quoteId for entry in snapshots.wisdom()):
            raise HTTPException(status_code=404, detail="Quote not found or not publicly active")
        try:
            # Una sesión puede sobrevivir a su usuario: sin este control se guardarían
            # favoritos a nombre de alguien que no existe en el almacén de usuarios.
            if users.get_by_id(claims.user_id) is None:
                raise HTTPException(status_code=401, detail="Authentication required")
            return favorites.save(claims.user_id, payload.quoteId)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Favorites store unavailable") from exc

    @app.get("/api/v1/favorites")
    def list_favorites(claims: SessionClaims = Depends(require_session)):
        try:
            entries = favorites.list(claims.user_id)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Favorites store unavailable") from exc
        # Una cita retirada del corpus público deja de aparecer aunque siga guardada.
        active_ids = {entry["id"] for entry in snapshots.wisdom()}
        return [entry for entry in entries if entry["quoteId"] in active_ids]

    @app.delete("/api/v1/favorites/{quote_id}", status_code=204)
    def delete_favorite(quote_id: str, claims: SessionClaims = Depends(require_session)):
        try:
            removed = favorites.remove(claims.user_id, quote_id)
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Favorites store unavailable") from exc
        if not removed:
            raise HTTPException(status_code=404, detail="Favorite not found")
        return Response(status_code=204)

    @app.post("/api/v1/proposals", status_code=201, response_model=ProposalCreated)
    def create_user_proposal(
        payload: ProposalRequest,
        claims: SessionClaims = Depends(require_session),
    ):
        # `origin` y el autor los fija el servidor: el cliente no puede declarar otra procedencia.
        candidate = {
            "text": payload.text,
            "section": payload.section,
            "level": payload.level,
            "origin": "human",
            "lang": payload.lang,
        }
        if payload.source is not None:
            candidate["source"] = payload.source
        if payload.tags:
            candidate["tags"] = payload.tags
        if payload.teaches is not None:
            candidate["teaches"] = payload.teaches

        try:
            guard("proposal-user", claims.user_id)
            proposal = create_proposal(
                candidate_content=candidate,
                proposer_kind="human",
                proposer_id=claims.user_id,
                generation_method="api-proposal-create",
            )
            proposals.save(proposal)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Proposal store unavailable") from exc
        except OSError as exc:
            logger.exception("Unable to persist proposal")
            raise HTTPException(status_code=500, detail="Unable to save proposal") from exc

        return ProposalCreated(proposal_id=proposal.proposal_id, status=proposal.status.value)

    # La cola solo la ve quien revisa: el rol se comprueba en el servidor, no ocultando la vista.
    @app.get("/api/v1/proposals")
    def list_proposals(claims: SessionClaims = Depends(require_session)):
        if not {"reviewer", "instructor"}.intersection(claims.roles):
            raise HTTPException(status_code=403, detail="Reviewer role required")
        try:
            return [proposal.to_dict() for proposal in proposals.list()]
        except redis.RedisError as exc:
            raise HTTPException(status_code=503, detail="Proposal store unavailable") from exc

    return app


app = create_app()
