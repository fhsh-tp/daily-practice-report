"""BadgeTrigger Protocol — defines the interface for badge trigger conditions."""
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from extensions.protocols.reward import RewardEvent


@dataclass
class TriggerContext:
    """Context passed to BadgeTrigger.evaluate() for decision making."""
    class_id: str
    extra: dict[str, Any] = None

    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


@runtime_checkable
class BadgeTrigger(Protocol):
    """
    Protocol for badge triggers.

    Implement this to define a custom badge award condition.
    All registered triggers are evaluated after every RewardEvent.
    """

    async def evaluate(
        self,
        student_id: str,
        event: RewardEvent,
        context: TriggerContext,
    ) -> bool:
        """
        Evaluate whether the badge should be awarded to the student.

        Args:
            student_id: The student to evaluate.
            event: The reward event that triggered evaluation.
            context: Additional context for the evaluation.

        Returns:
            True if the badge condition is met, False otherwise.
        """
        ...
