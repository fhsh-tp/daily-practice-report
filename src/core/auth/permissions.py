"""Permission IntFlag and Role Preset constants."""
from enum import IntFlag


class Permission(IntFlag):
    # Self domain
    READ_OWN_PROFILE  = 0x001
    WRITE_OWN_PROFILE = 0x002
    SUBMIT_TASK       = 0x004
    CHECKIN           = 0x008

    # Class domain
    READ_CLASS        = 0x010
    MANAGE_CLASS      = 0x020

    # Task domain
    READ_TASKS        = 0x040
    MANAGE_TASKS      = 0x080

    # User domain
    READ_USERS        = 0x100
    MANAGE_USERS      = 0x200

    # System domain
    READ_SYSTEM       = 0x400
    WRITE_SYSTEM      = 0x800


# Convenience aliases at module level
READ_OWN_PROFILE  = Permission.READ_OWN_PROFILE
WRITE_OWN_PROFILE = Permission.WRITE_OWN_PROFILE
SUBMIT_TASK       = Permission.SUBMIT_TASK
CHECKIN           = Permission.CHECKIN
READ_CLASS        = Permission.READ_CLASS
MANAGE_CLASS      = Permission.MANAGE_CLASS
READ_TASKS        = Permission.READ_TASKS
MANAGE_TASKS      = Permission.MANAGE_TASKS
READ_USERS        = Permission.READ_USERS
MANAGE_USERS      = Permission.MANAGE_USERS
READ_SYSTEM       = Permission.READ_SYSTEM
WRITE_SYSTEM      = Permission.WRITE_SYSTEM

# Role Presets — code constants, not stored in DB
STUDENT = (
    Permission.READ_OWN_PROFILE
    | Permission.WRITE_OWN_PROFILE
    | Permission.SUBMIT_TASK
    | Permission.CHECKIN
    | Permission.READ_CLASS
    | Permission.READ_TASKS
)  # 0x05F

TEACHER = (
    STUDENT
    | Permission.MANAGE_CLASS
    | Permission.MANAGE_TASKS
    | Permission.READ_USERS
)  # 0x0FF

USER_ADMIN = (
    Permission.READ_OWN_PROFILE
    | Permission.WRITE_OWN_PROFILE
    | Permission.READ_USERS
    | Permission.MANAGE_USERS
)  # 0x303

SYS_ADMIN = (
    Permission.READ_OWN_PROFILE
    | Permission.WRITE_OWN_PROFILE
    | Permission.READ_SYSTEM
    | Permission.WRITE_SYSTEM
)  # 0xC03
