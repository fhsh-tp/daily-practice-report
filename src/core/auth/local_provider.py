"""LocalAuthProvider — username/password authentication."""
from typing import Any

from core.auth.password import verify_password
from core.users.models import User


class LocalAuthProvider:
    """Default AuthProvider using username + password stored in MongoDB."""

    async def authenticate(self, credentials: dict[str, Any]) -> User:
        """
        Authenticate using username and password.

        Raises:
            ValueError: If username not found or password is wrong.
        """
        username = credentials.get("username", "")
        password = credentials.get("password", "")

        user = await User.find_one(User.username == username)
        if user is None:
            raise ValueError("Invalid username or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("Account is disabled")

        return user
