# user-auth Specification

## Purpose

TBD - created by archiving change 'daily-training-submission-system'. Update Purpose after archive.

## Requirements

### Requirement: User registration by teacher

Users with `MANAGE_USERS` permission SHALL be able to create new accounts. Each account MUST include a unique username, hashed password, display name, permissions (as an integer from a Role Preset), and an optional `tags` list. The `role` field is removed.

#### Scenario: User admin creates student account

- **WHEN** a user with `MANAGE_USERS` permission submits a valid username, password, display name, and permissions value
- **THEN** the system SHALL create the account with the given permissions and return the new user ID

#### Scenario: Duplicate username rejected

- **WHEN** a user submits a username that already exists
- **THEN** the system SHALL return an error and SHALL NOT create a duplicate account


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
### Requirement: User model stores permissions as integer and supports tags

The `User` Beanie Document MUST store `permissions: int` instead of `role: str`. The document MUST also include `tags: list[str]` defaulting to an empty list. Both fields MUST be included in all user response schemas.

#### Scenario: User created with permissions preset

- **WHEN** a new user is created with a Role Preset value
- **THEN** the stored `permissions` field MUST equal the integer value of that preset

#### Scenario: User tags are updatable

- **WHEN** a user with `MANAGE_USERS` permission updates another user's tags
- **THEN** the `tags` field MUST be replaced with the new list


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
### Requirement: Migration maps existing role field to permissions integer

The system SHALL provide a migration script that converts existing `User` documents from `role: "student"` to `permissions = STUDENT` and `role: "teacher"` to `permissions = TEACHER`. The `role` field MUST be removed after migration.

#### Scenario: Student role migrated to permissions

- **WHEN** the migration script runs on a user with `role = "student"`
- **THEN** the user's document MUST have `permissions` set to the `STUDENT` preset integer and `role` field removed

#### Scenario: Teacher role migrated to permissions

- **WHEN** the migration script runs on a user with `role = "teacher"`
- **THEN** the user's document MUST have `permissions` set to the `TEACHER` preset integer and `role` field removed


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
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
### Requirement: User login with credentials

The system SHALL authenticate users via username and password. On success, a signed JWT SHALL be issued and stored in an HttpOnly cookie. The API endpoint (`POST /auth/login`) SHALL accept JSON and return JSON. The form endpoint (`POST /pages/login`) SHALL accept form data and redirect.

#### Scenario: Successful API login

- **WHEN** a client submits valid credentials to `POST /auth/login` with JSON body
- **THEN** the system SHALL set an HttpOnly cookie containing a signed JWT and return JSON with permissions

#### Scenario: Successful form login

- **WHEN** a user submits valid credentials via `POST /pages/login` with form data
- **THEN** the system SHALL set an HttpOnly JWT cookie and redirect to `GET /pages/dashboard` (HTTP 302)

#### Scenario: Invalid credentials rejected via API

- **WHEN** a client submits an incorrect password or unknown username to `POST /auth/login`
- **THEN** the system SHALL return HTTP 401 and SHALL NOT set a session cookie

#### Scenario: Invalid credentials rejected via form

- **WHEN** a user submits incorrect credentials via `POST /pages/login`
- **THEN** the system SHALL redirect to `GET /pages/login?error=帳號或密碼錯誤` (HTTP 302) and SHALL NOT set a session cookie


<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: JWT-based session management

The system SHALL validate the JWT on every protected request. Tokens MUST include expiry (exp), user ID, and role claims. Expired tokens MUST be rejected.

#### Scenario: Expired token rejected

- **WHEN** a request arrives with an expired JWT cookie
- **THEN** the system SHALL redirect the user to the login page

#### Scenario: Valid token accepted

- **WHEN** a request arrives with a valid, non-expired JWT cookie
- **THEN** the system SHALL allow the request and provide the authenticated user context


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Role-based access control

The system SHALL enforce role-based access. Pages and endpoints designated for teachers MUST reject requests from students, and vice versa.

#### Scenario: Student accesses teacher-only endpoint

- **WHEN** a student sends a request to a teacher-only endpoint
- **THEN** the system SHALL return a 403 response


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: AuthProvider extension point

The system SHALL define an `AuthProvider` Protocol with method `authenticate(credentials) -> User`. The local (username/password) implementation SHALL be registered by default. Additional providers (e.g., Google OAuth) MUST be registerable without modifying core auth code.

#### Scenario: Default local provider authenticates

- **WHEN** the app starts with no additional providers configured
- **THEN** the LocalAuthProvider SHALL handle all authentication requests

#### Scenario: Additional provider registered

- **WHEN** a new AuthProvider implementation is registered in the ExtensionRegistry at startup
- **THEN** the auth router SHALL delegate to that provider when the corresponding login method is selected


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Password change

Users SHALL be able to change their own password. The current password MUST be verified before accepting a new one.

#### Scenario: Successful password change

- **WHEN** a user submits their current password and a valid new password
- **THEN** the system SHALL update the stored hash and invalidate existing sessions

#### Scenario: Wrong current password

- **WHEN** a user submits an incorrect current password
- **THEN** the system SHALL return an error and SHALL NOT update the password

<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Browser-based form login endpoint

The system SHALL accept `POST /pages/login` with `application/x-www-form-urlencoded` body containing `username` and `password`. On success, it SHALL set the JWT cookie and redirect to `GET /pages/dashboard`. On failure, it SHALL redirect to `GET /pages/login?error=<message>`.

#### Scenario: Successful form login

- **WHEN** a user submits valid credentials via the HTML login form at `POST /pages/login`
- **THEN** the system SHALL set an HttpOnly JWT cookie and redirect to `GET /pages/dashboard` (HTTP 302)

#### Scenario: Invalid credentials via form

- **WHEN** a user submits invalid credentials via the HTML login form
- **THEN** the system SHALL redirect to `GET /pages/login?error=帳號或密碼錯誤` (HTTP 302)
- **AND** the JWT cookie SHALL NOT be set

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->


<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: Browser-based logout redirects to login

The system SHALL accept `POST /auth/logout` and redirect to `GET /pages/login` after clearing the session cookie.

#### Scenario: Successful logout

- **WHEN** a user submits the logout form via `POST /auth/logout`
- **THEN** the system SHALL clear the JWT cookie and redirect to `GET /pages/login` (HTTP 302)

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->