"""Default RewardProvider implementations for check-in and submission."""
from typing import Any

from extensions.protocols.reward import RewardEvent, RewardEventType
from gamification.points.models import ClassPointConfig, PointTransaction
from gamification.points.service import award_points


class CheckinRewardProvider:
    """Awards points when a student checks in."""

    async def award(self, event: RewardEvent) -> PointTransaction | None:
        if event.event_type != RewardEventType.CHECKIN:
            return None

        config = await ClassPointConfig.find_one(
            ClassPointConfig.class_id == event.class_id
        )
        points = config.checkin_points if config else 5  # default 5

        return await award_points(
            student_id=event.student_id,
            class_id=event.class_id,
            amount=points,
            source_event="checkin",
            source_id=event.source_id,
        )


class SubmissionRewardProvider:
    """Awards points when a student submits a task."""

    async def award(self, event: RewardEvent) -> PointTransaction | None:
        if event.event_type != RewardEventType.SUBMISSION:
            return None

        config = await ClassPointConfig.find_one(
            ClassPointConfig.class_id == event.class_id
        )
        points = config.submission_points if config else 10  # default 10

        return await award_points(
            student_id=event.student_id,
            class_id=event.class_id,
            amount=points,
            source_event="submission",
            source_id=event.source_id,
        )
