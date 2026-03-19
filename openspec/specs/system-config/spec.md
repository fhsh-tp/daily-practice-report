## ADDED Requirements

### Requirement: SystemConfig document stores global settings

The system SHALL maintain a single `SystemConfig` Beanie Document in MongoDB with a fixed `_id` of `"global"`. This document MUST store system-level settings including site name and admin email.

#### Scenario: SystemConfig is created during setup

- **WHEN** the administrator completes the setup wizard form
- **THEN** a `SystemConfig` document with `_id = "global"` MUST be written to MongoDB

#### Scenario: SystemConfig is retrieved on startup

- **WHEN** the application starts and Redis flag `system:configured` is `"true"`
- **THEN** the system SHALL load the `SystemConfig` document from MongoDB and make it available via `app.state.system_config`


<!-- @trace
source: system-setup-wizard
updated: 2026-03-18
code:
  - src/core/system/models.py
  - src/shared/redis.py
  - docker-compose.yml
  - pyproject.toml
  - src/main.py
  - src/core/system/__init__.py
  - src/templates/setup.html
  - uv.lock
  - src/core/system/startup.py
  - src/shared/__init__.py
  - src/core/system/router.py
tests:
  - tests/test_setup_startup.py
  - tests/test_redis_shared.py
  - tests/test_system_config.py
  - tests/test_setup_wizard.py
-->

### Requirement: Redis caches system configuration state

The system SHALL use a Redis key `system:configured` to cache whether initial setup has been completed. The key value MUST be the string `"true"` when configured.

#### Scenario: Redis flag set after setup

- **WHEN** the setup wizard completes successfully
- **THEN** Redis `system:configured` MUST be set to `"true"` with no TTL (persistent)

#### Scenario: Redis flag missing but config exists in MongoDB

- **WHEN** the application starts and Redis key `system:configured` is absent
- **AND** a `SystemConfig` document exists in MongoDB
- **THEN** the system SHALL automatically restore the Redis flag to `"true"` and load the config


<!-- @trace
source: system-setup-wizard
updated: 2026-03-18
code:
  - src/core/system/models.py
  - src/shared/redis.py
  - docker-compose.yml
  - pyproject.toml
  - src/main.py
  - src/core/system/__init__.py
  - src/templates/setup.html
  - uv.lock
  - src/core/system/startup.py
  - src/shared/__init__.py
  - src/core/system/router.py
tests:
  - tests/test_setup_startup.py
  - tests/test_redis_shared.py
  - tests/test_system_config.py
  - tests/test_setup_wizard.py
-->

### Requirement: System config is updatable by system administrator

The system SHALL provide an API endpoint to update `SystemConfig`. Access MUST be restricted to users with system administrator permissions (enforced by the RBAC system).

#### Scenario: Admin updates system config

- **WHEN** an authenticated user with system admin permissions submits updated config values
- **THEN** the MongoDB `SystemConfig` document MUST be updated and the in-memory state refreshed

## Requirements

<!-- @trace
source: system-setup-wizard
updated: 2026-03-18
code:
  - src/core/system/models.py
  - src/shared/redis.py
  - docker-compose.yml
  - pyproject.toml
  - src/main.py
  - src/core/system/__init__.py
  - src/templates/setup.html
  - uv.lock
  - src/core/system/startup.py
  - src/shared/__init__.py
  - src/core/system/router.py
tests:
  - tests/test_setup_startup.py
  - tests/test_redis_shared.py
  - tests/test_system_config.py
  - tests/test_setup_wizard.py
-->

### Requirement: SystemConfig document stores global settings

The system SHALL maintain a single `SystemConfig` Beanie Document in MongoDB with a fixed `_id` of `"global"`. This document MUST store system-level settings including site name and admin email.

#### Scenario: SystemConfig is created during setup

- **WHEN** the administrator completes the setup wizard form
- **THEN** a `SystemConfig` document with `_id = "global"` MUST be written to MongoDB

#### Scenario: SystemConfig is retrieved on startup

- **WHEN** the application starts and Redis flag `system:configured` is `"true"`
- **THEN** the system SHALL load the `SystemConfig` document from MongoDB and make it available via `app.state.system_config`

---
### Requirement: Redis caches system configuration state

The system SHALL use a Redis key `system:configured` to cache whether initial setup has been completed. The key value MUST be the string `"true"` when configured.

#### Scenario: Redis flag set after setup

- **WHEN** the setup wizard completes successfully
- **THEN** Redis `system:configured` MUST be set to `"true"` with no TTL (persistent)

#### Scenario: Redis flag missing but config exists in MongoDB

- **WHEN** the application starts and Redis key `system:configured` is absent
- **AND** a `SystemConfig` document exists in MongoDB
- **THEN** the system SHALL automatically restore the Redis flag to `"true"` and load the config

---
### Requirement: System config is updatable by system administrator

The system SHALL provide an API endpoint to update `SystemConfig`. Access MUST be restricted to users with system administrator permissions (enforced by the RBAC system).

#### Scenario: Admin updates system config

- **WHEN** an authenticated user with system admin permissions submits updated config values
- **THEN** the MongoDB `SystemConfig` document MUST be updated and the in-memory state refreshed
---
### Requirement: System config read API

The system SHALL provide `GET /admin/system` returning the current `SystemConfig` values. The endpoint MUST require `READ_SYSTEM` permission. The response MUST include at minimum `site_name` and `admin_email`.

#### Scenario: Admin reads system config

- **WHEN** a user with `READ_SYSTEM` sends `GET /admin/system`
- **THEN** the system SHALL return HTTP 200 with the current `site_name` and `admin_email`

#### Scenario: Unauthorized read is rejected

- **WHEN** a user without `READ_SYSTEM` sends `GET /admin/system`
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
### Requirement: System config update API

The system SHALL provide `PUT /admin/system` accepting a JSON body with updatable fields (`site_name`, `admin_email`). The endpoint MUST require `WRITE_SYSTEM` permission. On success, the MongoDB `SystemConfig` document MUST be updated and `app.state.system_config` MUST reflect the new values immediately. The `WebPage` global context `site_name` MUST also be refreshed via `webpage_context_update`.

#### Scenario: Admin updates site name

- **WHEN** a user with `WRITE_SYSTEM` sends `PUT /admin/system` with a new `site_name`
- **THEN** the MongoDB document MUST be updated, `app.state.system_config.site_name` MUST reflect the new value, and subsequent page renders SHALL use the new site name

#### Scenario: Unauthorized update is rejected

- **WHEN** a user without `WRITE_SYSTEM` sends `PUT /admin/system`
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
### Requirement: System settings admin page

The system SHALL render a page at `GET /pages/admin/system/` displaying a form pre-filled with current `SystemConfig` values. The page MUST require `WRITE_SYSTEM` permission. Form submission SHALL use the PRG pattern: POST to the API, then redirect back to the settings page with a success or error message.

#### Scenario: Settings page pre-fills current config

- **WHEN** an admin with `WRITE_SYSTEM` navigates to `/pages/admin/system/`
- **THEN** the form SHALL display the current `site_name` and `admin_email` values

#### Scenario: Successful update redirects with confirmation

- **WHEN** an admin submits the system settings form with valid data
- **THEN** the system SHALL update the config and redirect to `/pages/admin/system/` with a success indicator

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