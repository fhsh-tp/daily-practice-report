"""Built-in BadgeTrigger implementations."""
from extensions.protocols.badge import BadgeTrigger, TriggerContext
from extensions.protocols.reward import RewardEvent, RewardEventType


class ConsecutiveCheckinTrigger:
    """
    Awards badge when a student checks in N consecutive days.
    Register with key like 'checkin_streak_3'.
    """

    def __init__(self, required_streak: int):
        self.required_streak = required_streak

    async def evaluate(
        self,
        student_id: str,
        event: RewardEvent,
        context: TriggerContext,
    ) -> bool:
        if event.event_type != RewardEventType.CHECKIN:
            return False

        from tasks.checkin.models import CheckinRecord
        from datetime import date, timedelta

        records = await CheckinRecord.find(
            CheckinRecord.student_id == student_id,
            CheckinRecord.class_id == context.class_id,
        ).sort(-CheckinRecord.checked_in_at).to_list()

        if len(records) < self.required_streak:
            return False

        # Check that the last N records are on consecutive calendar days
        check_dates = sorted(
            {r.checked_in_at.date() for r in records},
            reverse=True,
        )
        streak = 1
        for i in range(1, len(check_dates)):
            if check_dates[i - 1] - check_dates[i] == timedelta(days=1):
                streak += 1
                if streak >= self.required_streak:
                    return True
            else:
                break
        return streak >= self.required_streak


class SubmissionCountTrigger:
    """
    Awards badge when a student reaches N total submissions.
    Register with key like 'submit_10'.
    """

    def __init__(self, required_count: int):
        self.required_count = required_count

    async def evaluate(
        self,
        student_id: str,
        event: RewardEvent,
        context: TriggerContext,
    ) -> bool:
        if event.event_type != RewardEventType.SUBMISSION:
            return False

        from tasks.submissions.models import TaskSubmission

        count = await TaskSubmission.find(
            TaskSubmission.student_id == student_id,
            TaskSubmission.class_id == context.class_id,
        ).count()

        return count >= self.required_count
