from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2.low_level import Type

from app.core.config import settings

password_hasher = PasswordHasher(type=Type.ID)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def generate_session_token() -> str:
    return secrets.token_urlsafe(48)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def is_token_match(raw_token: str, token_hash: str) -> bool:
    computed_hash = hash_token(raw_token)
    return secrets.compare_digest(computed_hash, token_hash)


def build_session_expiry(now: datetime | None = None) -> datetime:
    base_time = now or datetime.utcnow()
    return base_time + timedelta(minutes=settings.SESSION_TTL_MINUTES)
