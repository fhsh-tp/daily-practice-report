"""FastAPI Depends factories for Extension Registry."""
from typing import Any

from extensions.protocols import AuthProvider, BadgeTrigger, RewardProvider, SubmissionValidator
from extensions.registry import registry


def get_auth_provider(key: str = "local"):
    """Return a FastAPI Depends factory for the AuthProvider with the given key."""
    def _dep() -> Any:
        return registry.get(AuthProvider, key)
    return _dep


def get_reward_providers() -> list[Any]:
    """Return all registered RewardProvider implementations."""
    return registry.get_all(RewardProvider)


def get_badge_triggers() -> list[Any]:
    """Return all registered BadgeTrigger implementations."""
    return registry.get_all(BadgeTrigger)


def get_submission_validators() -> list[Any]:
    """Return all registered SubmissionValidator implementations."""
    return registry.get_all(SubmissionValidator)
