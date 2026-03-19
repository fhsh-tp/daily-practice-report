## ADDED Requirements

### Requirement: Setup wizard is shown on first deployment

The system SHALL display a setup wizard HTML page at `GET /setup` when the Redis key `system:configured` is absent and no `SystemConfig` document exists in MongoDB. The page MUST be rendered via Jinja2 and SHALL NOT require authentication.

#### Scenario: First boot redirects to setup

- **WHEN** the application starts with no `system:configured` Redis key and no SystemConfig in MongoDB
- **THEN** `GET /setup` MUST return an HTML form page for initial configuration

#### Scenario: Setup page blocked after configuration

- **WHEN** `system:configured` Redis key is `"true"`
- **AND** a user navigates to `GET /setup`
- **THEN** the system SHALL redirect to `/` (HTTP 302)

### Requirement: Setup wizard form submits initial configuration

The system SHALL accept `POST /setup` with at minimum: site name and initial admin username/password. Upon successful submission, the system MUST create a `SystemConfig` document, create the admin `User` document, set Redis `system:configured = "true"`, and redirect to `/`.

#### Scenario: Successful setup submission

- **WHEN** the administrator submits a valid setup form with site name, admin username, and admin password
- **THEN** `SystemConfig` MUST be persisted in MongoDB
- **AND** an admin `User` MUST be created with full system admin permissions
- **AND** Redis `system:configured` MUST be set to `"true"`
- **AND** the response MUST redirect to `/` (HTTP 302)

#### Scenario: Duplicate setup attempt via API

- **WHEN** `POST /setup` is called after setup is already complete
- **THEN** the system SHALL return HTTP 409 Conflict

### Requirement: Startup lifespan checks setup state

The application `lifespan` SHALL check setup state on every startup before the application begins serving requests.

#### Scenario: Startup with completed setup

- **WHEN** the application starts and setup is confirmed (Redis flag or MongoDB fallback)
- **THEN** `SystemConfig` MUST be loaded into `app.state.system_config` before the first request is handled

#### Scenario: Startup without completed setup

- **WHEN** the application starts and no setup has been completed
- **THEN** the application SHALL start normally but MUST only serve `/setup` and static assets until setup completes
