"""Tests for Permission IntFlag and Role Preset constants."""
import pytest


# --- Permission IntFlag ---

def test_permission_flag_check_with_bitwise_and():
    """Permission flag check with bitwise AND must be truthy iff flag is held."""
    from core.auth.permissions import Permission, READ_OWN_PROFILE, SUBMIT_TASK
    user_perms = READ_OWN_PROFILE | SUBMIT_TASK
    assert user_perms & READ_OWN_PROFILE
    assert user_perms & SUBMIT_TASK
    assert not (user_perms & Permission.MANAGE_CLASS)


def test_permission_flags_combine_with_bitwise_or():
    """Flags combined with | must produce a valid Permission value."""
    from core.auth.permissions import Permission, READ_OWN_PROFILE, WRITE_OWN_PROFILE
    combined = READ_OWN_PROFILE | WRITE_OWN_PROFILE
    assert isinstance(combined, Permission)
    assert combined & READ_OWN_PROFILE
    assert combined & WRITE_OWN_PROFILE


def test_permission_flag_values_match_spec():
    """Each flag must have the exact hex value from the spec."""
    from core.auth.permissions import Permission
    assert Permission.READ_OWN_PROFILE  == 0x001
    assert Permission.WRITE_OWN_PROFILE == 0x002
    assert Permission.SUBMIT_TASK       == 0x004
    assert Permission.CHECKIN           == 0x008
    assert Permission.READ_CLASS        == 0x010
    assert Permission.MANAGE_CLASS      == 0x020
    assert Permission.READ_TASKS        == 0x040
    assert Permission.MANAGE_TASKS      == 0x080
    assert Permission.READ_USERS        == 0x100
    assert Permission.MANAGE_USERS      == 0x200
    assert Permission.READ_SYSTEM       == 0x400
    assert Permission.WRITE_SYSTEM      == 0x800


# --- Role Presets ---

def test_student_preset_grants_self_and_read_permissions():
    """Student preset must include READ/WRITE_OWN_PROFILE, SUBMIT_TASK, CHECKIN, READ_CLASS, READ_TASKS."""
    from core.auth.permissions import STUDENT, Permission
    assert STUDENT & Permission.READ_OWN_PROFILE
    assert STUDENT & Permission.WRITE_OWN_PROFILE
    assert STUDENT & Permission.SUBMIT_TASK
    assert STUDENT & Permission.CHECKIN
    assert STUDENT & Permission.READ_CLASS
    assert STUDENT & Permission.READ_TASKS


def test_teacher_preset_extends_student():
    """Teacher preset must include all STUDENT flags plus MANAGE_CLASS, MANAGE_TASKS, READ_USERS."""
    from core.auth.permissions import STUDENT, TEACHER, Permission
    # All student flags included
    assert (TEACHER & STUDENT) == STUDENT
    # Teacher-only flags
    assert TEACHER & Permission.MANAGE_CLASS
    assert TEACHER & Permission.MANAGE_TASKS
    assert TEACHER & Permission.READ_USERS


def test_user_admin_preset_grants_user_management():
    """USER_ADMIN must include READ/WRITE_OWN_PROFILE, READ_USERS, MANAGE_USERS."""
    from core.auth.permissions import USER_ADMIN, Permission
    assert USER_ADMIN & Permission.READ_OWN_PROFILE
    assert USER_ADMIN & Permission.WRITE_OWN_PROFILE
    assert USER_ADMIN & Permission.READ_USERS
    assert USER_ADMIN & Permission.MANAGE_USERS


def test_sys_admin_preset_grants_system_management():
    """SYS_ADMIN must include READ/WRITE_OWN_PROFILE, READ_SYSTEM, WRITE_SYSTEM."""
    from core.auth.permissions import SYS_ADMIN, Permission
    assert SYS_ADMIN & Permission.READ_OWN_PROFILE
    assert SYS_ADMIN & Permission.WRITE_OWN_PROFILE
    assert SYS_ADMIN & Permission.READ_SYSTEM
    assert SYS_ADMIN & Permission.WRITE_SYSTEM


def test_presets_are_permission_instances():
    """All presets must be Permission instances (not plain int)."""
    from core.auth.permissions import Permission, STUDENT, TEACHER, USER_ADMIN, SYS_ADMIN
    for preset in (STUDENT, TEACHER, USER_ADMIN, SYS_ADMIN):
        assert isinstance(preset, Permission)
