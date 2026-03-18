"""Class management service functions."""
import secrets

from core.classes.models import Class, ClassMembership
from core.users.models import User


def _new_invite_code() -> str:
    """Generate a URL-safe 8-character invite code."""
    return secrets.token_urlsafe(6).upper()[:8]


async def create_class(
    name: str,
    description: str,
    visibility: str,
    owner: User,
) -> Class:
    """Create a new class and assign the owner membership."""
    cls = Class(
        name=name,
        description=description,
        visibility=visibility,
        owner_id=str(owner.id),
        invite_code=_new_invite_code(),
    )
    await cls.insert()

    # Owner also gets a membership record as teacher
    membership = ClassMembership(
        class_id=str(cls.id),
        user_id=str(owner.id),
        role="teacher",
    )
    await membership.insert()
    return cls


async def join_class_by_code(user: User, invite_code: str) -> ClassMembership:
    """
    Add a user to a class using an invite code.
    Returns existing membership if already a member (idempotent).
    Raises ValueError if the code is invalid.
    """
    cls = await Class.find_one(Class.invite_code == invite_code)
    if cls is None:
        raise ValueError(f"Invalid invite code: {invite_code!r}")

    existing = await ClassMembership.find_one(
        ClassMembership.class_id == str(cls.id),
        ClassMembership.user_id == str(user.id),
    )
    if existing:
        return existing

    membership = ClassMembership(
        class_id=str(cls.id),
        user_id=str(user.id),
        role=user.role,
    )
    await membership.insert()
    return membership


async def join_class_by_id(user: User, class_id: str) -> ClassMembership:
    """Add a user to a public class by class ID."""
    cls = await Class.get(class_id)
    if cls is None or cls.visibility != "public":
        raise ValueError("Class not found or not public")

    existing = await ClassMembership.find_one(
        ClassMembership.class_id == class_id,
        ClassMembership.user_id == str(user.id),
    )
    if existing:
        return existing

    membership = ClassMembership(
        class_id=class_id,
        user_id=str(user.id),
        role=user.role,
    )
    await membership.insert()
    return membership


async def get_public_classes() -> list[Class]:
    """Return all public classes."""
    return await Class.find(Class.visibility == "public").to_list()


async def get_class_members(class_id: str) -> list[ClassMembership]:
    """Return all memberships for a class."""
    return await ClassMembership.find(ClassMembership.class_id == class_id).to_list()


async def remove_member(class_id: str, user_id: str) -> None:
    """Remove a user from a class."""
    membership = await ClassMembership.find_one(
        ClassMembership.class_id == class_id,
        ClassMembership.user_id == user_id,
    )
    if membership:
        await membership.delete()


async def promote_to_teacher(class_id: str, user_id: str) -> ClassMembership:
    """Promote a student membership to teacher role."""
    membership = await ClassMembership.find_one(
        ClassMembership.class_id == class_id,
        ClassMembership.user_id == user_id,
    )
    if membership is None:
        raise ValueError("User is not a member of this class")
    membership.role = "teacher"
    await membership.save()
    return membership


async def regenerate_invite_code(class_id: str) -> str:
    """
    Generate a new invite code for a class.
    The old code becomes invalid immediately.
    Returns the new code.
    """
    cls = await Class.get(class_id)
    if cls is None:
        raise ValueError("Class not found")
    cls.invite_code = _new_invite_code()
    await cls.save()
    return cls.invite_code


async def set_visibility(class_id: str, visibility: str) -> Class:
    """Update class visibility (public/private)."""
    cls = await Class.get(class_id)
    if cls is None:
        raise ValueError("Class not found")
    cls.visibility = visibility
    await cls.save()
    return cls
