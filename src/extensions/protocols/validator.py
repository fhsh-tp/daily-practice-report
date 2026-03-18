"""SubmissionValidator Protocol — defines the interface for submission validators."""
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass
class ValidationResult:
    valid: bool
    error_message: str = ""


@runtime_checkable
class SubmissionValidator(Protocol):
    """
    Protocol for submission validators.

    Implement this to add custom validation logic before persisting a submission.
    All registered validators are invoked before saving; any invalid result rejects.
    """

    async def validate(
        self,
        submission_data: dict[str, Any],
        template: Any,
    ) -> ValidationResult:
        """
        Validate a submission against the given template.

        Args:
            submission_data: Dict mapping field names to submitted values.
            template: The TaskTemplate document for this submission.

        Returns:
            ValidationResult with valid=True if the submission passes,
            or valid=False with an error_message if it should be rejected.
        """
        ...
