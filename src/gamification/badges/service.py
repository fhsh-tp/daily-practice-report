"""Badge service functions."""
from gamification.badges.models import BadgeAward, BadgeDefinition


async def award_badge(
    badge_id: str,
    student_id: str,
    class_id: str,
    awarded_by: str = "system",
    reason: str | None = None,
) -> BadgeAward | None:
    """Award a badge to a student. Returns None if already held."""
    existing = await BadgeAward.find_one(
        BadgeAward.badge_id == badge_id,
        BadgeAward.student_id == student_id,
    )
    if existing:
        return None  # Badge not awarded if already held

    award = BadgeAward(
        badge_id=badge_id,
        student_id=student_id,
        class_id=class_id,
        awarded_by=awarded_by,
        reason=reason,
    )
    await award.insert()
    return award


async def get_student_badges(student_id: str) -> list[dict]:
    """Return badges earned by a student with definition details."""
    awards = await BadgeAward.find(
        BadgeAward.student_id == student_id,
    ).sort(-BadgeAward.awarded_at).to_list()

    result = []
    for award in awards:
        defn = await BadgeDefinition.get(award.badge_id)
        result.append({
            "award": award,
            "definition": defn,
        })
    return result


async def evaluate_triggers_for_event(student_id: str, event, class_id: str) -> None:
    """Evaluate all BadgeTriggers after a reward event and award matching badges."""
    from extensions.registry import registry
    from extensions.protocols.badge import BadgeTrigger, TriggerContext

    triggers = registry.get_all(BadgeTrigger)
    if not triggers:
        return

    badges = await BadgeDefinition.find(
        BadgeDefinition.class_id == class_id,
        BadgeDefinition.trigger_key != None,  # noqa: E711
    ).to_list()

    for key, trigger in triggers.items():
        matching = [b for b in badges if b.trigger_key == key]
        if not matching:
            continue

        ctx = TriggerContext(class_id=class_id)
        should_award = await trigger.evaluate(student_id, event, ctx)
        if should_award:
            for badge in matching:
                await award_badge(
                    badge_id=str(badge.id),
                    student_id=student_id,
                    class_id=class_id,
                    awarded_by="system",
                )
