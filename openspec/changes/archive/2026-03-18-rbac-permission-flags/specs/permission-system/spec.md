## ADDED Requirements

### Requirement: Permission flags defined as IntFlag with five domains

The system SHALL define a `Permission` Python `IntFlag` class in `src/core/auth/permissions.py` with 12 named flags across five domains: Self (0x001–0x008), Class (0x010–0x020), Task (0x040–0x080), User (0x100–0x200), and System (0x400–0x800).

#### Scenario: Permission flags can be combined with bitwise OR

- **WHEN** two or more `Permission` flags are combined using `|`
- **THEN** the result MUST be a valid `Permission` value representing all combined flags

#### Scenario: Permission flag check with bitwise AND

- **WHEN** a user's `permissions` integer is checked against a required flag using `&`
- **THEN** the result MUST be truthy if and only if the user holds that flag

### Requirement: Role presets defined as module-level constants

The system SHALL define four Role Preset constants (`STUDENT`, `TEACHER`, `USER_ADMIN`, `SYS_ADMIN`) as module-level `Permission` values in `src/core/auth/permissions.py`. These constants MUST NOT be stored in the database.

#### Scenario: Student preset grants self and read permissions

- **WHEN** a user is assigned the `STUDENT` preset
- **THEN** the user's `permissions` MUST include `READ_OWN_PROFILE`, `WRITE_OWN_PROFILE`, `SUBMIT_TASK`, `CHECKIN`, `READ_CLASS`, and `READ_TASKS`

#### Scenario: Teacher preset extends student preset

- **WHEN** a user is assigned the `TEACHER` preset
- **THEN** the user's `permissions` MUST include all `STUDENT` flags plus `MANAGE_CLASS`, `MANAGE_TASKS`, and `READ_USERS`

#### Scenario: UserAdmin preset grants user management

- **WHEN** a user is assigned the `USER_ADMIN` preset
- **THEN** the user's `permissions` MUST include `READ_OWN_PROFILE`, `WRITE_OWN_PROFILE`, `READ_USERS`, and `MANAGE_USERS`

#### Scenario: SysAdmin preset grants system management

- **WHEN** a user is assigned the `SYS_ADMIN` preset
- **THEN** the user's `permissions` MUST include `READ_OWN_PROFILE`, `WRITE_OWN_PROFILE`, `READ_SYSTEM`, and `WRITE_SYSTEM`

### Requirement: Route guard enforces required permission flag

The system SHALL provide a `require_permission(flag: Permission)` FastAPI dependency factory in `src/core/auth/guards.py`. A route using this dependency MUST reject requests from users who do not hold the required flag with HTTP 403.

#### Scenario: Authorized request passes guard

- **WHEN** an authenticated user with the required permission flag sends a request to a guarded route
- **THEN** the request MUST proceed normally

#### Scenario: Unauthorized request blocked by guard

- **WHEN** an authenticated user without the required permission flag sends a request to a guarded route
- **THEN** the system MUST return HTTP 403 Forbidden
