# identity-tags Specification

## Purpose

Defines the IdentityTag system for classifying users by their role identity (student, teacher, staff). Identity tags are stored on the User document and used for visibility and filtering decisions, but do not directly affect permission checks.

## Requirements

### Requirement: IdentityTag enum defines three identity values

The system SHALL define an `IdentityTag` Python `str` Enum in `src/core/users/models.py` with three values: `TEACHER`, `STUDENT`, and `STAFF`. This enum SHALL be used exclusively for identity classification and MUST NOT affect permission checks directly.

#### Scenario: IdentityTag values are fixed strings

- **WHEN** `IdentityTag` is imported from `src/core/users/models.py`
- **THEN** it MUST contain exactly the values `"teacher"`, `"student"`, and `"staff"`


<!-- @trace
source: permission-identity-refactor
updated: 2026-03-19
code:
  - src/core/classes/router.py
  - src/core/users/schemas.py
  - src/core/classes/service.py
  - src/core/users/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/pages/router.py
  - src/core/auth/router.py
  - src/tasks/checkin/router.py
  - src/tasks/templates/router.py
  - src/core/classes/models.py
  - src/templates/admin/classes_list.html
  - scripts/migrations/20260319_003_init_identity_tags.py
  - src/community/feed/router.py
  - src/core/users/models.py
  - src/gamification/leaderboard/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/templates/admin/users_list.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_assign.html
  - src/templates/teacher/template_form.html
  - scripts/migrations/20260319_002_manage_class_rename.py
  - src/core/auth/permissions.py
tests:
  - tests/test_class_permissions.py
  - tests/test_admin_permissions.py
  - tests/test_identity_tags.py
  - tests/test_auth.py
  - tests/auth/test_user_model.py
  - tests/test_user_visibility.py
  - tests/auth/test_guards.py
  - tests/auth/test_permissions.py
-->

---
### Requirement: User model stores identity_tags as a list

The `User` document SHALL include an `identity_tags: list[IdentityTag]` field with a default of an empty list. A user MAY hold multiple identity tags simultaneously (e.g., a teacher who also holds a staff role). The field MUST be stored in MongoDB as an array of strings.

#### Scenario: New user created without identity tags

- **WHEN** a new user is created without specifying `identity_tags`
- **THEN** the user's `identity_tags` field MUST default to an empty list

#### Scenario: User holds multiple identity tags

- **WHEN** a user is assigned both `TEACHER` and `STAFF` identity tags
- **THEN** both values SHALL appear in `identity_tags` and both MUST be returned in API responses


<!-- @trace
source: permission-identity-refactor
updated: 2026-03-19
code:
  - src/core/classes/router.py
  - src/core/users/schemas.py
  - src/core/classes/service.py
  - src/core/users/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/pages/router.py
  - src/core/auth/router.py
  - src/tasks/checkin/router.py
  - src/tasks/templates/router.py
  - src/core/classes/models.py
  - src/templates/admin/classes_list.html
  - scripts/migrations/20260319_003_init_identity_tags.py
  - src/community/feed/router.py
  - src/core/users/models.py
  - src/gamification/leaderboard/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/templates/admin/users_list.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_assign.html
  - src/templates/teacher/template_form.html
  - scripts/migrations/20260319_002_manage_class_rename.py
  - src/core/auth/permissions.py
tests:
  - tests/test_class_permissions.py
  - tests/test_admin_permissions.py
  - tests/test_identity_tags.py
  - tests/test_auth.py
  - tests/auth/test_user_model.py
  - tests/test_user_visibility.py
  - tests/auth/test_guards.py
  - tests/auth/test_permissions.py
-->

---
### Requirement: Identity tags are managed only by users with MANAGE_USERS

The system SHALL enforce that `identity_tags` can only be modified by a user holding the `MANAGE_USERS` permission. A user MUST NOT be able to update their own `identity_tags` via the self-edit profile endpoint.

#### Scenario: Admin sets identity tags for a user

- **WHEN** a user with `MANAGE_USERS` sends `PUT /admin/users/{id}` with a valid `identity_tags` array
- **THEN** the target user's `identity_tags` SHALL be updated accordingly

#### Scenario: Self-edit cannot change identity tags

- **WHEN** an authenticated user sends `PUT /auth/profile` including an `identity_tags` field
- **THEN** the system MUST ignore the `identity_tags` field and leave it unchanged


<!-- @trace
source: permission-identity-refactor
updated: 2026-03-19
code:
  - src/core/classes/router.py
  - src/core/users/schemas.py
  - src/core/classes/service.py
  - src/core/users/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/pages/router.py
  - src/core/auth/router.py
  - src/tasks/checkin/router.py
  - src/tasks/templates/router.py
  - src/core/classes/models.py
  - src/templates/admin/classes_list.html
  - scripts/migrations/20260319_003_init_identity_tags.py
  - src/community/feed/router.py
  - src/core/users/models.py
  - src/gamification/leaderboard/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/templates/admin/users_list.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_assign.html
  - src/templates/teacher/template_form.html
  - scripts/migrations/20260319_002_manage_class_rename.py
  - src/core/auth/permissions.py
tests:
  - tests/test_class_permissions.py
  - tests/test_admin_permissions.py
  - tests/test_identity_tags.py
  - tests/test_auth.py
  - tests/auth/test_user_model.py
  - tests/test_user_visibility.py
  - tests/auth/test_guards.py
  - tests/auth/test_permissions.py
-->

---
### Requirement: Identity tags endpoint returns available tag values

The system SHALL provide `GET /admin/permissions/identity-tags` returning the list of all valid `IdentityTag` values as a JSON array of strings. The endpoint MUST require `MANAGE_USERS` permission.

#### Scenario: Identity tags list endpoint returns all values

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/permissions/identity-tags`
- **THEN** the system SHALL return HTTP 200 with a JSON array containing `"teacher"`, `"student"`, and `"staff"`

<!-- @trace
source: permission-identity-refactor
updated: 2026-03-19
code:
  - src/core/classes/router.py
  - src/core/users/schemas.py
  - src/core/classes/service.py
  - src/core/users/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/pages/router.py
  - src/core/auth/router.py
  - src/tasks/checkin/router.py
  - src/tasks/templates/router.py
  - src/core/classes/models.py
  - src/templates/admin/classes_list.html
  - scripts/migrations/20260319_003_init_identity_tags.py
  - src/community/feed/router.py
  - src/core/users/models.py
  - src/gamification/leaderboard/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/templates/admin/users_list.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_assign.html
  - src/templates/teacher/template_form.html
  - scripts/migrations/20260319_002_manage_class_rename.py
  - src/core/auth/permissions.py
tests:
  - tests/test_class_permissions.py
  - tests/test_admin_permissions.py
  - tests/test_identity_tags.py
  - tests/test_auth.py
  - tests/auth/test_user_model.py
  - tests/test_user_visibility.py
  - tests/auth/test_guards.py
  - tests/auth/test_permissions.py
-->