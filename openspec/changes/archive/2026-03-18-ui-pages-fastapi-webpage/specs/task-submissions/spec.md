## ADDED Requirements

### Requirement: Student task submission HTML page

The system SHALL serve a task submission form page at `GET /pages/student/classes/{class_id}/submit`. The page SHALL require authentication. It SHALL display the current day's task template fields and allow the student to submit. If an `error` query parameter is present, the page SHALL display it.

#### Scenario: Submit page shows today's template

- **WHEN** an authenticated student navigates to `GET /pages/student/classes/{class_id}/submit`
- **THEN** the system SHALL display an HTML form with all fields from today's assigned template for that class

#### Scenario: Submit page shown with error

- **WHEN** `GET /pages/student/classes/{class_id}/submit?error=<message>` is requested
- **THEN** the page SHALL display the error message

---

### Requirement: Student submission via browser form uses PRG pattern

The system SHALL accept task submission via `POST /classes/{class_id}/submit` with `application/x-www-form-urlencoded` body. On success, it SHALL redirect to `GET /pages/dashboard`. On failure, it SHALL redirect to `GET /pages/student/classes/{class_id}/submit?error=<message>`.

#### Scenario: Successful form submission

- **WHEN** a student submits a valid task form via the browser
- **THEN** the system SHALL persist the submission, trigger reward providers, and redirect to `GET /pages/dashboard` (HTTP 302)

#### Scenario: Duplicate submission via form

- **WHEN** a student submits the form a second time for the same template-date
- **THEN** the system SHALL redirect to `GET /pages/student/classes/{class_id}/submit?error=今日已提交` (HTTP 302)
- **AND** SHALL NOT create a duplicate submission

#### Scenario: Validation error via form

- **WHEN** a student submits a form with a required field left empty
- **THEN** the system SHALL redirect to `GET /pages/student/classes/{class_id}/submit?error=<field_error>` (HTTP 302)
- **AND** SHALL NOT persist the submission
