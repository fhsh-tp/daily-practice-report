## ADDED Requirements

### Requirement: Discord webhook URL format validation

The system SHALL validate that a Discord webhook URL starts with `https://discord.com/api/webhooks/` or `https://discordapp.com/api/webhooks/` before saving it. URLs that do not match either prefix SHALL be rejected with HTTP 422.

#### Scenario: Invalid webhook URL rejected

- **WHEN** a user submits a webhook URL that does not start with `https://discord.com/api/webhooks/` or `https://discordapp.com/api/webhooks/`
- **THEN** the system SHALL return HTTP 422 and SHALL NOT persist the URL

#### Scenario: Valid discord.com webhook URL accepted

- **WHEN** a user submits a URL beginning with `https://discord.com/api/webhooks/`
- **THEN** the system SHALL accept and persist the URL

#### Scenario: Valid discordapp.com webhook URL accepted

- **WHEN** a user submits a URL beginning with `https://discordapp.com/api/webhooks/`
- **THEN** the system SHALL accept and persist the URL

#### Scenario: Empty URL accepted (disables webhook)

- **WHEN** a user submits an empty string as the webhook URL
- **THEN** the system SHALL accept it (effectively disabling the webhook)

<!-- @trace
source: security-audit-fixes
updated: 2026-03-23
code:
  - src/core/classes/router.py
tests:
  - tests/test_security_audit.py
-->
