"""JWT token creation and decoding."""
import logging
import os
from datetime import datetime, timedelta, timezone

import jwt

_DEFAULT_SECRET = "dev-secret-change-in-production"
_SECRET = os.getenv("SESSION_SECRET", _DEFAULT_SECRET)
_ALGORITHM = "HS256"
_DEFAULT_EXPIRES = int(os.getenv("JWT_EXPIRES_SECONDS", str(60 * 60 * 24)))  # 24h

_logger = logging.getLogger(__name__)


def check_secret_safety() -> None:
    """Warn or raise if SESSION_SECRET is using the default development value.

    In production (FASTAPI_APP_ENVIRONMENT=production), raises RuntimeError to
    prevent startup with an insecure secret. In other environments, logs a warning.
    """
    if _SECRET == _DEFAULT_SECRET:
        env = os.getenv("FASTAPI_APP_ENVIRONMENT", "development")
        if env == "production":
            raise RuntimeError(
                "SESSION_SECRET is using the default development value. "
                "Set SESSION_SECRET to a secure random value before running in production."
            )
        _logger.warning(
            "SESSION_SECRET is using the default development value. "
            "Change this in production."
        )


def create_access_token(
    user_id: str,
    permissions: int,
    expires_seconds: int | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id: The user's MongoDB ID as a string.
        permissions: The user's permission flags as an integer.
        expires_seconds: Token lifetime in seconds. Defaults to JWT_EXPIRES_SECONDS env var.

    Returns:
        A signed JWT string.
    """
    if expires_seconds is None:
        expires_seconds = _DEFAULT_EXPIRES

    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "permissions": permissions,
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
