## ADDED Requirements

### Requirement: Class stores optional Discord Webhook URL

The Class model SHALL include an optional field `discord_webhook_url` (string, nullable) for storing the class Discord integration endpoint.

#### Scenario: New class has null webhook URL

- **WHEN** a new class is created
- **THEN** `discord_webhook_url` SHALL default to null

#### Scenario: Webhook URL is only visible to class managers

- **WHEN** a student views class information
- **THEN** the `discord_webhook_url` SHALL NOT be exposed in any student-facing API response or template
