## ADDED Requirements

### Requirement: Admin password minimum length

The setup wizard SHALL enforce a minimum password length of 8 characters for the initial admin account. Passwords shorter than 8 characters SHALL be rejected and the setup SHALL NOT proceed.

#### Scenario: Short password rejected

- **WHEN** a user submits an admin password shorter than 8 characters during setup
- **THEN** the system SHALL reject the request (HTTP 302 redirect back to the setup page with an error message) and SHALL NOT create the admin account

#### Scenario: Password of exactly 8 characters accepted

- **WHEN** a user submits an admin password of exactly 8 characters
- **THEN** the system SHALL accept the password and proceed with setup

<!-- @trace
source: security-audit-fixes
updated: 2026-03-23
code:
  - src/core/system/router.py
tests:
  - tests/test_security_audit.py
-->
