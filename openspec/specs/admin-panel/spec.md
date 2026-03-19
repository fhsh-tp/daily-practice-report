# admin-panel Specification

## Purpose

Defines the unified Admin Panel page layer: access control, overview dashboard, and navigation. The Admin Panel is served under `/pages/admin/*` and requires administrative permissions.

## Requirements

### Requirement: Admin Panel is accessible only to authorized users

The system SHALL serve Admin Panel pages under `/pages/admin/*`. Every route in this group MUST require an authenticated user with at least `MANAGE_USERS` OR `WRITE_SYSTEM` permission. Unauthenticated requests MUST redirect to `/pages/login`. Users lacking both permissions MUST receive HTTP 403.

#### Scenario: Authorized user accesses admin panel

- **WHEN** an authenticated user with `MANAGE_USERS` permission navigates to `/pages/admin/`
- **THEN** the system SHALL render the Admin Panel overview page with HTTP 200

#### Scenario: Unauthenticated access redirects to login

- **WHEN** an unauthenticated request is made to any `/pages/admin/*` route
- **THEN** the system SHALL redirect to `/pages/login?next=<requested_path>` with HTTP 302

#### Scenario: Insufficient permission returns 403

- **WHEN** an authenticated user with only `SUBMIT_TASK` permission navigates to `/pages/admin/`
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
### Requirement: Admin Panel overview page displays system summary

The system SHALL render an overview page at `GET /pages/admin/` that displays the total number of registered users and current site name loaded from `SystemConfig`.

#### Scenario: Overview renders user count and site name

- **WHEN** an authorized admin navigates to `/pages/admin/`
- **THEN** the page SHALL display the total user count and the configured site name


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
### Requirement: Admin navigation reflects caller's permissions

The system SHALL render an admin navigation bar that shows only the sections the current user is permitted to access: "User Management" (requires `MANAGE_USERS`) and "System Settings" (requires `WRITE_SYSTEM`).

#### Scenario: Full admin sees all nav items

- **WHEN** a user with both `MANAGE_USERS` and `WRITE_SYSTEM` views the admin panel
- **THEN** both "User Management" and "System Settings" links SHALL be present in the navigation

#### Scenario: User-only admin sees restricted nav

- **WHEN** a user with `MANAGE_USERS` but without `WRITE_SYSTEM` views the admin panel
- **THEN** "System Settings" link SHALL NOT be rendered in the navigation

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