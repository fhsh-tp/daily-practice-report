## MODIFIED Requirements

### Requirement: Permission flags defined as IntFlag with five domains

The system SHALL define a `Permission` Python `IntFlag` class in `src/core/auth/permissions.py` with named flags across five domains: Self (0x001–0x008), Class (0x010–0x020, 0x1000), Task (0x040–0x080), User (0x100–0x200), and System (0x400–0x800). The `MANAGE_CLASS` flag (0x020) MUST be replaced by `MANAGE_OWN_CLASS` (0x020) and `MANAGE_ALL_CLASSES` (0x1000). No other existing flag values SHALL change.

#### Scenario: Permission flags can be combined with bitwise OR

- **WHEN** two or more `Permission` flags are combined using `|`
- **THEN** the result MUST be a valid `Permission` value representing all combined flags

#### Scenario: Permission flag check with bitwise AND

- **WHEN** a user's `permissions` integer is checked against a required flag using `&`
- **THEN** the result MUST be truthy if and only if the user holds that flag

#### Scenario: MANAGE_OWN_CLASS and MANAGE_ALL_CLASSES are distinct flags

- **WHEN** a user holds only `MANAGE_OWN_CLASS`
- **THEN** checking `user.permissions & MANAGE_ALL_CLASSES` MUST be falsy

---

### Requirement: Role presets defined as module-level constants

The system SHALL define Role Preset constants as module-level `Permission` values in `src/core/auth/permissions.py`. The following presets MUST be defined: `STUDENT`, `TEACHER`, `STAFF`, `CLASS_MANAGER`, `USER_ADMIN`, `SYS_ADMIN`, `SITE_ADMIN`. These constants MUST NOT be stored in the database.

#### Scenario: Student preset grants self and read permissions

- **WHEN** a user is assigned the `STUDENT` preset
- **THEN** the user's `permissions` MUST include `READ_OWN_PROFILE`, `WRITE_OWN_PROFILE`, `SUBMIT_TASK`, `CHECKIN`, `READ_CLASS`, and `READ_TASKS`

#### Scenario: Teacher preset grants ownership-scoped class management

- **WHEN** a user is assigned the `TEACHER` preset
- **THEN** the user's `permissions` MUST include all `STUDENT` flags plus `MANAGE_OWN_CLASS`, `MANAGE_TASKS`, and `READ_USERS`

#### Scenario: Staff preset grants same permissions as Teacher

- **WHEN** a user is assigned the `STAFF` preset
- **THEN** the user's `permissions` MUST be identical to the `TEACHER` preset

#### Scenario: ClassManager preset grants global class management

- **WHEN** a user is assigned the `CLASS_MANAGER` preset
- **THEN** the user's `permissions` MUST include all `TEACHER` flags plus `MANAGE_ALL_CLASSES`

#### Scenario: UserAdmin preset grants user management

- **WHEN** a user is assigned the `USER_ADMIN` preset
- **THEN** the user's `permissions` MUST include `READ_OWN_PROFILE`, `WRITE_OWN_PROFILE`, `READ_USERS`, and `MANAGE_USERS`

#### Scenario: SysAdmin preset grants system management

- **WHEN** a user is assigned the `SYS_ADMIN` preset
- **THEN** the user's `permissions` MUST include `READ_OWN_PROFILE`, `WRITE_OWN_PROFILE`, `READ_SYSTEM`, and `WRITE_SYSTEM`

---

### Requirement: Permission presets API endpoint

The system SHALL provide `GET /admin/permissions/presets` returning all named Role Presets as a JSON array. Each element MUST include `name` (string) and `value` (integer). The endpoint MUST require `MANAGE_USERS` permission.

#### Scenario: Presets endpoint returns all presets including new ones

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/permissions/presets`
- **THEN** the system SHALL return HTTP 200 with a JSON array containing at minimum `STUDENT`, `TEACHER`, `STAFF`, `CLASS_MANAGER`, `USER_ADMIN`, `SYS_ADMIN`, and `SITE_ADMIN` entries
