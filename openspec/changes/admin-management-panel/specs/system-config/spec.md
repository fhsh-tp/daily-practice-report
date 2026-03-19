## ADDED Requirements

### Requirement: System config read API

The system SHALL provide `GET /admin/system` returning the current `SystemConfig` values. The endpoint MUST require `READ_SYSTEM` permission. The response MUST include at minimum `site_name` and `admin_email`.

#### Scenario: Admin reads system config

- **WHEN** a user with `READ_SYSTEM` sends `GET /admin/system`
- **THEN** the system SHALL return HTTP 200 with the current `site_name` and `admin_email`

#### Scenario: Unauthorized read is rejected

- **WHEN** a user without `READ_SYSTEM` sends `GET /admin/system`
- **THEN** the system SHALL return HTTP 403

---

### Requirement: System config update API

The system SHALL provide `PUT /admin/system` accepting a JSON body with updatable fields (`site_name`, `admin_email`). The endpoint MUST require `WRITE_SYSTEM` permission. On success, the MongoDB `SystemConfig` document MUST be updated and `app.state.system_config` MUST reflect the new values immediately. The `WebPage` global context `site_name` MUST also be refreshed via `webpage_context_update`.

#### Scenario: Admin updates site name

- **WHEN** a user with `WRITE_SYSTEM` sends `PUT /admin/system` with a new `site_name`
- **THEN** the MongoDB document MUST be updated, `app.state.system_config.site_name` MUST reflect the new value, and subsequent page renders SHALL use the new site name

#### Scenario: Unauthorized update is rejected

- **WHEN** a user without `WRITE_SYSTEM` sends `PUT /admin/system`
- **THEN** the system SHALL return HTTP 403

---

### Requirement: System settings admin page

The system SHALL render a page at `GET /pages/admin/system/` displaying a form pre-filled with current `SystemConfig` values. The page MUST require `WRITE_SYSTEM` permission. Form submission SHALL use the PRG pattern: POST to the API, then redirect back to the settings page with a success or error message.

#### Scenario: Settings page pre-fills current config

- **WHEN** an admin with `WRITE_SYSTEM` navigates to `/pages/admin/system/`
- **THEN** the form SHALL display the current `site_name` and `admin_email` values

#### Scenario: Successful update redirects with confirmation

- **WHEN** an admin submits the system settings form with valid data
- **THEN** the system SHALL update the config and redirect to `/pages/admin/system/` with a success indicator
