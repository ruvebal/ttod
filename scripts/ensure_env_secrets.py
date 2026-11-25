#!/usr/bin/env python3
"""Ensure local .env has stable shore secrets (idempotent; never overwrites set values).

Fills empty TTOD_SESSION_SECRET / TTOD_PAT_SECRET, merges missing keys from
.env.example, and (when passlib is available) seeds TTOD_ADMIN_PASSWORD_HASH
once, writing the plaintext password to .env.admin-password (gitignored via .env*).
"""

from __future__ import annotations

import secrets
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"
ADMIN_PASSWORD_PATH = ROOT / ".env.admin-password"


def _parse(text: str) -> list[tuple[str, str | None, str]]:
    """Return rows as (kind, key, raw_line) where kind is 'assign' | 'other'."""
    rows: list[tuple[str, str | None, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            rows.append(("other", None, line))
            continue
        key, _, _ = line.partition("=")
        if key.strip().startswith("#"):
            rows.append(("other", None, line))
            continue
        rows.append(("assign", key.strip(), line))
    return rows


def _value_map(rows: list[tuple[str, str | None, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for kind, key, line in rows:
        if kind != "assign" or key is None:
            continue
        out[key] = line.partition("=")[2]
    return out


def _set_value(rows: list[tuple[str, str | None, str]], key: str, value: str) -> None:
    for i, (kind, k, line) in enumerate(rows):
        if kind == "assign" and k == key:
            rows[i] = ("assign", key, f"{key}={value}")
            return
    rows.append(("assign", key, f"{key}={value}"))


def _merge_missing_from_example(env_rows: list[tuple[str, str | None, str]], example_text: str) -> None:
    present = {k for kind, k, _ in env_rows if kind == "assign" and k}
    for kind, key, line in _parse(example_text):
        if kind == "assign" and key is not None and key not in present:
            env_rows.append(("assign", key, line))
            present.add(key)


def _hash_password(password: str) -> str | None:
    try:
        from passlib.context import CryptContext
    except ImportError:
        return None
    return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)


def _for_compose(value: str) -> str:
    """Escape `$` for Docker Compose `.env` interpolation (`$2b$…` bcrypt → `$$2b$$…`)."""
    if "$$" in value:
        return value
    return value.replace("$", "$$")


def main() -> int:
    if not EXAMPLE_PATH.is_file():
        print(f"missing {EXAMPLE_PATH}", file=sys.stderr)
        return 1

    if not ENV_PATH.is_file():
        ENV_PATH.write_text(EXAMPLE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"created {ENV_PATH.name} from .env.example")

    rows = _parse(ENV_PATH.read_text(encoding="utf-8"))
    _merge_missing_from_example(rows, EXAMPLE_PATH.read_text(encoding="utf-8"))
    values = _value_map(rows)
    changed: list[str] = []

    session = values.get("TTOD_SESSION_SECRET", "").strip()
    pat = values.get("TTOD_PAT_SECRET", "").strip()
    if not session:
        session = secrets.token_urlsafe(32)
        _set_value(rows, "TTOD_SESSION_SECRET", session)
        changed.append("TTOD_SESSION_SECRET")
    if not pat or pat == session:
        pat = secrets.token_urlsafe(32)
        while pat == session:
            pat = secrets.token_urlsafe(32)
        _set_value(rows, "TTOD_PAT_SECRET", pat)
        changed.append("TTOD_PAT_SECRET")

    admin_hash = values.get("TTOD_ADMIN_PASSWORD_HASH", "").strip()
    if not admin_hash:
        password = secrets.token_urlsafe(18)
        digest = _hash_password(password)
        if digest is None:
            print(
                "passlib not installed — left TTOD_ADMIN_PASSWORD_HASH empty "
                "(run: make venv && make env-secrets)",
                file=sys.stderr,
            )
        else:
            _set_value(rows, "TTOD_ADMIN_PASSWORD_HASH", _for_compose(digest))
            ADMIN_PASSWORD_PATH.write_text(
                f"# Local only — gitignored. Admin email is TTOD_ADMIN_EMAIL in .env\n"
                f"{password}\n",
                encoding="utf-8",
            )
            ADMIN_PASSWORD_PATH.chmod(0o600)
            changed.append("TTOD_ADMIN_PASSWORD_HASH")
            print(f"admin password written once to {ADMIN_PASSWORD_PATH.name}")
    elif admin_hash.startswith("$") and "$$" not in admin_hash:
        # Already hashed, but Compose would eat `$2b$12$…` — escape in place.
        _set_value(rows, "TTOD_ADMIN_PASSWORD_HASH", _for_compose(admin_hash))
        changed.append("TTOD_ADMIN_PASSWORD_HASH")
        print("escaped TTOD_ADMIN_PASSWORD_HASH dollars for Docker Compose")

    if not values.get("REDIS_URL", "").strip():
        _set_value(rows, "REDIS_URL", "redis://redis:6379/0")
        changed.append("REDIS_URL")

    ENV_PATH.write_text("\n".join(line for _, _, line in rows) + "\n", encoding="utf-8")
    if changed:
        print("filled: " + ", ".join(changed))
    else:
        print("env secrets already set — no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
