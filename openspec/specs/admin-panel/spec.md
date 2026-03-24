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

The system SHALL render an overview page at `GET /pages/admin/` that displays statistics cards for: total registered users, active class count, and archived class count. Below the statistics, the page SHALL display management entry cards for each section the user has access to: "使用者管理" (requires `MANAGE_USERS`), "班級管理" (requires `MANAGE_ALL_CLASSES`), "系統管理" (requires `WRITE_SYSTEM`). Each card SHALL include a title, description, and link to the respective management page.

#### Scenario: Overview renders statistics cards

- **WHEN** an authorized admin navigates to `/pages/admin/`
- **THEN** the page SHALL display three statistics cards: total user count, active class count, and archived class count

#### Scenario: Overview renders management entry cards

- **WHEN** an authorized admin with `MANAGE_USERS` and `WRITE_SYSTEM` navigates to `/pages/admin/`
- **THEN** the page SHALL display entry cards for "使用者管理" and "系統管理" but NOT "班級管理" (since user lacks `MANAGE_ALL_CLASSES`)

---
### Requirement: Admin navigation reflects caller's permissions

The sidebar SHALL render admin management items within the unified "平台管理" section instead of separate "管理工具" and "管理員" sections. The section SHALL show only the items the current user is permitted to access: "使用者管理" (requires `MANAGE_USERS`), "班級管理" (requires `MANAGE_ALL_CLASSES`), and "系統管理" (requires `WRITE_SYSTEM`).

#### Scenario: Full admin sees all platform management items

- **WHEN** a user with `MANAGE_USERS`, `MANAGE_ALL_CLASSES`, and `WRITE_SYSTEM` views the sidebar
- **THEN** the "平台管理" section SHALL contain "使用者管理", "班級管理", and "系統管理"

#### Scenario: User-only admin sees restricted items

- **WHEN** a user with `MANAGE_USERS` but without `WRITE_SYSTEM` or `MANAGE_ALL_CLASSES` views the sidebar
- **THEN** the "平台管理" section SHALL contain only "使用者管理"
