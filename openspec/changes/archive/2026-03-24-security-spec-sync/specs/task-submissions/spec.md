## ADDED Requirements

### Requirement: Submission endpoint validates class membership

The system SHALL verify that the submitting student is a member of the target class before processing a task submission. Non-members SHALL be rejected with HTTP 403.

#### Scenario: Non-member student submission rejected

- **WHEN** a student who is not a member of the class submits a task to `POST /classes/{class_id}/submissions`
- **THEN** the system SHALL return HTTP 403 and SHALL NOT create a submission record

#### Scenario: Member student submission proceeds normally

- **WHEN** a student who is a member of the class submits a task
- **THEN** the system SHALL proceed with the submission as normal

<!-- @trace
source: security-audit-fixes
updated: 2026-03-23
code:
  - src/tasks/submissions/service.py
  - src/tasks/submissions/router.py
tests:
  - tests/test_security_audit.py
-->
