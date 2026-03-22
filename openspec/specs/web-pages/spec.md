## ADDED Requirements

### Requirement: Student dashboard shows today's tasks across all classes with search

The student dashboard page SHALL display one task card per class the student belongs to, representing today's assigned task (if any). The page SHALL include a search input that filters task cards in real time by task name, class name, or teacher display name. Filtering SHALL be client-side with no additional API calls.

#### Scenario: Dashboard shows today's task for each enrolled class

- **WHEN** a student views their dashboard
- **THEN** the page SHALL render one task card per class showing the class name, today's task name, and submit status (submitted / not submitted)

#### Scenario: Student searches tasks by task name

- **WHEN** a student types a query into the search input
- **THEN** the page SHALL immediately hide task cards whose task name, class name, and teacher name do not match the query (case-insensitive)

#### Scenario: No tasks today shows empty state per class

- **WHEN** a class has no task assigned for today
- **THEN** the task card for that class SHALL indicate "今日無任務" and SHALL remain searchable by class name

### Requirement: Student sidebar shows class navigation

The shared sidebar SHALL render a "我的班級" section for authenticated students (non-teacher, non-admin users). Each class the student belongs to SHALL appear as a collapsible nav entry. When expanded, each class SHALL expose links to its task history and leaderboard pages.

#### Scenario: Student sidebar lists enrolled classes

- **WHEN** an authenticated student views any page
- **THEN** the sidebar SHALL display a "我的班級" section listing each class they belong to

#### Scenario: Class entry links to task history

- **WHEN** a student expands a class entry in the sidebar
- **THEN** the entry SHALL include a link to the class-specific task history page

### Requirement: Create class button works from any page

The "新增班級" button in the teacher sidebar SHALL navigate to `GET /pages/dashboard?create_class=1` on any page. The dashboard SHALL detect the `create_class=1` query parameter and automatically open the create-class modal on page load.

#### Scenario: Create class button navigates to dashboard with param

- **WHEN** a teacher clicks "新增班級" from any page other than the dashboard
- **THEN** the browser SHALL navigate to `GET /pages/dashboard?create_class=1`

#### Scenario: Dashboard opens modal when param present

- **WHEN** the dashboard loads with `?create_class=1` in the URL
- **THEN** the create-class modal SHALL open automatically without further user interaction

## ADDED Requirements

### Requirement: Student dashboard layout

The student dashboard SHALL NOT display inline class cards with embedded task information as the primary layout. Instead, the dashboard SHALL focus on today's task cards (one per class) with a search bar. Class navigation SHALL be provided through the sidebar's "我的班級" section. Statistical widgets (total points, badges, streak) SHALL remain on the dashboard.

#### Scenario: Dashboard shows task cards not class management cards

- **WHEN** a student views their dashboard
- **THEN** the page SHALL display task cards for today's assignments grouped by class
- **AND** the page SHALL NOT display the class management card format used previously (which embedded check-in status and teacher tools inline)

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

### Requirement: Student dashboard layout

The student dashboard SHALL NOT display inline class cards with embedded task information as the primary layout. Instead, the dashboard SHALL focus on today's task cards (one per class) with a search bar. Class navigation SHALL be provided through the sidebar's "我的班級" section. Statistical widgets (total points, badges, streak) SHALL remain on the dashboard.

#### Scenario: Dashboard shows task cards not class management cards

- **WHEN** a student views their dashboard
- **THEN** the page SHALL display task cards for today's assignments grouped by class
- **AND** the page SHALL NOT display the class management card format used previously (which embedded check-in status and teacher tools inline)