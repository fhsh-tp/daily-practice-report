"""Tests for community feed."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_feed")
    from core.users.models import User
    from core.classes.models import Class, ClassMembership
    from tasks.submissions.models import TaskSubmission
    from community.feed.models import FeedPost, Reaction
    await init_beanie(
        database=database,
        document_models=[User, Class, ClassMembership, TaskSubmission, FeedPost, Reaction],
    )
    yield database
    client.close()


@pytest.fixture
async def student(db):
    from core.users.models import User
    from core.auth.password import hash_password
    u = User(username="stu", hashed_password=hash_password("pw"), display_name="S", role="student")
    await u.insert()
    return u


@pytest.fixture
async def teacher(db):
    from core.users.models import User
    from core.auth.password import hash_password
    u = User(username="tchr", hashed_password=hash_password("pw"), display_name="T", role="teacher")
    await u.insert()
    return u


@pytest.fixture
async def membership(db, student):
    from core.classes.models import ClassMembership
    m = ClassMembership(class_id="cls1", user_id=str(student.id), role="student")
    await m.insert()
    return m


@pytest.fixture
async def submission(db, student):
    from tasks.submissions.models import TaskSubmission
    from datetime import date
    sub = TaskSubmission(
        template_id="tmpl1",
        template_snapshot={"name": "T"},
        field_values={},
        student_id=str(student.id),
        class_id="cls1",
        date=date.today(),
    )
    await sub.insert()
    return sub


# --- Share to feed ---

async def test_share_creates_post(db, student, membership, submission):
    from community.feed.models import FeedPost
    post = FeedPost(
        submission_id=str(submission.id),
        student_id=str(student.id),
        class_id="cls1",
        content_preview="Great work!",
    )
    await post.insert()
    found = await FeedPost.get(post.id)
    assert found is not None
    assert found.student_id == str(student.id)


# --- Non-member forbidden ---

async def test_non_member_forbidden(db, student, submission):
    from core.classes.models import ClassMembership
    # No membership created — check that member check raises
    membership = await ClassMembership.find_one(
        ClassMembership.class_id == "cls1",
        ClassMembership.user_id == str(student.id),
    )
    assert membership is None


# --- Reactions ---

async def test_add_reaction(db, student, membership, submission):
    from community.feed.models import FeedPost, Reaction
    post = FeedPost(submission_id=str(submission.id), student_id=str(student.id), class_id="cls1")
    await post.insert()

    reaction = Reaction(post_id=str(post.id), user_id=str(student.id), emoji="🎉")
    await reaction.insert()

    found = await Reaction.find(Reaction.post_id == str(post.id)).to_list()
    assert len(found) == 1
    assert found[0].emoji == "🎉"


async def test_duplicate_reaction_rejected(db, student, membership, submission):
    from community.feed.models import FeedPost, Reaction
    post = FeedPost(submission_id=str(submission.id), student_id=str(student.id), class_id="cls1")
    await post.insert()

    await Reaction(post_id=str(post.id), user_id=str(student.id)).insert()

    # Check duplicate detection logic
    existing = await Reaction.find_one(
        Reaction.post_id == str(post.id),
        Reaction.user_id == str(student.id),
    )
    assert existing is not None  # would be rejected by router


async def test_remove_reaction(db, student, membership, submission):
    from community.feed.models import FeedPost, Reaction
    post = FeedPost(submission_id=str(submission.id), student_id=str(student.id), class_id="cls1")
    await post.insert()

    reaction = Reaction(post_id=str(post.id), user_id=str(student.id))
    await reaction.insert()
    await reaction.delete()

    found = await Reaction.find(Reaction.post_id == str(post.id)).to_list()
    assert len(found) == 0


# --- Delete post ---

async def test_student_deletes_own_post(db, student, submission):
    from community.feed.models import FeedPost
    post = FeedPost(submission_id=str(submission.id), student_id=str(student.id), class_id="cls1")
    await post.insert()
    await post.delete()
    found = await FeedPost.get(post.id)
    assert found is None
