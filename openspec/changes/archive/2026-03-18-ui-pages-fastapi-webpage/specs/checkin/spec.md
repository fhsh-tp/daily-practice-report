## ADDED Requirements

### Requirement: Student performs daily check-in via browser form

The system SHALL accept check-in via `POST /classes/{class_id}/checkin` from browser form submissions. The endpoint SHALL redirect after processing (PRG pattern). On success or expected states (already checked in, window closed), it SHALL redirect to `GET /pages/dashboard`. On unexpected error, it SHALL redirect to `GET /pages/dashboard?error=<message>`.

#### Scenario: Successful check-in redirects to dashboard

- **WHEN** a student submits the check-in form and the check-in window is open
- **THEN** the system SHALL record the check-in and redirect to `GET /pages/dashboard` (HTTP 302)

#### Scenario: Already checked in redirects to dashboard

- **WHEN** a student who already checked in today submits the check-in form
- **THEN** the system SHALL redirect to `GET /pages/dashboard` (HTTP 302) without creating a duplicate record

#### Scenario: Check-in window closed redirects with error

- **WHEN** a student submits the check-in form outside the check-in window
- **THEN** the system SHALL redirect to `GET /pages/dashboard?error=簽到時間已關閉` (HTTP 302)
