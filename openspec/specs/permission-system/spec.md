# permission-system Specification

## Purpose

Defines the permission system using Python IntFlag for fine-grained access control, replacing the previous role-based string approach. Permissions are stored as integers on the User document and checked via bitwise operations.

## Requirements

### Requirement: Permission flags defined as IntFlag with five domains

The system SHALL define a `Permission` Python `IntFlag` class in `src/core/auth/permissions.py` with 12 named flags across five domains: Self (0x001–0x008), Class (0x010–0x020), Task (0x040–0x080), User (0x100–0x200), and System (0x400–0x800).

#### Scenario: Permission flags can be combined with bitwise OR

- **WHEN** two or more `Permission` flags are combined using `|`
- **THEN** the result MUST be a valid `Permission` value representing all combined flags

#### Scenario: Permission flag check with bitwise AND

- **WHEN** a user's `permissions` integer is checked against a required flag using `&`
- **THEN** the result MUST be truthy if and only if the user holds that flag


<!-- @trace
source: rbac-permission-flags
updated: 2026-03-18
code:
  - docker-compose.yml
  - src/core/auth/guards.py
  - src/tasks/templates/router.py
  - src/tasks/checkin/router.py
  - src/core/system/router.py
  - scripts/migrations/role_to_permissions.py
  - src/gamification/prizes/router.py
  - src/core/system/__init__.py
  - src/core/classes/service.py
  - src/gamification/leaderboard/router.py
  - src/core/system/models.py
  - src/tasks/submissions/router.py
  - pyproject.toml
  - src/core/system/startup.py
  - src/community/feed/router.py
  - src/core/auth/jwt.py
  - src/core/auth/deps.py
  - src/core/auth/router.py
  - src/shared/redis.py
  - src/shared/__init__.py
  - tests/auth/__init__.py
  - src/core/classes/router.py
  - src/templates/setup.html
  - src/gamification/badges/router.py
  - src/core/auth/permissions.py
  - src/main.py
  - src/core/users/router.py
  - src/gamification/points/router.py
  - uv.lock
  - src/core/users/models.py
tests:
  - tests/auth/test_role_migration.py
  - tests/test_redis_shared.py
  - tests/auth/test_deps.py
  - tests/auth/test_permissions.py
  - tests/auth/test_user_model.py
  - tests/test_setup_wizard.py
  - tests/auth/test_guards.py
  - tests/test_classes.py
  - tests/test_setup_startup.py
  - tests/test_system_config.py
  - tests/test_auth.py
  - tests/auth/test_user_router.py
-->

---
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


<!-- @trace
source: rbac-permission-flags
updated: 2026-03-18
code:
  - docker-compose.yml
  - src/core/auth/guards.py
  - src/tasks/templates/router.py
  - src/tasks/checkin/router.py
  - src/core/system/router.py
  - scripts/migrations/role_to_permissions.py
  - src/gamification/prizes/router.py
  - src/core/system/__init__.py
  - src/core/classes/service.py
  - src/gamification/leaderboard/router.py
  - src/core/system/models.py
  - src/tasks/submissions/router.py
  - pyproject.toml
  - src/core/system/startup.py
  - src/community/feed/router.py
  - src/core/auth/jwt.py
  - src/core/auth/deps.py
  - src/core/auth/router.py
  - src/shared/redis.py
  - src/shared/__init__.py
  - tests/auth/__init__.py
  - src/core/classes/router.py
  - src/templates/setup.html
  - src/gamification/badges/router.py
  - src/core/auth/permissions.py
  - src/main.py
  - src/core/users/router.py
  - src/gamification/points/router.py
  - uv.lock
  - src/core/users/models.py
tests:
  - tests/auth/test_role_migration.py
  - tests/test_redis_shared.py
  - tests/auth/test_deps.py
  - tests/auth/test_permissions.py
  - tests/auth/test_user_model.py
  - tests/test_setup_wizard.py
  - tests/auth/test_guards.py
  - tests/test_classes.py
  - tests/test_setup_startup.py
  - tests/test_system_config.py
  - tests/test_auth.py
  - tests/auth/test_user_router.py
-->

---
### Requirement: Route guard enforces required permission flag

The system SHALL provide a `require_permission(flag: Permission)` FastAPI dependency factory in `src/core/auth/guards.py`. A route using this dependency MUST reject requests from users who do not hold the required flag with HTTP 403.

#### Scenario: Authorized request passes guard

- **WHEN** an authenticated user with the required permission flag sends a request to a guarded route
- **THEN** the request MUST proceed normally

#### Scenario: Unauthorized request blocked by guard

- **WHEN** an authenticated user without the required permission flag sends a request to a guarded route
- **THEN** the system MUST return HTTP 403 Forbidden

<!-- @trace
source: rbac-permission-flags
updated: 2026-03-18
-->

