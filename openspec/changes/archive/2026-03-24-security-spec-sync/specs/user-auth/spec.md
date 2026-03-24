## ADDED Requirements

### Requirement: JWT secret safety check at startup

The system SHALL check whether the `SESSION_SECRET` environment variable is set to the default development value at application startup. If the default value is detected, the system SHALL log a WARNING to alert operators that the secret must be changed before production use.

#### Scenario: Default secret triggers warning log

- **WHEN** the application starts with `SESSION_SECRET` equal to the default development value
- **THEN** the system SHALL emit a WARNING-level log message indicating that the default secret is in use and must be changed in production

#### Scenario: Custom secret produces no warning

- **WHEN** the application starts with a non-default `SESSION_SECRET` value
- **THEN** the system SHALL NOT emit a warning related to the JWT secret

<!-- @trace
source: security-audit-fixes
updated: 2026-03-23
code:
  - src/core/auth/jwt.py
tests:
  - tests/test_security_audit.py
-->
