"""AuthProvider Protocol — defines the interface for authentication providers."""
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AuthProvider(Protocol):
    """
    Protocol for authentication providers.

    Implement this to add a new authentication method (e.g., Google OAuth,
    SAML, custom SSO). Register with ExtensionRegistry under key "auth".
    """

    async def authenticate(self, credentials: dict[str, Any]) -> Any:
        """
        Authenticate a user from the given credentials dict.

        Args:
            credentials: Provider-specific credential map.
                Local: {"username": str, "password": str}
                OAuth: {"token": str, "provider": str}

        Returns:
            A User document if authentication succeeds.

        Raises:
            ValueError: If credentials are invalid or authentication fails.
        """
        ...
