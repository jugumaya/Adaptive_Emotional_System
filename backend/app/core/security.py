"""
Security utilities for the AEE platform.

Password hashing: PBKDF2-HMAC-SHA256 (100,000 iterations) — no external
native dependencies required (no bcrypt/passlib build issues on Windows).

Tokens: standard JWT (python-jose), used for all 5 roles
(student, counselor, advisor, admin, management).
"""
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from jose import JWTError, jwt
from app.core.config import settings

HASH_ITERATIONS = 100_000


def _derive_hash(password: str) -> str:
    salt = settings.SECRET_KEY.encode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    return base64.urlsafe_b64encode(digest).decode("utf-8")


def hash_password(password: str) -> str:
    return _derive_hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(_derive_hash(plain), hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


__all__ = ["JWTError", "hash_password", "verify_password", "create_access_token", "decode_token"]
