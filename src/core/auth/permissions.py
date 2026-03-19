"""Permission IntFlag and Role Preset constants."""
from enum import IntFlag


class Permission(IntFlag):
    # Self domain
    READ_OWN_PROFILE   = 0x001
    WRITE_OWN_PROFILE  = 0x002
    SUBMIT_TASK        = 0x004
    CHECKIN            = 0x008

    # Class domain
    READ_CLASS         = 0x010
    MANAGE_OWN_CLASS   = 0x020   # manage classes where user is teacher-member
    MANAGE_ALL_CLASSES = 0x1000  # manage any class (classmanager level)

    # Task domain
    READ_TASKS         = 0x040
    MANAGE_TASKS       = 0x080

    # User domain
    READ_USERS         = 0x100
    MANAGE_USERS       = 0x200

    # System domain
    READ_SYSTEM        = 0x400
    WRITE_SYSTEM       = 0x800


# Convenience aliases at module level
READ_OWN_PROFILE   = Permission.READ_OWN_PROFILE
WRITE_OWN_PROFILE  = Permission.WRITE_OWN_PROFILE
SUBMIT_TASK        = Permission.SUBMIT_TASK
CHECKIN            = Permission.CHECKIN
READ_CLASS         = Permission.READ_CLASS
MANAGE_OWN_CLASS   = Permission.MANAGE_OWN_CLASS
MANAGE_ALL_CLASSES = Permission.MANAGE_ALL_CLASSES
READ_TASKS         = Permission.READ_TASKS
MANAGE_TASKS       = Permission.MANAGE_TASKS
READ_USERS         = Permission.READ_USERS
MANAGE_USERS       = Permission.MANAGE_USERS
READ_SYSTEM        = Permission.READ_SYSTEM
WRITE_SYSTEM       = Permission.WRITE_SYSTEM

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
    | Permission.MANAGE_OWN_CLASS
    | Permission.MANAGE_TASKS
    | Permission.READ_USERS
)  # 0x1FF with new flag layout: 0x05F | 0x020 | 0x080 | 0x100 = 0x1FF

STAFF = TEACHER  # Same permissions as TEACHER

CLASS_MANAGER = (
    TEACHER
    | Permission.MANAGE_ALL_CLASSES
)  # TEACHER + global class management

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

# Full site administrator — teacher capabilities + user management + system management
SITE_ADMIN = (
    TEACHER
    | Permission.MANAGE_ALL_CLASSES
    | Permission.MANAGE_USERS
    | Permission.READ_SYSTEM
    | Permission.WRITE_SYSTEM
)

# Domain schema — maps each domain to its read and write flag groups.
# The admin UI reads this to dynamically render the permission matrix.
PERMISSION_SCHEMA: list[dict] = [
    {
        "domain": "Self",
        "read":  Permission.READ_OWN_PROFILE | Permission.SUBMIT_TASK | Permission.CHECKIN,
        "write": Permission.WRITE_OWN_PROFILE,
    },
    {
        "domain": "Class",
        "read":  Permission.READ_CLASS,
        "write": Permission.MANAGE_OWN_CLASS | Permission.MANAGE_ALL_CLASSES,
    },
    {
        "domain": "Task",
        "read":  Permission.READ_TASKS,
        "write": Permission.MANAGE_TASKS,
    },
    {
        "domain": "User",
        "read":  Permission.READ_USERS,
        "write": Permission.MANAGE_USERS,
    },
    {
        "domain": "System",
        "read":  Permission.READ_SYSTEM,
        "write": Permission.WRITE_SYSTEM,
    },
]

# Named presets list — used by the admin UI preset selector.
ROLE_PRESETS: list[dict] = [
    {"name": "STUDENT",       "value": int(STUDENT)},
    {"name": "TEACHER",       "value": int(TEACHER)},
    {"name": "STAFF",         "value": int(STAFF)},
    {"name": "CLASS_MANAGER", "value": int(CLASS_MANAGER)},
    {"name": "USER_ADMIN",    "value": int(USER_ADMIN)},
    {"name": "SYS_ADMIN",     "value": int(SYS_ADMIN)},
    {"name": "SITE_ADMIN",    "value": int(SITE_ADMIN)},
]
