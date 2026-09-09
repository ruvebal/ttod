"""Auth hello-world: httpOnly signed session + a separate bearer PAT.

Two credential surfaces on purpose (FE I: JWT lesson + Framework-mode session lesson).
A leaked PAT is not a live browser session, and the session cookie is not a PAT.
This module gates *who* may act; it never writes ttod.yml or calls ttod_core.repository.
"""

from __future__ import annotations

import json
import logging
from typing import Literal

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from .config import Settings

log = logging.getLogger("ttod.auth")

UserRole = Literal["student", "reviewer", "instructor"]

# Long-lived for bot/API use; still signed and typed so it cannot be confused with a session.
PAT_MAX_AGE_SECONDS = 60 * 60 * 24 * 90
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7
PAT_SALT = "ttod-pat-v1"


class PublicUser(BaseModel):
    """Wire shape matching frontend domain.ts `User`. Not a session object."""

    id: str
    email: str
    displayName: str
    role: UserRole


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    token: str
    token_type: Literal["Bearer"] = "Bearer"
    shown_once: bool = True
    notice: str


def _audit(event: str, **fields: object) -> None:
    payload = {"event": event, **fields}
    log.info(json.dumps(payload, default=str))


class AuthService:
    """One seeded user, passlib/bcrypt hashes, PAT signer with a distinct secret."""

    def __init__(self, settings: Settings):
        self._cookie_name = settings.session_cookie_name
        self._pwd = CryptContext(schemes=["bcrypt"], bcrypt__default_rounds=4, deprecated="auto")
        role = settings.seed_user_role
        if role not in {"student", "reviewer", "instructor"}:
            raise ValueError("seed_user_role must be student, reviewer, or instructor")
        self._user = PublicUser(
            id=settings.seed_user_id,
            email=settings.seed_user_email,
            displayName=settings.seed_user_display_name,
            role=role,
        )
        self._password_hash = self._pwd.hash(settings.seed_user_password)
        # Dummy hash so a missing user still runs verify() (timing-neighbour, not a second account).
        self._dummy_hash = self._pwd.hash("ttod-dummy-hash-not-a-login")
        self._pat = URLSafeTimedSerializer(settings.pat_secret, salt=PAT_SALT)

    @property
    def cookie_name(self) -> str:
        return self._cookie_name

    def authenticate(self, email: str, password: str) -> PublicUser | None:
        matched = email.strip().lower() == self._user.email.lower()
        hashed = self._password_hash if matched else self._dummy_hash
        ok = self._pwd.verify(password, hashed)
        if not (matched and ok):
            return None
        return self._user

    def user_for_id(self, user_id: str | None) -> PublicUser | None:
        if user_id == self._user.id:
            return self._user
        return None

    def issue_pat(self, user: PublicUser) -> str:
        # typ=pat is the discriminant: this blob is not a session cookie payload.
        return self._pat.dumps({"sub": user.id, "role": user.role, "typ": "pat"})

    def read_pat(self, token: str) -> PublicUser | None:
        try:
            payload = self._pat.loads(token, max_age=PAT_MAX_AGE_SECONDS)
        except (BadSignature, SignatureExpired, TypeError, ValueError):
            return None
        if not isinstance(payload, dict) or payload.get("typ") != "pat":
            return None
        return self.user_for_id(str(payload.get("sub", "")))


def current_user(request: Request) -> PublicUser | None:
    auth: AuthService = request.app.state.auth
    uid = request.session.get("uid")
    if not isinstance(uid, str):
        return None
    return auth.user_for_id(uid)


def require_session_user(request: Request) -> PublicUser:
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def create_auth_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

    @router.post("/login")
    def login(payload: LoginRequest, request: Request) -> PublicUser:
        auth: AuthService = request.app.state.auth
        user = auth.authenticate(payload.email, payload.password)
        if user is None:
            _audit("login_failure")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        request.session.clear()
        request.session["uid"] = user.id
        _audit("login_success", user_id=user.id)
        return user

    @router.post("/logout", status_code=204)
    def logout(request: Request) -> Response:
        request.session.clear()
        _audit("logout")
        return Response(status_code=204)

    @router.get("/me")
    def me(request: Request) -> PublicUser:
        return require_session_user(request)

    @router.post("/token")
    def issue_token(request: Request) -> TokenResponse:
        user = require_session_user(request)
        auth: AuthService = request.app.state.auth
        token = auth.issue_pat(user)
        _audit("pat_issued", user_id=user.id)
        return TokenResponse(
            token=token,
            notice=(
                "Store this personal access token now; it is shown here once. "
                "It is a separate credential from your browser session cookie — "
                "a leaked token is not a live session, and vice versa. "
                "Teaching-only seed user; never reuse a real password."
            ),
        )

    return router


def mount_auth(app: FastAPI, settings: Settings) -> None:
    app.state.auth = AuthService(settings)
    app.include_router(create_auth_router())
    # httpOnly + signed is SessionMiddleware's default; https_only stays off for the local HTTP teaching stack.
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie=settings.session_cookie_name,
        same_site="lax",
        https_only=False,
        max_age=SESSION_MAX_AGE_SECONDS,
        path="/",
    )
