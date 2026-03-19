"""Tests for Permission IntFlag and Role Preset constants."""
import pytest


# --- Permission IntFlag ---

def test_permission_flag_check_with_bitwise_and():
    """Permission flag check with bitwise AND must be truthy iff flag is held."""
    from core.auth.permissions import Permission, READ_OWN_PROFILE, SUBMIT_TASK
    user_perms = READ_OWN_PROFILE | SUBMIT_TASK
    assert user_perms & READ_OWN_PROFILE
    assert user_perms & SUBMIT_TASK
    assert not (user_perms & Permission.MANAGE_OWN_CLASS)


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
    assert Permission.READ_OWN_PROFILE    == 0x001
    assert Permission.WRITE_OWN_PROFILE   == 0x002
    assert Permission.SUBMIT_TASK         == 0x004
    assert Permission.CHECKIN             == 0x008
    assert Permission.READ_CLASS          == 0x010
    assert Permission.MANAGE_OWN_CLASS    == 0x020
    assert Permission.READ_TASKS          == 0x040
    assert Permission.MANAGE_TASKS        == 0x080
    assert Permission.READ_USERS          == 0x100
    assert Permission.MANAGE_USERS        == 0x200
    assert Permission.READ_SYSTEM         == 0x400
    assert Permission.WRITE_SYSTEM        == 0x800
    assert Permission.MANAGE_ALL_CLASSES  == 0x1000


def test_manage_own_class_and_manage_all_classes_are_distinct():
    """MANAGE_OWN_CLASS and MANAGE_ALL_CLASSES must be distinct flags."""
    from core.auth.permissions import Permission
    own = Permission.MANAGE_OWN_CLASS
    all_ = Permission.MANAGE_ALL_CLASSES
    assert own != all_
    assert not (own & all_)


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


def test_teacher_preset_grants_ownership_scoped_class_management():
    """Teacher preset must include all STUDENT flags plus MANAGE_OWN_CLASS, MANAGE_TASKS, READ_USERS."""
    from core.auth.permissions import STUDENT, TEACHER, Permission
    assert (TEACHER & STUDENT) == STUDENT
    assert TEACHER & Permission.MANAGE_OWN_CLASS
    assert TEACHER & Permission.MANAGE_TASKS
    assert TEACHER & Permission.READ_USERS
    # Must NOT have global class management
    assert not (TEACHER & Permission.MANAGE_ALL_CLASSES)


def test_staff_preset_same_as_teacher():
    """STAFF preset must have the same permissions as TEACHER."""
    from core.auth.permissions import STAFF, TEACHER
    assert int(STAFF) == int(TEACHER)


def test_class_manager_preset_includes_manage_all_classes():
    """CLASS_MANAGER preset must include MANAGE_ALL_CLASSES."""
    from core.auth.permissions import CLASS_MANAGER, Permission
    assert CLASS_MANAGER & Permission.MANAGE_ALL_CLASSES
    assert CLASS_MANAGER & Permission.MANAGE_OWN_CLASS


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
    from core.auth.permissions import Permission, STUDENT, TEACHER, STAFF, CLASS_MANAGER, USER_ADMIN, SYS_ADMIN
    for preset in (STUDENT, TEACHER, STAFF, CLASS_MANAGER, USER_ADMIN, SYS_ADMIN):
        assert isinstance(preset, Permission)


def test_role_presets_list_contains_all_presets():
    """ROLE_PRESETS must contain STUDENT, TEACHER, STAFF, CLASS_MANAGER, USER_ADMIN, SYS_ADMIN, SITE_ADMIN."""
    from core.auth.permissions import ROLE_PRESETS
    names = {p["name"] for p in ROLE_PRESETS}
    assert {"STUDENT", "TEACHER", "STAFF", "CLASS_MANAGER", "USER_ADMIN", "SYS_ADMIN", "SITE_ADMIN"}.issubset(names)


# --- PERMISSION_SCHEMA ---

def test_permission_schema_has_expected_domains():
    """PERMISSION_SCHEMA must contain the expected domain entries."""
    from core.auth.permissions import PERMISSION_SCHEMA
    domains = {entry["domain"] for entry in PERMISSION_SCHEMA}
    assert domains == {"Self", "Class", "ClassManager", "Task", "User", "System"}


def test_permission_schema_entries_have_required_keys():
    """Each PERMISSION_SCHEMA entry must have domain, read, write keys."""
    from core.auth.permissions import PERMISSION_SCHEMA
    for entry in PERMISSION_SCHEMA:
        assert "domain" in entry
        assert "read" in entry
        assert "write" in entry


def test_permission_schema_read_write_are_permissions():
    """PERMISSION_SCHEMA read/write values must be Permission instances."""
    from core.auth.permissions import PERMISSION_SCHEMA, Permission
    for entry in PERMISSION_SCHEMA:
        assert isinstance(entry["read"], Permission)
        assert isinstance(entry["write"], Permission)


def test_permission_schema_class_domains_split():
    """Class domain has MANAGE_OWN_CLASS; ClassManager domain has MANAGE_ALL_CLASSES."""
    from core.auth.permissions import PERMISSION_SCHEMA, Permission
    class_entry = next(e for e in PERMISSION_SCHEMA if e["domain"] == "Class")
    cm_entry = next(e for e in PERMISSION_SCHEMA if e["domain"] == "ClassManager")
    assert class_entry["write"] & Permission.MANAGE_OWN_CLASS
    assert not (class_entry["write"] & Permission.MANAGE_ALL_CLASSES)
    assert cm_entry["write"] & Permission.MANAGE_ALL_CLASSES
