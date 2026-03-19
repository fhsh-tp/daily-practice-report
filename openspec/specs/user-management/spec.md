# user-management Specification

## Purpose

Defines user account management: CRUD API, bulk operations, CSV batch import, and the corresponding admin UI pages. All endpoints require `MANAGE_USERS` permission.

## Requirements

### Requirement: User list API returns paginated user records

The system SHALL provide `GET /admin/users` returning a paginated list of all users. The endpoint MUST require `MANAGE_USERS` permission. Response MUST include `id`, `username`, `display_name`, `permissions`, and `tags` for each user. The endpoint SHALL support `page` and `page_size` query parameters, defaulting to page 1 and page size 20.

#### Scenario: Admin fetches user list

- **WHEN** a user with `MANAGE_USERS` permission sends `GET /admin/users`
- **THEN** the system SHALL return HTTP 200 with a list of user objects and pagination metadata

#### Scenario: Unauthorized request is rejected

- **WHEN** a user without `MANAGE_USERS` permission sends `GET /admin/users`
- **THEN** the system SHALL return HTTP 403


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
### Requirement: Single user read API

The system SHALL provide `GET /admin/users/{id}` returning the full user record for the given ID. The endpoint MUST require `MANAGE_USERS` permission. If the user does not exist, the system MUST return HTTP 404.

#### Scenario: Admin reads existing user

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/{id}` for an existing user
- **THEN** the system SHALL return HTTP 200 with the user's `id`, `username`, `display_name`, `permissions`, and `tags`

#### Scenario: Non-existent user returns 404

- **WHEN** `GET /admin/users/{id}` is called with an ID that does not exist
- **THEN** the system SHALL return HTTP 404


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
### Requirement: User update API

The system SHALL provide `PUT /admin/users/{id}` to update `display_name`, `permissions`, and `tags`. The endpoint MUST require `MANAGE_USERS` permission. Username MUST NOT be changed via this endpoint. Password update SHALL be performed via a separate field `new_password`; if absent, the password MUST remain unchanged.

#### Scenario: Admin updates user display name and permissions

- **WHEN** a user with `MANAGE_USERS` sends `PUT /admin/users/{id}` with valid `display_name` and `permissions`
- **THEN** the system SHALL update the user document and return HTTP 200 with the updated record

#### Scenario: Password unchanged when new_password absent

- **WHEN** `PUT /admin/users/{id}` is submitted without `new_password`
- **THEN** the user's `hashed_password` MUST remain unchanged


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

The system SHALL provide `POST /admin/users/import` accepting a multipart file upload of a CSV with columns: `username`, `password`, `display_name`, `preset`, `tags` (tags semicolon-separated, optional). The endpoint MUST require `MANAGE_USERS` permission. Parsing MUST use Python's standard `csv` module. The `preset` column MUST match one of the defined preset names (`STUDENT`, `TEACHER`, `USER_ADMIN`, `SYS_ADMIN`, `SITE_ADMIN`). Rows with invalid preset or duplicate username SHALL be skipped and reported. The response MUST return `{"success": N, "failed": [{"row": N, "reason": "..."}]}`.

#### Scenario: Valid CSV import

- **WHEN** a user with `MANAGE_USERS` uploads a valid CSV file
- **THEN** all valid rows SHALL be created as new users and the response SHALL report the success count

#### Scenario: Duplicate username rows are skipped

- **WHEN** a CSV row contains a username that already exists
- **THEN** that row MUST be skipped and reported in the `failed` list with reason "Username already exists"

#### Scenario: Invalid preset rows are skipped

- **WHEN** a CSV row contains an unrecognized preset name
- **THEN** that row MUST be skipped and reported in the `failed` list with reason "Unknown preset"


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