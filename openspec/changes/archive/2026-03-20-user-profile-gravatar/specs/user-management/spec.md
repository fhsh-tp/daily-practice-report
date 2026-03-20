## ADDED Requirements

### Requirement: Admin user creation form requires email

The admin user creation form SHALL mark the email field as required and SHALL validate presence before submission.

#### Scenario: Form shows email as required

- **WHEN** an admin opens the create user form
- **THEN** the email field SHALL be marked as required with a visual indicator

#### Scenario: Form submission blocked without email

- **WHEN** an admin submits the create user form with an empty email field
- **THEN** the form SHALL prevent submission and display an error message
