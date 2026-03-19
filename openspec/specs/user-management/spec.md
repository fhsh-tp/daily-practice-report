# user-management Specification

## Purpose

Defines user account management: CRUD API, bulk operations, CSV batch import, and the corresponding admin UI pages. All endpoints require `MANAGE_USERS` permission.

## Requirements

### Requirement: User list API returns paginated user records

The system SHALL provide `GET /admin/users` returning a paginated list of all users. The endpoint MUST require `MANAGE_USERS` permission. Response MUST include `id`, `username`, `display_name`, `name`, `email`, `permissions`, `identity_tags`, `tags`, and `student_profile` (if present) for each user. The endpoint SHALL support `page` and `page_size` query parameters, defaulting to page 1 and page size 20.

#### Scenario: Admin fetches user list

- **WHEN** a user with `MANAGE_USERS` permission sends `GET /admin/users`
- **THEN** the system SHALL return HTTP 200 with a list of user objects including `name`, `email`, `identity_tags`, and `student_profile` fields alongside existing fields

#### Scenario: Unauthorized request is rejected

- **WHEN** a user without `MANAGE_USERS` permission sends `GET /admin/users`
- **THEN** the system SHALL return HTTP 403


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
### Requirement: Single user read API

The system SHALL provide `GET /admin/users/{id}` returning the full user record for the given ID. The endpoint MUST require `MANAGE_USERS` permission. The response MUST include `name`, `email`, `identity_tags`, and `student_profile`. If the user does not exist, the system MUST return HTTP 404.

