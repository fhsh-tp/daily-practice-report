## ADDED Requirements

### Requirement: Admin page group requires admin-level permission

The system SHALL register a set of routes under `/pages/admin/*` in the pages router. Every route in this group MUST use a dependency that verifies the authenticated user holds at least `MANAGE_USERS` OR `WRITE_SYSTEM`. Any route within the group MAY add further per-route permission checks beyond this baseline.

#### Scenario: Base admin guard allows user with MANAGE_USERS

- **WHEN** a user with `MANAGE_USERS` accesses any `/pages/admin/*` route
- **THEN** the route handler SHALL execute and return the page

#### Scenario: Base admin guard allows user with WRITE_SYSTEM

- **WHEN** a user with `WRITE_SYSTEM` (but without `MANAGE_USERS`) accesses `/pages/admin/`
- **THEN** the route handler SHALL execute and return the overview page

#### Scenario: User without admin permissions receives 403

- **WHEN** a user holding only `STUDENT` permissions accesses any `/pages/admin/*` route
- **THEN** the system SHALL return HTTP 403

---

### Requirement: Admin templates use a shared admin layout

The system SHALL provide a Jinja2 base template at `src/templates/admin/layout.html` that all admin pages extend. The layout MUST include the admin navigation bar described in the admin-panel spec. Admin templates MUST be placed under `src/templates/admin/`.

#### Scenario: Admin pages share consistent layout

- **WHEN** any admin page is rendered
- **THEN** the HTML MUST include the admin navigation bar from `admin/layout.html`
