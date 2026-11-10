from __future__ import annotations

import unicodedata
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SessionRole = Literal["student", "reviewer", "instructor"]


class AuthUser(BaseModel):
    id: str
    email: str
    roles: list[SessionRole]
    # Set by PATCH /auth/profile (D5); omitted from responses while unset, so the login contract is unchanged.
    display_name: str | None = None


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


class AuthRegisterRequest(BaseModel):
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # bcrypt solo usa los primeros 72 bytes: se rechaza antes que recortarla sin avisar.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes")
        return value


def _password_fits_bcrypt(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 bytes")
    return value


class PasswordChangeRequest(BaseModel):
    """F55 (AA2): same length rules as register; revokes the other sessions by default."""

    current_password: str = Field(min_length=1, max_length=1024)
    new_password: str = Field(min_length=8)
    revoke_others: bool = True

    @field_validator("new_password")
    @classmethod
    def new_password_fits_bcrypt(cls, value: str) -> str:
        return _password_fits_bcrypt(value)


class ProfileUpdateRequest(BaseModel):
    display_name: str

    @field_validator("display_name")
    @classmethod
    def plain_short_name(cls, value: str) -> str:
        value = unicodedata.normalize("NFC", value).strip()
        if not 1 <= len(value) <= 40:
            raise ValueError("display_name must be 1–40 characters")
        # No markup, and no invisible or direction-changing characters (Cc/Cf: e.g. U+202E, U+200B).
        if any(ch in value for ch in "<>") or any(unicodedata.category(ch) in {"Cc", "Cf"} for ch in value):
            raise ValueError("display_name must be plain, visible text")
        return value


class AuthLoginResponse(BaseModel):
    session_token: str
    token_type: Literal["Session"] = "Session"
    expires_in: int
    user: AuthUser


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int


class FavoriteRequest(BaseModel):
    quoteId: str = Field(min_length=1, max_length=200)


class ProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    text: str = Field(min_length=1, max_length=2000)
    section: str = Field(min_length=1, max_length=100)
    source: str | None = Field(default=None, min_length=1, max_length=2000)
    level: Literal["beginner", "intermediate", "advanced", "master"] = "intermediate"
    tags: list[str] = Field(default_factory=list, max_length=20)
    teaches: str | None = Field(default=None, min_length=1, max_length=2000)
    lang: Literal["en", "es"] = "en"


class ProposalCreated(BaseModel):
    proposal_id: str
    status: str


class OracleQueryPayload(BaseModel):
    query: str = Field(min_length=1, max_length=8000)
    contextTag: str | None = None
    sessionHistory: list[str] = Field(default_factory=list, max_length=50)
    locale: Literal["en", "es"] | None = None


class OracleProposeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=8000)
    creativeAnswer: str = Field(min_length=1, max_length=16000)
    suggestedSection: str | None = None
    suggestedTags: list[str] | None = None
    locale: Literal["en", "es"] | None = None


class OracleResponseChunk(BaseModel):
    mode: Literal["grounded", "creative"]
    citedQuoteIds: list[str] | None = None
    themes: list[str] | None = None
    tags: list[str] | None = None
    text: str

