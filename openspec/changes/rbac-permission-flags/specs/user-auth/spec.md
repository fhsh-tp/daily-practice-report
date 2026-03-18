## MODIFIED Requirements

### Requirement: User registration by teacher

Users with `MANAGE_USERS` permission SHALL be able to create new accounts. Each account MUST include a unique username, hashed password, display name, permissions (as an integer from a Role Preset), and an optional `tags` list. The `role` field is removed.

#### Scenario: User admin creates student account

- **WHEN** a user with `MANAGE_USERS` permission submits a valid username, password, display name, and permissions value
- **THEN** the system SHALL create the account with the given permissions and return the new user ID

#### Scenario: Duplicate username rejected

- **WHEN** a user submits a username that already exists
- **THEN** the system SHALL return an error and SHALL NOT create a duplicate account

## ADDED Requirements

### Requirement: User model stores permissions as integer and supports tags

The `User` Beanie Document MUST store `permissions: int` instead of `role: str`. The document MUST also include `tags: list[str]` defaulting to an empty list. Both fields MUST be included in all user response schemas.

#### Scenario: User created with permissions preset

- **WHEN** a new user is created with a Role Preset value
- **THEN** the stored `permissions` field MUST equal the integer value of that preset

#### Scenario: User tags are updatable

- **WHEN** a user with `MANAGE_USERS` permission updates another user's tags
- **THEN** the `tags` field MUST be replaced with the new list

### Requirement: Migration maps existing role field to permissions integer

The system SHALL provide a migration script that converts existing `User` documents from `role: "student"` to `permissions = STUDENT` and `role: "teacher"` to `permissions = TEACHER`. The `role` field MUST be removed after migration.

#### Scenario: Student role migrated to permissions

- **WHEN** the migration script runs on a user with `role = "student"`
- **THEN** the user's document MUST have `permissions` set to the `STUDENT` preset integer and `role` field removed

#### Scenario: Teacher role migrated to permissions

- **WHEN** the migration script runs on a user with `role = "teacher"`
- **THEN** the user's document MUST have `permissions` set to the `TEACHER` preset integer and `role` field removed
