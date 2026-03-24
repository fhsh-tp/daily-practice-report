## MODIFIED Requirements

### Requirement: Admin navigation reflects caller's permissions

The sidebar SHALL render a single "管理後台" link under the "平台管理" section that navigates to `/pages/admin/`. The link SHALL appear when the user has `MANAGE_USERS`, `MANAGE_ALL_CLASSES`, or `WRITE_SYSTEM` permission. The sidebar SHALL NOT render individual items for "使用者管理", "班級管理", or "系統管理" — sub-page navigation SHALL be handled by the Admin Panel's own tab navigation.

#### Scenario: Admin user sees single admin entry in sidebar

- **WHEN** a user with any admin permission (`MANAGE_USERS`, `MANAGE_ALL_CLASSES`, or `WRITE_SYSTEM`) views the sidebar
- **THEN** the "平台管理" section SHALL contain a single "管理後台" link pointing to `/pages/admin/`

#### Scenario: Sidebar does not show individual admin items

- **WHEN** a user with `MANAGE_USERS`, `MANAGE_ALL_CLASSES`, and `WRITE_SYSTEM` views the sidebar
- **THEN** the sidebar SHALL NOT display separate "使用者管理", "班級管理", or "系統管理" links

#### Scenario: Non-admin user sees no platform management section

- **WHEN** a user without any admin permission views the sidebar
- **THEN** the sidebar SHALL NOT display the "平台管理" section