<!-- @trace
source: rbac-permission-flags
updated: 2026-03-18
code:
  - docker-compose.yml
  - src/core/auth/guards.py
  - src/tasks/templates/router.py
  - src/tasks/checkin/router.py
  - src/core/system/router.py
  - scripts/migrations/role_to_permissions.py
  - src/gamification/prizes/router.py
  - src/core/system/__init__.py
  - src/core/classes/service.py
  - src/gamification/leaderboard/router.py
  - src/core/system/models.py
  - src/tasks/submissions/router.py
  - pyproject.toml
  - src/core/system/startup.py
  - src/community/feed/router.py
  - src/core/auth/jwt.py
  - src/core/auth/deps.py
  - src/core/auth/router.py
  - src/shared/redis.py
  - src/shared/__init__.py
  - tests/auth/__init__.py
  - src/core/classes/router.py
  - src/templates/setup.html
  - src/gamification/badges/router.py
  - src/core/auth/permissions.py
  - src/main.py
  - src/core/users/router.py
  - src/gamification/points/router.py
  - uv.lock
  - src/core/users/models.py
tests:
  - tests/auth/test_role_migration.py
  - tests/test_redis_shared.py
  - tests/auth/test_deps.py
  - tests/auth/test_permissions.py
  - tests/auth/test_user_model.py
  - tests/test_setup_wizard.py
  - tests/auth/test_guards.py
  - tests/test_classes.py
  - tests/test_setup_startup.py
  - tests/test_system_config.py
  - tests/test_auth.py
  - tests/auth/test_user_router.py
-->
---
### Requirement: PERMISSION_SCHEMA defines domain-to-flag mapping

The system SHALL define a module-level constant `PERMISSION_SCHEMA` in `src/core/auth/permissions.py` as a list of dicts, each with keys `domain` (str), `read` (Permission), and `write` (Permission). This structure MUST cover all five domains: Self, Class, Task, User, and System. When a developer adds a new `Permission` flag, they MUST add it to `PERMISSION_SCHEMA` to make it visible in the admin UI.

#### Scenario: PERMISSION_SCHEMA covers all existing domains

- **WHEN** `PERMISSION_SCHEMA` is imported from `permissions.py`
- **THEN** it MUST contain exactly one entry per domain: Self, Class, Task, User, System

#### Scenario: New flag added to schema appears in API response

- **WHEN** a developer adds a new `Permission` flag and includes it in `PERMISSION_SCHEMA`
- **THEN** `GET /admin/permissions/schema` MUST return the updated domain entry including the new flag value


<!-- @trace
source: admin-management-panel
updated: 2026-03-19
code:
  - src/templates/admin/index.html
  - src/templates/admin/layout.html
  - src/core/users/router.py
  - src/templates/admin/system_settings.html
  - src/templates/shared/base.html
  - src/templates/admin/users_list.html
  - src/core/system/router.py
  - src/core/auth/permissions.py
  - src/templates/admin/user_form.html
  - src/pages/router.py
tests:
  - tests/test_admin_permissions.py
  - tests/test_admin_system.py
  - tests/test_admin_users.py
  - tests/auth/test_permissions.py
  - tests/test_admin_pages.py
-->

---
### Requirement: Permission schema API endpoint

The system SHALL provide `GET /admin/permissions/schema` returning the serialized `PERMISSION_SCHEMA` as a JSON array. Each element MUST include `domain` (string), `read` (integer bitmask), and `write` (integer bitmask). The endpoint MUST require `MANAGE_USERS` permission.

#### Scenario: Schema endpoint returns domain list

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/permissions/schema`
- **THEN** the system SHALL return HTTP 200 with a JSON array where each object has `domain`, `read`, and `write` integer fields


<!-- @trace
source: admin-management-panel
updated: 2026-03-19
code:
  - src/templates/admin/index.html
  - src/templates/admin/layout.html
  - src/core/users/router.py
  - src/templates/admin/system_settings.html
  - src/templates/shared/base.html
  - src/templates/admin/users_list.html
  - src/core/system/router.py
  - src/core/auth/permissions.py
  - src/templates/admin/user_form.html
  - src/pages/router.py
tests:
  - tests/test_admin_permissions.py
  - tests/test_admin_system.py
  - tests/test_admin_users.py
  - tests/auth/test_permissions.py
  - tests/test_admin_pages.py
-->

---
### Requirement: Permission presets API endpoint

The system SHALL provide `GET /admin/permissions/presets` returning all named Role Presets as a JSON array. Each element MUST include `name` (string, e.g. `"STUDENT"`) and `value` (integer). The endpoint MUST require `MANAGE_USERS` permission.

#### Scenario: Presets endpoint returns all presets

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/permissions/presets`
- **THEN** the system SHALL return HTTP 200 with a JSON array containing at minimum `STUDENT`, `TEACHER`, `USER_ADMIN`, `SYS_ADMIN`, and `SITE_ADMIN` entries

<!-- @trace
source: admin-management-panel
updated: 2026-03-19
code:
  - src/templates/admin/index.html
  - src/templates/admin/layout.html
  - src/core/users/router.py
  - src/templates/admin/system_settings.html
  - src/templates/shared/base.html
  - src/templates/admin/users_list.html
  - src/core/system/router.py
  - src/core/auth/permissions.py
  - src/templates/admin/user_form.html
  - src/pages/router.py
tests:
  - tests/test_admin_permissions.py
  - tests/test_admin_system.py
  - tests/test_admin_users.py
  - tests/auth/test_permissions.py
  - tests/test_admin_pages.py
-->