"""Password hashing utilities using passlib bcrypt."""
from passlib.context import CryptContext

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return _ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return _ctx.verify(plain, hashed)


def validate_password_strength(plain: str) -> None:
    """Raise ValueError if the password does not meet strength requirements.

    Requirements:
    - Minimum 8 characters.
    """
    if len(plain) < 8:
        raise ValueError("密碼長度至少需要 8 個字元。")
