## MODIFIED Requirements

### Requirement: Setup wizard is shown on first deployment

The system SHALL display a setup wizard HTML page at `GET /setup` when the Redis key `system:configured` is absent and no `SystemConfig` document exists in MongoDB. The page SHALL be rendered via `WebPage` and SHALL NOT require authentication. If an `error` query parameter is present, the page SHALL display it.

#### Scenario: First boot redirects to setup

- **WHEN** the application starts with no `system:configured` Redis key and no SystemConfig in MongoDB
- **THEN** `GET /setup` MUST return an HTML form page for initial configuration

#### Scenario: Setup page blocked after configuration

- **WHEN** `system:configured` Redis key is `"true"`
- **AND** a user navigates to `GET /setup`
- **THEN** the system SHALL redirect to `/` (HTTP 302)

#### Scenario: Error shown after failed submission

- **WHEN** `GET /setup?error=<message>` is requested
- **THEN** the page SHALL display the error message

---

### Requirement: Setup wizard form submits initial configuration

The system SHALL accept `POST /setup` with at minimum: site name and initial admin username/password. Upon successful submission, the system MUST create a `SystemConfig` document, create the admin `User` document, set Redis `system:configured = "true"`, and redirect to `/`. Upon failure, the system SHALL redirect to `GET /setup?error=<message>` (HTTP 302).

#### Scenario: Successful setup submission

- **WHEN** the administrator submits a valid setup form with site name, admin username, and admin password
- **THEN** `SystemConfig` MUST be persisted in MongoDB
- **AND** an admin `User` MUST be created with full system admin permissions
- **AND** Redis `system:configured` MUST be set to `"true"`
- **AND** the response MUST redirect to `/` (HTTP 302)

#### Scenario: Duplicate setup attempt via API

- **WHEN** `POST /setup` is called after setup is already complete
- **THEN** the system SHALL return HTTP 409 Conflict

#### Scenario: Setup submission failure redirects with error

- **WHEN** `POST /setup` fails due to a processing error while not yet configured
- **THEN** the system SHALL redirect to `GET /setup?error=<message>` (HTTP 302)
