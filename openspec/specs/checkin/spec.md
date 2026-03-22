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