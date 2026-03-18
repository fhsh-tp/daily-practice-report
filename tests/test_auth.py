"""Tests for the user-auth capability."""
import pytest
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie


@pytest.fixture
async def db():
    client = AsyncMongoMockClient()
    database = client.get_database("test_auth")
    from core.users.models import User
    await init_beanie(database=database, document_models=[User])
    yield database
    client.close()


# --- User model ---

async def test_user_model_has_required_fields(db):
    from core.users.models import User
    u = User(
        username="alice",
        hashed_password="hashed",
        display_name="Alice",
        role="student",
    )
    assert u.username == "alice"
    assert u.role == "student"
    assert u.created_at is not None


async def test_user_role_must_be_valid(db):
    from core.users.models import User
    import pydantic
    with pytest.raises((pydantic.ValidationError, ValueError)):
        User(username="x", hashed_password="h", display_name="X", role="admin")


# --- LocalAuthProvider ---

async def test_local_auth_provider_authenticates_valid_user(db):
    from core.users.models import User
    from core.auth.local_provider import LocalAuthProvider
    from core.auth.password import hash_password

    user = User(
        username="bob",
        hashed_password=hash_password("secret123"),
        display_name="Bob",
        role="student",
    )
    await user.insert()

    provider = LocalAuthProvider()
    result = await provider.authenticate({"username": "bob", "password": "secret123"})
    assert result is not None
    assert result.username == "bob"


async def test_local_auth_provider_rejects_wrong_password(db):
    from core.users.models import User
    from core.auth.local_provider import LocalAuthProvider
    from core.auth.password import hash_password

    user = User(
        username="carol",
        hashed_password=hash_password("correct"),
        display_name="Carol",
        role="student",
    )
    await user.insert()

    provider = LocalAuthProvider()
    with pytest.raises(ValueError):
        await provider.authenticate({"username": "carol", "password": "wrong"})


async def test_local_auth_provider_rejects_unknown_user(db):
    from core.auth.local_provider import LocalAuthProvider

    provider = LocalAuthProvider()
    with pytest.raises(ValueError):
        await provider.authenticate({"username": "nobody", "password": "x"})


# --- JWT token ---

def test_create_token_contains_claims():
    from core.auth.jwt import create_access_token, decode_access_token
    token = create_access_token(user_id="user123", role="teacher")
    payload = decode_access_token(token)
    assert payload["user_id"] == "user123"
    assert payload["role"] == "teacher"
    assert "exp" in payload


def test_expired_token_raises():
    import time
    from core.auth.jwt import create_access_token, decode_access_token
    token = create_access_token(user_id="x", role="student", expires_seconds=-1)
    with pytest.raises(Exception):  # jwt.ExpiredSignatureError
        decode_access_token(token)


def test_tampered_token_raises():
    from core.auth.jwt import create_access_token, decode_access_token
    token = create_access_token(user_id="x", role="student")
    tampered = token + "tampered"
    with pytest.raises(Exception):
        decode_access_token(tampered)


# --- Password hashing ---

def test_password_hashing_is_not_plaintext():
    from core.auth.password import hash_password
    h = hash_password("mypassword")
    assert h != "mypassword"
    assert len(h) > 20


def test_password_verify_correct():
    from core.auth.password import hash_password, verify_password
    h = hash_password("mypassword")
    assert verify_password("mypassword", h) is True


def test_password_verify_wrong():
    from core.auth.password import hash_password, verify_password
    h = hash_password("mypassword")
    assert verify_password("wrongpassword", h) is False


# --- Role-based access control ---

async def test_require_teacher_allows_teacher(db):
    from core.auth.deps import require_teacher
    from core.users.models import User
    from core.auth.password import hash_password

    teacher = User(
        username="teach1",
        hashed_password=hash_password("pw"),
        display_name="Teacher",
        role="teacher",
    )
    await teacher.insert()

    # Simulate the dependency by calling it directly
    dep = require_teacher()
    result = await dep(current_user=teacher)
    assert result.role == "teacher"


async def test_require_teacher_rejects_student(db):
    from core.auth.deps import require_teacher
    from core.users.models import User
    from core.auth.password import hash_password
    from fastapi import HTTPException

    student = User(
        username="stu1",
        hashed_password=hash_password("pw"),
        display_name="Student",
        role="student",
    )

    dep = require_teacher()
    with pytest.raises(HTTPException) as exc_info:
        await dep(current_user=student)
    assert exc_info.value.status_code == 403
