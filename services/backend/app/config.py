from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

from .throttle import DEFAULT_BUDGETS, Budget, budgets_from_env


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _secret(name: str) -> str:
    """Read a signing secret. F28: with REDIS_URL set, an empty secret fails boot.

    A random per-process secret would invalidate every session and PAT on each restart
    (and differ between workers), so the shore deployment refuses it. Without Redis
    (local dev, tests) a throwaway secret is still generated.
    """
    value = os.getenv(name, "").strip()
    if value:
        return value
    if os.getenv("REDIS_URL", "").strip():
        raise RuntimeError(
            f"{name} is empty while REDIS_URL is set; run `python3 scripts/ensure_env_secrets.py` "
            "(or `make env-secrets`) to write stable secrets into .env"
        )
    return secrets.token_urlsafe(32)


@dataclass(frozen=True)
class Settings:
    ttod_path: Path = REPOSITORY_ROOT / "ttod.yml"
    schema_dir: Path = REPOSITORY_ROOT / "schema"
    proposal_dir: Path = REPOSITORY_ROOT / "services/backend/data/proposals"
    session_secret: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    session_ttl_seconds: int = 3600
    pat_secret: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    pat_ttl_seconds: int = 3600
    admin_email: str = "admin@ttod.local"
    admin_password_hash: str = ""
    redis_url: str = ""
    ollama_mode: str = "host"
    ollama_model: str = ""
    ollama_embed_model: str = "nomic-embed-text"
    ollama_base_url: str = "http://host.containers.internal:11434"
    mcp_server_url: str = "http://mcp:3001"
    retrieval_threshold: float = 0.575
    retrieval_top_k: int = 5
    # AA2 (F4): signed-cookie sessions are refused unless explicitly re-enabled.
    allow_signed_session_fallback: bool = False
    # AA2 (F3): trust the left-most X-Forwarded-For hop as the client IP. True in Compose, where the
    # backend is reachable only through Caddy (which replaces untrusted XFF) and Astro (which
    # forwards Caddy's value). Never enable it on a backend published directly.
    trust_forwarded_for: bool = False
    throttle_budgets: dict[str, Budget] = field(default_factory=lambda: dict(DEFAULT_BUDGETS))

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("OLLAMA_MODE", "host")
        if mode not in {"host", "container"}:
            raise ValueError("OLLAMA_MODE must be 'host' or 'container'")
        return cls(
            ttod_path=Path(os.getenv("TTOD_PATH", str(REPOSITORY_ROOT / "ttod.yml"))),
            schema_dir=Path(os.getenv("TTOD_SCHEMA_DIR", str(REPOSITORY_ROOT / "schema"))),
            proposal_dir=Path(os.getenv("TTOD_PROPOSAL_DIR", str(REPOSITORY_ROOT / "services/backend/data/proposals"))),
            session_secret=_secret("TTOD_SESSION_SECRET"),
            session_ttl_seconds=int(os.getenv("TTOD_SESSION_TTL_SECONDS", "3600")),
            pat_secret=_secret("TTOD_PAT_SECRET"),
            pat_ttl_seconds=int(os.getenv("TTOD_PAT_TTL_SECONDS", "3600")),
            admin_email=os.getenv("TTOD_ADMIN_EMAIL", "admin@ttod.local"),
            admin_password_hash=os.getenv("TTOD_ADMIN_PASSWORD_HASH", ""),
            redis_url=os.getenv("REDIS_URL", ""),
            ollama_mode=mode,
            ollama_model=os.getenv("OLLAMA_MODEL", ""),
            ollama_embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://host.containers.internal:11434").rstrip("/"),
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://mcp:3001").rstrip("/"),
            retrieval_threshold=float(os.getenv("ORACLE_RETRIEVAL_THRESHOLD", "0.575")),
            retrieval_top_k=int(os.getenv("ORACLE_RETRIEVAL_TOP_K", "5")),
            allow_signed_session_fallback=os.getenv("TTOD_ALLOW_SIGNED_SESSION_FALLBACK", "0") == "1",
            trust_forwarded_for=os.getenv("TTOD_TRUST_FORWARDED_FOR", "1") == "1",
            throttle_budgets=budgets_from_env(),
        )
