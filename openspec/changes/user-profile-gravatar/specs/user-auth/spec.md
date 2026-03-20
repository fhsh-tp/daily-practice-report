## ADDED Requirements

### Requirement: Email is required when creating a new user account

The system SHALL require a valid email address when creating a new user account.

#### Scenario: User creation fails without email

- **WHEN** an admin submits the create user form without an email address
- **THEN** the system SHALL return a validation error and SHALL NOT create the account

#### Scenario: User creation succeeds with email

- **WHEN** an admin submits the create user form with a valid email address
- **THEN** the system SHALL create the account with the provided email
