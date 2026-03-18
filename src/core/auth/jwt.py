"""JWT token creation and decoding."""
import os
from datetime import datetime, timedelta, timezone

import jwt

_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-production")
_ALGORITHM = "HS256"
_DEFAULT_EXPIRES = int(os.getenv("JWT_EXPIRES_SECONDS", str(60 * 60 * 24)))  # 24h


def create_access_token(
    user_id: str,
    role: str,
    expires_seconds: int | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id: The user's MongoDB ID as a string.
        role: "student" or "teacher".
        expires_seconds: Token lifetime in seconds. Defaults to JWT_EXPIRES_SECONDS env var.

    Returns:
        A signed JWT string.
    """
    if expires_seconds is None:
        expires_seconds = _DEFAULT_EXPIRES

    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=expires_seconds),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid or tampered.
    """
    return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