#### Scenario: Admin reads existing user

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/{id}` for an existing user
- **THEN** the system SHALL return HTTP 200 with the full user record including `name`, `email`, `identity_tags`, and `student_profile`

#### Scenario: Non-existent user returns 404

- **WHEN** `GET /admin/users/{id}` is called with an ID that does not exist
- **THEN** the system SHALL return HTTP 404


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
### Requirement: User update API

The system SHALL provide `PUT /admin/users/{id}` to update `display_name`, `name`, `email`, `permissions`, `identity_tags`, `tags`, and `student_profile`. The endpoint MUST require `MANAGE_USERS` permission. Username MUST NOT be changed via this endpoint. Password update SHALL be performed via a separate field `new_password`; if absent, the password MUST remain unchanged.

#### Scenario: Admin updates user identity tags and real name

- **WHEN** a user with `MANAGE_USERS` sends `PUT /admin/users/{id}` with valid `name`, `email`, and `identity_tags`
- **THEN** the system SHALL update those fields and return HTTP 200 with the updated record

#### Scenario: Admin updates student profile fields

- **WHEN** a user with `MANAGE_USERS` sends `PUT /admin/users/{id}` with a valid `student_profile` object
- **THEN** the system SHALL update `student_profile.class_name` and `student_profile.seat_number` accordingly

#### Scenario: Password unchanged when new_password absent

- **WHEN** `PUT /admin/users/{id}` is submitted without `new_password`
- **THEN** the user's `hashed_password` MUST remain unchanged


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
### Requirement: Single user delete API

The system SHALL provide `DELETE /admin/users/{id}` to delete a user account. The endpoint MUST require `MANAGE_USERS` permission. An admin MUST NOT be able to delete their own account via this endpoint; the system SHALL return HTTP 400 in that case.

#### Scenario: Admin deletes another user

- **WHEN** a user with `MANAGE_USERS` sends `DELETE /admin/users/{id}` for a different user
- **THEN** the system SHALL delete the user and return HTTP 204

#### Scenario: Self-deletion is rejected

- **WHEN** an admin sends `DELETE /admin/users/{id}` where `{id}` is their own user ID
- **THEN** the system SHALL return HTTP 400 with an appropriate error message


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
### Requirement: Bulk delete API

The system SHALL provide `DELETE /admin/users/bulk` accepting a JSON body `{"ids": ["<id>", ...]}`. The endpoint MUST require `MANAGE_USERS` permission. The caller's own ID MUST be excluded from deletion silently. The response MUST return the count of deleted users.

#### Scenario: Admin bulk deletes multiple users

- **WHEN** a user with `MANAGE_USERS` sends `DELETE /admin/users/bulk` with a list of IDs
- **THEN** the system SHALL delete all matching users (excluding the caller's own ID) and return `{"deleted": N}`


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
### Requirement: Bulk permissions update API

The system SHALL provide `PATCH /admin/users/bulk` accepting `{"ids": ["<id>", ...], "permissions": <int>}`. The endpoint MUST require `MANAGE_USERS` permission. All specified users SHALL have their `permissions` field updated to the provided value.

#### Scenario: Admin bulk updates permissions

- **WHEN** a user with `MANAGE_USERS` sends `PATCH /admin/users/bulk` with IDs and a valid permissions int
- **THEN** all specified users SHALL have their permissions updated and the system MUST return `{"updated": N}`


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
### Requirement: CSV batch import API

The system SHALL provide `POST /admin/users/import` accepting a multipart file upload of a CSV. The student CSV MUST support columns: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags` (semicolon-separated, optional), `class_name` (optional), `seat_number` (optional). The staff/teacher CSV MUST support: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags` (optional). The endpoint MUST require `MANAGE_USERS` permission. The `preset` column MUST match a defined preset name. The `identity_tag` column MUST match a valid `IdentityTag` value. Rows with invalid preset, invalid identity_tag, or duplicate username SHALL be skipped and reported. The response MUST return `{"success": N, "failed": [{"row": N, "reason": "..."}]}`.

#### Scenario: Valid student CSV import

- **WHEN** a user with `MANAGE_USERS` uploads a valid student CSV file
- **THEN** all valid rows SHALL be created as new users with the correct `identity_tags` and `student_profile` populated, and the response SHALL report the success count

#### Scenario: Invalid identity_tag rows are skipped

- **WHEN** a CSV row contains an unrecognized identity_tag value
- **THEN** that row MUST be skipped and reported in the `failed` list with reason "Unknown identity tag"

#### Scenario: Duplicate username rows are skipped

- **WHEN** a CSV row contains a username that already exists
- **THEN** that row MUST be skipped and reported in the `failed` list with reason "Username already exists"


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
### Requirement: Admin user list page

The system SHALL render a page at `GET /pages/admin/users/` displaying all users in a table with checkboxes for multi-select. The page MUST require `MANAGE_USERS` permission. The table SHALL include columns for username, display name, permissions summary, and tags. The page MUST provide UI controls for bulk delete and bulk permissions change on selected rows.

#### Scenario: User list page renders all users

- **WHEN** an admin with `MANAGE_USERS` navigates to `/pages/admin/users/`
- **THEN** all registered users SHALL be displayed in a table with checkboxes


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
### Requirement: User create and edit pages

The system SHALL render a create page at `GET /pages/admin/users/new` and an edit page at `GET /pages/admin/users/{id}/edit`. Both pages MUST require `MANAGE_USERS` permission. Both pages MUST render the permission assignment matrix (domain × level) populated from `GET /admin/permissions/schema` and a preset selector populated from `GET /admin/permissions/presets` as a quick-fill shortcut.

#### Scenario: Create page renders permission matrix

- **WHEN** an admin navigates to `/pages/admin/users/new`
- **THEN** the page SHALL render a permission matrix with one row per domain from the schema endpoint

#### Scenario: Edit page pre-fills current user permissions

- **WHEN** an admin navigates to `/pages/admin/users/{id}/edit`
- **THEN** the page SHALL pre-select the correct read/write level for each domain based on the user's current `permissions` value

#### Scenario: Preset selector auto-fills matrix

- **WHEN** an admin selects a preset from the preset dropdown
- **THEN** the matrix cells SHALL update to reflect the preset's domain-level breakdown without submitting the form

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
### Requirement: User profile visibility is controlled by viewer identity

The system SHALL apply visibility rules when returning user data in non-admin contexts. The rules SHALL be enforced via distinct Pydantic response schemas:

- `UserPublicView`: exposes only `id` and `display_name`
- `UserStaffView`: exposes `id`, `display_name`, `name`, `email`, `identity_tags`, and `student_profile`
- `UserAdminView`: exposes all fields (used by admin endpoints)

The viewer's `identity_tags` SHALL determine which schema is applied: viewers with `TEACHER` or `STAFF` identity SHALL receive `UserStaffView`; all other authenticated viewers SHALL receive `UserPublicView`.

#### Scenario: Student views another student's profile

- **WHEN** a user with identity tag `STUDENT` requests another user's profile in a non-admin context
- **THEN** the system SHALL return only `id` and `display_name`

#### Scenario: Teacher views a student's profile

- **WHEN** a user with identity tag `TEACHER` requests a student's profile in a non-admin context
- **THEN** the system SHALL return `id`, `display_name`, `name`, `email`, `identity_tags`, and `student_profile`

#### Scenario: Admin endpoint always returns full profile

- **WHEN** any user with `MANAGE_USERS` requests a user's profile via `GET /admin/users/{id}`
- **THEN** the system MUST return the full `UserAdminView` regardless of identity tags


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
### Requirement: Authenticated user can update own display name

The system SHALL provide `PUT /auth/profile` allowing an authenticated user to update only their `display_name`. All other fields MUST be ignored in this endpoint. The endpoint MUST reject unauthenticated requests with HTTP 401.

#### Scenario: User updates own display name

- **WHEN** an authenticated user sends `PUT /auth/profile` with a new `display_name`
- **THEN** the system SHALL update only `display_name` and return HTTP 200 with the updated value

#### Scenario: User cannot change name via profile endpoint

- **WHEN** an authenticated user sends `PUT /auth/profile` including a `name` field
- **THEN** the system MUST ignore the `name` field and leave it unchanged


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
### Requirement: CSV batch import template download

The system SHALL provide two downloadable CSV template files via `GET /admin/users/import/template?type=student` and `GET /admin/users/import/template?type=staff`. Each response MUST have `Content-Type: text/csv` and `Content-Disposition: attachment` headers. The student template MUST include columns: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags`, `class_name`, `seat_number`. The staff template MUST include columns: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags`.

#### Scenario: Download student CSV template

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/import/template?type=student`
- **THEN** the system SHALL return a CSV file with the student column headers and one example row

#### Scenario: Download staff CSV template

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/import/template?type=staff`
- **THEN** the system SHALL return a CSV file with the staff column headers and one example row

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