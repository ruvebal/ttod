from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    ttod_path: Path = REPOSITORY_ROOT / "ttod.yml"
    schema_dir: Path = REPOSITORY_ROOT / "schema"
    proposal_dir: Path = REPOSITORY_ROOT / "services/backend/data/proposals"
    ollama_mode: str = "host"
    ollama_model: str = ""
    ollama_embed_model: str = "nomic-embed-text"
    ollama_base_url: str = "http://host.containers.internal:11434"
    mcp_server_url: str = "http://mcp:3001"
    retrieval_threshold: float = 0.575
    retrieval_top_k: int = 5
    # Auth hello-world (TS4c). Defaults are teaching-only; never reuse a real password.
    session_secret: str = "dev-insecure-session-secret-not-for-production"
    session_cookie_name: str = "ttod_session"
    pat_secret: str = "dev-insecure-pat-secret-not-for-production"
    seed_user_id: str = "user-seed-student"
    seed_user_email: str = "student@ttod.local"
    seed_user_password: str = "ttod-teaching-only-not-a-real-password"
    seed_user_display_name: str = "Cohort Student"
    seed_user_role: str = "student"

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("OLLAMA_MODE", "host")
        if mode not in {"host", "container"}:
            raise ValueError("OLLAMA_MODE must be 'host' or 'container'")
        role = os.getenv("TTOD_SEED_USER_ROLE", "student")
        if role not in {"student", "reviewer", "instructor"}:
            raise ValueError("TTOD_SEED_USER_ROLE must be student, reviewer, or instructor")
        session_secret = os.getenv("TTOD_SESSION_SECRET", "dev-insecure-session-secret-not-for-production")
        pat_secret = os.getenv("TTOD_PAT_SECRET", "dev-insecure-pat-secret-not-for-production")
        if not session_secret or not pat_secret:
            raise ValueError("TTOD_SESSION_SECRET and TTOD_PAT_SECRET must be non-empty")
        if session_secret == pat_secret:
            raise ValueError("TTOD_PAT_SECRET must differ from TTOD_SESSION_SECRET — session and bearer are separate credentials")
        return cls(
            ttod_path=Path(os.getenv("TTOD_PATH", str(REPOSITORY_ROOT / "ttod.yml"))),
            schema_dir=Path(os.getenv("TTOD_SCHEMA_DIR", str(REPOSITORY_ROOT / "schema"))),
            proposal_dir=Path(os.getenv("TTOD_PROPOSAL_DIR", str(REPOSITORY_ROOT / "services/backend/data/proposals"))),
            ollama_mode=mode,
            ollama_model=os.getenv("OLLAMA_MODEL", ""),
            ollama_embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://host.containers.internal:11434").rstrip("/"),
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://mcp:3001").rstrip("/"),
            retrieval_threshold=float(os.getenv("ORACLE_RETRIEVAL_THRESHOLD", "0.575")),
            retrieval_top_k=int(os.getenv("ORACLE_RETRIEVAL_TOP_K", "5")),
            session_secret=session_secret,
            session_cookie_name=os.getenv("TTOD_SESSION_COOKIE_NAME", "ttod_session"),
            pat_secret=pat_secret,
            seed_user_id=os.getenv("TTOD_SEED_USER_ID", "user-seed-student"),
            seed_user_email=os.getenv("TTOD_SEED_USER_EMAIL", "student@ttod.local"),
            seed_user_password=os.getenv("TTOD_SEED_USER_PASSWORD", "ttod-teaching-only-not-a-real-password"),
            seed_user_display_name=os.getenv("TTOD_SEED_USER_DISPLAY_NAME", "Cohort Student"),
            seed_user_role=role,
        )
