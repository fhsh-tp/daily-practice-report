## MODIFIED Requirements

### Requirement: Student performs daily check-in via browser form

The system SHALL accept check-in via `POST /classes/{class_id}/checkin/browser` from browser form submissions. The endpoint SHALL redirect after processing (PRG pattern). The redirect behavior SHALL differ based on outcome:

- **Success**: Record created → redirect to `GET /pages/dashboard` (HTTP 302, no error parameter)
- **Already checked in**: Duplicate attempt → redirect to `GET /pages/dashboard` (HTTP 302, **no error parameter**)
- **Window closed or other error**: → redirect to `GET /pages/dashboard?error=<message>` (HTTP 302, with error parameter)

The "already checked in" state MUST NOT be treated as an error condition in the redirect. It is an expected idempotent state.

#### Scenario: Successful check-in redirects to dashboard

- **WHEN** a student submits the check-in form and the check-in window is open
- **THEN** the system SHALL record the check-in and redirect to `GET /pages/dashboard` (HTTP 302)
- **AND** the redirect SHALL NOT include an `error` query parameter

#### Scenario: Already checked in redirects to dashboard without error

- **WHEN** a student who already checked in today submits the check-in form
- **THEN** the system SHALL redirect to `GET /pages/dashboard` (HTTP 302) without creating a duplicate record
- **AND** the redirect SHALL NOT include an `error` query parameter

#### Scenario: Check-in window closed redirects with error

- **WHEN** a student submits the check-in form outside the check-in window
- **THEN** the system SHALL redirect to `GET /pages/dashboard?error=簽到時間已關閉` (HTTP 302)
- **AND** the redirect SHALL include the `error` query parameter with a descriptive message
