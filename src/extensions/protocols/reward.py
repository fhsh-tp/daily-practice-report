"""RewardProvider Protocol — defines the interface for reward awarding logic."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class RewardEventType(str, Enum):
    CHECKIN = "checkin"
    SUBMISSION = "submission"
    MANUAL = "manual"


@dataclass
class RewardEvent:
    event_type: RewardEventType
    student_id: str
    class_id: str
    source_id: str  # checkin record ID or submission ID
    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now(timezone.utc)


@runtime_checkable
class RewardProvider(Protocol):
    """
    Protocol for reward providers.

    Implement this to define how points are awarded for a given event.
    Multiple providers can be registered; all are invoked per event.
    """

    async def award(self, event: RewardEvent) -> Any | None:
        """
        Award points for the given reward event.

        Args:
            event: The reward event that triggered this call.

        Returns:
            A PointTransaction document if points were awarded, None otherwise.
        """
        ...
