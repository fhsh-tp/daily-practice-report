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