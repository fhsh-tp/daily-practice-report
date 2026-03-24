## Requirements

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

---
### Requirement: Student sidebar shows class navigation

The shared sidebar SHALL render a "我的班級" section for authenticated students (non-teacher, non-admin users). Each class the student belongs to SHALL appear as a collapsible nav entry. When expanded, each class SHALL expose links to its task history and leaderboard pages.

#### Scenario: Student sidebar lists enrolled classes

- **WHEN** an authenticated student views any page
- **THEN** the sidebar SHALL display a "我的班級" section listing each class they belong to

#### Scenario: Class entry links to task history

- **WHEN** a student expands a class entry in the sidebar
- **THEN** the entry SHALL include a link to the class-specific task history page

---
### Requirement: Create class button works from any page

The "新增班級" button in the teacher sidebar SHALL navigate to `GET /pages/dashboard?create_class=1` on any page. The button SHALL display a single plus icon (SVG) followed by the text "新增班級" without any additional plus character in the text. The dashboard SHALL detect the `create_class=1` query parameter and automatically open the create-class modal on page load.

#### Scenario: Create class button navigates to dashboard with param

- **WHEN** a teacher clicks "新增班級" from any page other than the dashboard
- **THEN** the browser SHALL navigate to `GET /pages/dashboard?create_class=1`

#### Scenario: Dashboard opens modal when param present

- **WHEN** the dashboard loads with `?create_class=1` in the URL
- **THEN** the create-class modal SHALL open automatically without further user interaction

#### Scenario: Create class button shows single icon

- **WHEN** the teacher sidebar renders the "新增班級" button
- **THEN** the button SHALL display exactly one plus icon (the SVG) and the text "新增班級" without a full-width "＋" character prefix

---
### Requirement: Student dashboard layout

The student dashboard SHALL NOT display inline class cards with embedded task information as the primary layout. Instead, the dashboard SHALL focus on today's task cards (one per class) with a search bar. Class navigation SHALL be provided through the sidebar's "我的班級" section. Statistical widgets (total points, badges, streak) SHALL remain on the dashboard.

#### Scenario: Dashboard shows task cards not class management cards

- **WHEN** a student views their dashboard
- **THEN** the page SHALL display task cards for today's assignments grouped by class
- **AND** the page SHALL NOT display the class management card format used previously (which embedded check-in status and teacher tools inline)


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

---
### Requirement: Teacher sidebar uses class dropdown selector with search

The teacher sidebar SHALL replace the expandable class list with a dropdown class selector. The selector SHALL display the currently active class name with a dropdown indicator. Clicking the selector SHALL expand a dropdown panel containing a search input and a scrollable list of all non-archived classes the teacher manages. Selecting a class SHALL navigate to that class's hub page. The search input SHALL filter classes by name in real time (client-side).

#### Scenario: Teacher sees class selector in sidebar

- **WHEN** a teacher views any page with the teacher sidebar
- **THEN** the sidebar SHALL display a dropdown selector showing the currently active class name under the "班級管理" section label

#### Scenario: Teacher expands class selector

- **WHEN** a teacher clicks the class dropdown selector
- **THEN** the sidebar SHALL display a dropdown panel with a search input at the top and a scrollable list of all non-archived classes

#### Scenario: Teacher searches classes

- **WHEN** a teacher types into the class selector search input
- **THEN** the class list SHALL immediately filter to show only classes whose name contains the search query (case-insensitive)

#### Scenario: Teacher selects a different class

- **WHEN** a teacher clicks a class in the dropdown list
- **THEN** the browser SHALL navigate to that class's hub page at `/pages/teacher/class/{class_id}`

#### Scenario: Active class shows expanded tool links

- **WHEN** a class is selected (active) in the sidebar
- **THEN** the sidebar SHALL display indented tool links below the class selector: 成員管理, 任務模板, 任務審查, 簽到設定, 出席紀錄, 排行榜, 積分管理

---
### Requirement: Teacher sidebar includes submission review and attendance links

The teacher sidebar's class tool links SHALL include "任務審查" linking to `/pages/teacher/class/{class_id}/submissions` and "出席紀錄" linking to `/pages/teacher/classes/{class_id}/attendance` in addition to the existing tool links.

#### Scenario: Sidebar shows submission review link

- **WHEN** a teacher views the sidebar with an active class
- **THEN** the class tool links SHALL include "任務審查" that navigates to the submission review page

#### Scenario: Sidebar shows attendance link

- **WHEN** a teacher views the sidebar with an active class
- **THEN** the class tool links SHALL include "出席紀錄" that navigates to the attendance management page

---
### Requirement: Sidebar merges admin sections into unified platform management

The sidebar SHALL merge the "管理工具" and "管理員" sections into a single "平台管理" section. The section SHALL appear when the user has `MANAGE_USERS`, `MANAGE_ALL_CLASSES`, or `WRITE_SYSTEM` permission. Individual items SHALL be rendered based on the user's specific permissions: "使用者管理" (requires `MANAGE_USERS`), "班級管理" (requires `MANAGE_ALL_CLASSES`), "系統管理" (requires `WRITE_SYSTEM`).

#### Scenario: Full admin sees all platform management items

- **WHEN** a user with `MANAGE_USERS`, `MANAGE_ALL_CLASSES`, and `WRITE_SYSTEM` views the sidebar
- **THEN** the sidebar SHALL display a single "平台管理" section containing "使用者管理", "班級管理", and "系統管理"

#### Scenario: Teacher with no admin permissions sees no platform management

- **WHEN** a user with only `MANAGE_OWN_CLASS` and `MANAGE_TASKS` views the sidebar
- **THEN** the sidebar SHALL NOT display the "平台管理" section

---
### Requirement: All teacher and admin pages display breadcrumb navigation

Every teacher page SHALL display a breadcrumb navigation above the page title showing the path: "儀表板 > {class_name} > {current_page}". Admin pages SHALL display: "平台管理 > {current_page}". Breadcrumb items SHALL be clickable links to their respective pages.

#### Scenario: Class hub shows breadcrumb

- **WHEN** a teacher views the class hub for class "test1"
- **THEN** the page SHALL display breadcrumb: "儀表板 > test1" where "儀表板" links to the dashboard

#### Scenario: Nested teacher page shows full breadcrumb

- **WHEN** a teacher views the members page for class "test1"
- **THEN** the page SHALL display breadcrumb: "儀表板 > test1 > 成員管理" where each segment links to its respective page
