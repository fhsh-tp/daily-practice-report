## ADDED Requirements

### Requirement: SystemConfig document stores global settings

The system SHALL maintain a single `SystemConfig` Beanie Document in MongoDB with a fixed `_id` of `"global"`. This document MUST store system-level settings including site name and admin email.

#### Scenario: SystemConfig is created during setup

- **WHEN** the administrator completes the setup wizard form
- **THEN** a `SystemConfig` document with `_id = "global"` MUST be written to MongoDB

#### Scenario: SystemConfig is retrieved on startup

- **WHEN** the application starts and Redis flag `system:configured` is `"true"`
- **THEN** the system SHALL load the `SystemConfig` document from MongoDB and make it available via `app.state.system_config`

### Requirement: Redis caches system configuration state

The system SHALL use a Redis key `system:configured` to cache whether initial setup has been completed. The key value MUST be the string `"true"` when configured.

#### Scenario: Redis flag set after setup

- **WHEN** the setup wizard completes successfully
- **THEN** Redis `system:configured` MUST be set to `"true"` with no TTL (persistent)

#### Scenario: Redis flag missing but config exists in MongoDB

- **WHEN** the application starts and Redis key `system:configured` is absent
- **AND** a `SystemConfig` document exists in MongoDB
- **THEN** the system SHALL automatically restore the Redis flag to `"true"` and load the config

### Requirement: System config is updatable by system administrator

The system SHALL provide an API endpoint to update `SystemConfig`. Access MUST be restricted to users with system administrator permissions (enforced by the RBAC system).

#### Scenario: Admin updates system config

- **WHEN** an authenticated user with system admin permissions submits updated config values
- **THEN** the MongoDB `SystemConfig` document MUST be updated and the in-memory state refreshed
