## ADDED Requirements

### Requirement: Teacher accesses attendance management from points manage page

The points management page (`/pages/teacher/classes/{class_id}/points`) SHALL include a link or navigation entry to the attendance management page (`/pages/teacher/classes/{class_id}/attendance`). The existing generic point deduction form SHALL NOT be the sole mechanism for handling check-in exceptions.

#### Scenario: Points manage page links to attendance management

- **WHEN** a teacher views the points management page
- **THEN** the page SHALL display a clearly labeled link or card navigating to the attendance management page for the same class

## Requirements


<!-- @trace
source: task-review-attendance-dashboard
updated: 2026-03-22
code:
  - src/templates/student/dashboard.html
  - src/gamification/points/models.py
  - src/templates/student/learning_history.html
  - src/tasks/checkin/models.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/models.py
  - src/templates/shared/base.html
  - src/templates/teacher/points_manage.html
  - src/templates/teacher/attendance_manage.html
  - src/templates/student/submit_task.html
  - src/templates/student/class_history.html
  - src/tasks/submissions/service.py
  - src/pages/router.py
  - src/main.py
  - src/tasks/submissions/router.py
  - src/templates/teacher/submission_review.html
  - src/templates/student/submission_rejection.html
  - src/community/feed/models.py
tests:
  - tests/test_submission_approval.py
  - tests/test_resubmission.py
  - tests/test_attendance_management.py
  - tests/test_pages.py
  - tests/test_submissions.py
-->

### Requirement: Teacher accesses attendance management from points manage page

The points management page (`/pages/teacher/classes/{class_id}/points`) SHALL include a link or navigation entry to the attendance management page (`/pages/teacher/classes/{class_id}/attendance`). The existing generic point deduction form SHALL NOT be the sole mechanism for handling check-in exceptions.

#### Scenario: Points manage page links to attendance management

- **WHEN** a teacher views the points management page
- **THEN** the page SHALL display a clearly labeled link or card navigating to the attendance management page for the same class
## ADDED Requirements

### Requirement: Check-in endpoint validates class membership

The system SHALL verify that the student is a member of the target class before recording a check-in. Non-members SHALL be rejected with HTTP 403.

#### Scenario: Non-member check-in rejected

- **WHEN** a student who is not a member of the class attempts to check in via `POST /classes/{class_id}/checkin` or `POST /classes/{class_id}/checkin/browser`
- **THEN** the system SHALL return HTTP 403 and SHALL NOT create a check-in record

#### Scenario: Member check-in proceeds normally

- **WHEN** a student who is a member of the class attempts to check in
- **THEN** the system SHALL proceed with check-in processing as normal

### Requirement: Checkin config endpoints validate class ownership

The check-in configuration endpoints (`POST /classes/{class_id}/checkin-config` and `POST /classes/{class_id}/checkin-overrides`) SHALL verify that the requesting user is either a teacher-member of the target class or holds the `MANAGE_ALL_CLASSES` permission. Users who hold `MANAGE_OWN_CLASS` but are not a teacher-member of the specific class SHALL be rejected with HTTP 403.

#### Scenario: Teacher of a different class cannot configure checkin

- **WHEN** a user with `MANAGE_OWN_CLASS` permission who is NOT a teacher-member of the target class attempts to configure its check-in settings
- **THEN** the system SHALL return HTTP 403

#### Scenario: Teacher of the class can configure checkin

- **WHEN** a user with `MANAGE_OWN_CLASS` permission who IS a teacher-member of the target class configures check-in settings
- **THEN** the system SHALL accept the request and update the configuration

#### Scenario: Global class manager can configure any class checkin

- **WHEN** a user with `MANAGE_ALL_CLASSES` permission configures check-in settings for any class
- **THEN** the system SHALL accept the request regardless of class membership

<!-- @trace
source: security-audit-fixes
updated: 2026-03-23
code:
  - src/tasks/checkin/service.py
  - src/tasks/checkin/router.py
tests:
  - tests/test_security_audit.py
-->
