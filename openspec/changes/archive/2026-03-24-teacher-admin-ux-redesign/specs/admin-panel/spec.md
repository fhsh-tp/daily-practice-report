## MODIFIED Requirements

### Requirement: Admin Panel overview page displays system summary

The system SHALL render an overview page at `GET /pages/admin/` that displays statistics cards for: total registered users, active class count, and archived class count. Below the statistics, the page SHALL display management entry cards for each section the user has access to: "使用者管理" (requires `MANAGE_USERS`), "班級管理" (requires `MANAGE_ALL_CLASSES`), "系統管理" (requires `WRITE_SYSTEM`). Each card SHALL include a title, description, and link to the respective management page.

#### Scenario: Overview renders statistics cards

- **WHEN** an authorized admin navigates to `/pages/admin/`
- **THEN** the page SHALL display three statistics cards: total user count, active class count, and archived class count

#### Scenario: Overview renders management entry cards

- **WHEN** an authorized admin with `MANAGE_USERS` and `WRITE_SYSTEM` navigates to `/pages/admin/`
- **THEN** the page SHALL display entry cards for "使用者管理" and "系統管理" but NOT "班級管理" (since user lacks `MANAGE_ALL_CLASSES`)

### Requirement: Admin navigation reflects caller's permissions

The sidebar SHALL render admin management items within the unified "平台管理" section instead of separate "管理工具" and "管理員" sections. The section SHALL show only the items the current user is permitted to access: "使用者管理" (requires `MANAGE_USERS`), "班級管理" (requires `MANAGE_ALL_CLASSES`), and "系統管理" (requires `WRITE_SYSTEM`).

#### Scenario: Full admin sees all platform management items

- **WHEN** a user with `MANAGE_USERS`, `MANAGE_ALL_CLASSES`, and `WRITE_SYSTEM` views the sidebar
- **THEN** the "平台管理" section SHALL contain "使用者管理", "班級管理", and "系統管理"

#### Scenario: User-only admin sees restricted items

- **WHEN** a user with `MANAGE_USERS` but without `WRITE_SYSTEM` or `MANAGE_ALL_CLASSES` views the sidebar
- **THEN** the "平台管理" section SHALL contain only "使用者管理"
