# submission-review Specification

## Purpose

TBD - created by syncing change 'submission-review-and-history'. Update Purpose after archive.

## Requirements

### Requirement: Teacher can view all student submissions for a class

The system SHALL provide a submission review page at `/pages/teacher/class/<class_id>/submissions` that lists all student submissions for the given class.

#### Scenario: Review page lists submissions

- **WHEN** a teacher with class management permission navigates to the review page
- **THEN** the page SHALL display all TaskSubmission records for that class, grouped by student

#### Scenario: Unauthorized access is rejected

- **WHEN** a user without class management permission accesses the review page
- **THEN** the system SHALL return 403 or redirect to dashboard


<!-- @trace
source: submission-review-and-history
updated: 2026-03-20
code:
  - src/gamification/points/router.py
  - src/templates/shared/base.html
  - src/gamification/points/service.py
  - src/templates/teacher/submission_review.html
  - src/templates/student/learning_history.html
  - src/tasks/submissions/models.py
  - src/tasks/submissions/router.py
tests:
  - tests/test_task_scheduling.py
  - tests/test_points.py
  - tests/test_submissions.py
  - tests/test_submission_review.py
  - tests/test_checkin_config_page.py
-->

---
### Requirement: Teacher can leave a comment on a submission

The system SHALL allow a teacher to add or update a comment on any submission via `POST /api/submissions/<submission_id>/comment`.

#### Scenario: Comment is saved

- **WHEN** a teacher submits a non-empty comment for a submission
- **THEN** the system SHALL save the comment to `teacher_comment` and record `reviewed_at` timestamp

#### Scenario: Comment can be overwritten

- **WHEN** a teacher submits a new comment for a submission that already has a comment
- **THEN** the old comment SHALL be replaced with the new one


<!-- @trace
source: submission-review-and-history
updated: 2026-03-20
code:
  - src/gamification/points/router.py
  - src/templates/shared/base.html
  - src/gamification/points/service.py
  - src/templates/teacher/submission_review.html
  - src/templates/student/learning_history.html
  - src/tasks/submissions/models.py
  - src/tasks/submissions/router.py
tests:
  - tests/test_task_scheduling.py
  - tests/test_points.py
  - tests/test_submissions.py
  - tests/test_submission_review.py
  - tests/test_checkin_config_page.py
-->

---
### Requirement: Teacher can deduct points from a student

The system SHALL allow a teacher to deduct points from a student via `POST /api/points/deduct`, specifying student_id, class_id, amount, and reason.

#### Scenario: Points are deducted

- **WHEN** a teacher submits a valid deduction request with a reason
- **THEN** the system SHALL create a `PointLedger` entry with `entry_type: "teacher_deduct"` and the student's balance SHALL decrease accordingly

#### Scenario: Deduction requires reason

- **WHEN** a teacher submits a deduction request without a reason
- **THEN** the system SHALL return a 422 error and SHALL NOT deduct any points

<!-- @trace
source: submission-review-and-history
updated: 2026-03-20
code:
  - src/gamification/points/router.py
  - src/templates/shared/base.html
  - src/gamification/points/service.py
  - src/templates/teacher/submission_review.html
  - src/templates/student/learning_history.html
  - src/tasks/submissions/models.py
  - src/tasks/submissions/router.py
tests:
  - tests/test_task_scheduling.py
  - tests/test_points.py
  - tests/test_submissions.py
  - tests/test_submission_review.py
  - tests/test_checkin_config_page.py
-->