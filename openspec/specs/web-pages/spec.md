# web-pages Specification

## Purpose

Defines the HTML page layer of the application: shared template infrastructure (WebPage singleton), page routes, page-aware authentication, and the POST-Redirect-GET (PRG) pattern used by all form submissions.

## Requirements

### Requirement: WebPage singleton provides shared template rendering

The system SHALL maintain a single `WebPage` instance (from `fastapi-webpage`) in `shared/webpage.py`. All page handlers MUST use this singleton instead of instantiating `Jinja2Templates` directly. The singleton SHALL expose `webpage_context` for global template variables.

#### Scenario: site_name available in all templates

- **WHEN** the application lifespan completes and a `SystemConfig` document exists
- **THEN** all template renders SHALL have `{{ webpage.site_name }}` available with the configured site name

#### Scenario: Multiple routers share one instance

- **WHEN** two different routers render templates
- **THEN** both SHALL use the same `WebPage` instance and receive the same `webpage_context`

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->


<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: Login page renders HTML login form

The system SHALL serve an HTML login form at `GET /pages/login`. The page SHALL NOT require authentication. If an `error` query parameter is present, the page SHALL display it.

#### Scenario: Login page shown to unauthenticated user

- **WHEN** an unauthenticated user navigates to `GET /pages/login`
- **THEN** the system SHALL return an HTML page containing a username/password form

#### Scenario: Error message displayed after failed login

- **WHEN** `GET /pages/login?error=帳號或密碼錯誤` is requested
- **THEN** the page SHALL display the error message

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->


<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: Dashboard is the unified authenticated entry point

The system SHALL serve a dashboard page at `GET /pages/dashboard`. The page SHALL require authentication. The `dashboard_page` route handler SHALL provide the following context variables to the template:

**Student context (when user does NOT have MANAGE_CLASS permission):**
- `stats.total_points`: total point balance from `get_balance(user_id)`
- `stats.badge_count`: count of `BadgeAward` documents for the user
- `stats.submission_count`: count of `TaskSubmission` documents for the user
- `stats.streak_days`: consecutive check-in streak (SHALL default to `0` when streak computation is not yet implemented)
- `badges`: list of the user's most recent badge awards (up to 10), from `get_student_badges(user_id)`
- `recent_activities`: list of up to 20 recent activity entries merged from `CheckinRecord`, `TaskSubmission`, and `BadgeAward`, sorted by timestamp descending
- `classes`: list of class status objects, each containing at minimum `class_id`, `class_name`, `is_archived`, `checkin_open`, `already_checked_in`, `closes_at`, `today_template`

**Teacher/manager context (when user has MANAGE_CLASS permission):**
- All of the above
- Each class status object SHALL additionally include `member_count`: the number of `ClassMembership` records for that class

#### Scenario: Student views dashboard with full stats

- **WHEN** a student navigates to `GET /pages/dashboard`
- **THEN** the template context SHALL include `stats.total_points`, `stats.badge_count`, `stats.submission_count`, `stats.streak_days`, `badges`, `recent_activities`, and `classes`

#### Scenario: Teacher views dashboard with member counts

- **WHEN** a user with `MANAGE_CLASS` permission navigates to `GET /pages/dashboard`
- **THEN** each entry in `classes` SHALL include a `member_count` field with the number of enrolled students

#### Scenario: Error message shown on dashboard

- **WHEN** `GET /pages/dashboard?error=<message>` is requested by an authenticated user
- **THEN** the page SHALL display the error message


<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
code:
  - src/templates/teacher/template_form.html
  - src/pages/router.py
  - uv.lock
  - src/templates/admin/index.html
  - src/templates/teacher/templates_list.html
  - src/templates/teacher/template_assign.html
  - src/templates/login.html
  - src/templates/admin/users_list.html
  - src/templates/student/submit_task.html
  - src/gamification/badges/router.py
  - src/templates/community/feed.html
  - src/templates/student/dashboard.html
  - src/community/feed/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/tasks/checkin/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/badges.html
  - src/templates/admin/classes_list.html
  - src/templates/teacher/points_manage.html
  - src/templates/admin/system_settings.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_checkin_config_page.py
  - tests/test_ui_polish.py
  - tests/test_setup_wizard.py
  - tests/test_admin_pages.py
  - tests/test_pages.py
  - tests/test_task_scheduling.py
  - tests/test_dashboard_and_page_bugs.py
-->

---
### Requirement: Dashboard displays gamified badge strip

The dashboard page SHALL render a horizontal scrollable badge strip below the Widget Grid, showing the user's most recently earned badges (up to 10). Each badge item SHALL display the badge icon and name. Unearned badge slots SHALL be shown in a visually muted locked state to communicate progress.

#### Scenario: Earned badges shown in strip

- **WHEN** a student has earned at least one badge
- **THEN** the badge strip SHALL show those badges with full color and label

#### Scenario: Empty badge strip hidden

- **WHEN** a student has earned no badges
- **THEN** the badge strip section SHALL not render

<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
-->


<!-- @trace
source: ui-redesign-academic-pro
updated: 2026-03-19
code:
  - src/templates/community/leaderboard.html
  - src/templates/login.html
  - src/templates/setup.html
  - src/templates/teacher/template_form.html
  - src/templates/student/badges.html
  - src/templates/student/dashboard.html
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/templates/teacher/templates_list.html
  - src/templates/shared/base.html
  - src/templates/student/submit_task.html
-->

---
### Requirement: Root route redirects based on authentication state

`GET /` SHALL redirect to `GET /pages/dashboard` if the user is authenticated, or to `GET /pages/login` if not.

#### Scenario: Authenticated user hits root

- **WHEN** an authenticated user navigates to `/`
- **THEN** the system SHALL redirect to `/pages/dashboard` (HTTP 302)

#### Scenario: Unauthenticated user hits root

- **WHEN** an unauthenticated user navigates to `/`
- **THEN** the system SHALL redirect to `/pages/login` (HTTP 302)

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->


<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: Page-aware auth dependency redirects to login

A page-specific authentication dependency SHALL redirect unauthenticated requests to `GET /pages/login` with a `next` query parameter instead of returning HTTP 401.

#### Scenario: Unauthenticated page request redirected to login

- **WHEN** an unauthenticated user accesses a protected page
- **THEN** the system SHALL redirect to `/pages/login?next=<original_path>` (HTTP 302)

#### Scenario: Authenticated request proceeds normally

- **WHEN** a user with a valid session accesses a protected page
- **THEN** the system SHALL serve the page normally

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->


<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: All form POSTs use POST-Redirect-GET pattern

Every HTML form submission endpoint SHALL redirect after processing. On success, it SHALL redirect to the appropriate page. On failure, it SHALL redirect back to the originating page with an `error` query parameter.

#### Scenario: Successful form POST redirects to target page

- **WHEN** a form POST succeeds
- **THEN** the system SHALL respond with an HTTP 302 redirect to the designated success page

#### Scenario: Failed form POST redirects with error

- **WHEN** a form POST fails due to validation or business logic
- **THEN** the system SHALL redirect to the originating GET page with `?error=<message>` (HTTP 302)
- **AND** the browser SHALL NOT re-submit on refresh

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
-->

<!-- @trace
source: ui-pages-fastapi-webpage
updated: 2026-03-18
code:
  - src/gamification/points/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/dashboard.html
  - src/templates/login.html
  - src/core/auth/permissions.py
  - src/main.py
  - src/pages/deps.py
  - src/gamification/badges/router.py
  - src/templates/shared/base.html
  - src/tasks/templates/router.py
  - src/shared/webpage.py
  - src/tasks/checkin/router.py
  - src/tasks/submissions/router.py
  - src/core/auth/router.py
  - src/core/system/router.py
  - src/pages/__init__.py
  - src/templates/student/submit_task.html
  - src/pages/router.py
  - src/community/feed/router.py
tests:
  - tests/test_pages.py
-->

---
### Requirement: Admin page group requires admin-level permission

The system SHALL register a set of routes under `/pages/admin/*` in the pages router. Every route in this group MUST use a dependency that verifies the authenticated user holds at least `MANAGE_USERS` OR `WRITE_SYSTEM`. Any route within the group MAY add further per-route permission checks beyond this baseline.

#### Scenario: Base admin guard allows user with MANAGE_USERS

- **WHEN** a user with `MANAGE_USERS` accesses any `/pages/admin/*` route
- **THEN** the route handler SHALL execute and return the page

#### Scenario: Base admin guard allows user with WRITE_SYSTEM

- **WHEN** a user with `WRITE_SYSTEM` (but without `MANAGE_USERS`) accesses `/pages/admin/`
- **THEN** the route handler SHALL execute and return the overview page

#### Scenario: User without admin permissions receives 403

- **WHEN** a user holding only `STUDENT` permissions accesses any `/pages/admin/*` route
- **THEN** the system SHALL return HTTP 403


<!-- @trace
source: admin-management-panel
updated: 2026-03-19
code:
  - src/templates/admin/index.html
  - src/templates/admin/layout.html
  - src/core/users/router.py
  - src/templates/admin/system_settings.html
  - src/templates/shared/base.html
  - src/templates/admin/users_list.html
  - src/core/system/router.py
  - src/core/auth/permissions.py
  - src/templates/admin/user_form.html
  - src/pages/router.py
tests:
  - tests/test_admin_permissions.py
  - tests/test_admin_system.py
  - tests/test_admin_users.py
  - tests/auth/test_permissions.py
  - tests/test_admin_pages.py
-->

---
### Requirement: Admin templates use a shared admin layout

The system SHALL provide a Jinja2 base template at `src/templates/admin/layout.html` that all admin pages extend. The layout MUST include the admin navigation bar described in the admin-panel spec. Admin templates MUST be placed under `src/templates/admin/`.

#### Scenario: Admin pages share consistent layout

- **WHEN** any admin page is rendered
- **THEN** the HTML MUST include the admin navigation bar from `admin/layout.html`

<!-- @trace
source: admin-management-panel
updated: 2026-03-19
code:
  - src/templates/admin/index.html
  - src/templates/admin/layout.html
  - src/core/users/router.py
  - src/templates/admin/system_settings.html
  - src/templates/shared/base.html
  - src/templates/admin/users_list.html
  - src/core/system/router.py
  - src/core/auth/permissions.py
  - src/templates/admin/user_form.html
  - src/pages/router.py
tests:
  - tests/test_admin_permissions.py
  - tests/test_admin_system.py
  - tests/test_admin_users.py
  - tests/auth/test_permissions.py
  - tests/test_admin_pages.py
-->

---
### Requirement: All page routes use page-aware auth dependency

Every route handler decorated with `@webpage.page()` SHALL use `get_page_user` as its authentication dependency. The `get_current_user` dependency MUST NOT be used in page route handlers because it returns HTTP 401 JSON for unauthenticated requests instead of redirecting to the login page.

#### Scenario: Unauthenticated user hits a page route using get_page_user

- **WHEN** an unauthenticated user accesses any `@webpage.page()` decorated route
- **THEN** the system SHALL redirect to `/pages/login?next=<original_path>` (HTTP 302)

#### Scenario: Badges page redirects unauthenticated users

- **WHEN** an unauthenticated user accesses `GET /pages/students/me/badges`
- **THEN** the system SHALL redirect to `/pages/login` (HTTP 302) with a `next` parameter

#### Scenario: Leaderboard page redirects unauthenticated users

- **WHEN** an unauthenticated user accesses `GET /pages/classes/{class_id}/leaderboard`
- **THEN** the system SHALL redirect to `/pages/login` (HTTP 302) with a `next` parameter

#### Scenario: Feed page redirects unauthenticated users

- **WHEN** an unauthenticated user accesses `GET /pages/classes/{class_id}/feed`
- **THEN** the system SHALL redirect to `/pages/login` (HTTP 302) with a `next` parameter

<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
-->


<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
code:
  - src/templates/teacher/template_form.html
  - src/pages/router.py
  - uv.lock
  - src/templates/admin/index.html
  - src/templates/teacher/templates_list.html
  - src/templates/teacher/template_assign.html
  - src/templates/login.html
  - src/templates/admin/users_list.html
  - src/templates/student/submit_task.html
  - src/gamification/badges/router.py
  - src/templates/community/feed.html
  - src/templates/student/dashboard.html
  - src/community/feed/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/tasks/checkin/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/badges.html
  - src/templates/admin/classes_list.html
  - src/templates/teacher/points_manage.html
  - src/templates/admin/system_settings.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_checkin_config_page.py
  - tests/test_ui_polish.py
  - tests/test_setup_wizard.py
  - tests/test_admin_pages.py
  - tests/test_pages.py
  - tests/test_task_scheduling.py
  - tests/test_dashboard_and_page_bugs.py
-->

---
### Requirement: Task submission page handles missing template gracefully

The task submission page at `GET /pages/student/classes/{class_id}/submit` SHALL handle the case where no task template is assigned for today. When `template is None`, the page SHALL render an informational message instead of attempting to render template fields.

#### Scenario: No template assigned for today

- **WHEN** a student accesses the submission page and no template is assigned for today
- **THEN** the page SHALL display an error message (e.g., "今日無任務模板")
- **AND** the template form fields SHALL NOT be rendered
- **AND** the page SHALL NOT raise a server error

#### Scenario: Template available — normal render

- **WHEN** a student accesses the submission page and a template is assigned for today
- **THEN** the page SHALL render all template fields for submission

<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
-->


<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
code:
  - src/templates/teacher/template_form.html
  - src/pages/router.py
  - uv.lock
  - src/templates/admin/index.html
  - src/templates/teacher/templates_list.html
  - src/templates/teacher/template_assign.html
  - src/templates/login.html
  - src/templates/admin/users_list.html
  - src/templates/student/submit_task.html
  - src/gamification/badges/router.py
  - src/templates/community/feed.html
  - src/templates/student/dashboard.html
  - src/community/feed/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/tasks/checkin/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/badges.html
  - src/templates/admin/classes_list.html
  - src/templates/teacher/points_manage.html
  - src/templates/admin/system_settings.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_checkin_config_page.py
  - tests/test_ui_polish.py
  - tests/test_setup_wizard.py
  - tests/test_admin_pages.py
  - tests/test_pages.py
  - tests/test_task_scheduling.py
  - tests/test_dashboard_and_page_bugs.py
-->

---
### Requirement: Badge award date rendered correctly in HTML templates

When rendering `BadgeAward.awarded_at` in a Jinja2 template, the value SHALL be formatted using `.strftime('%Y-%m-%d')` rather than string slicing. The `awarded_at` field is a Python `datetime` object and does not support subscript access.

#### Scenario: Badge date displays correctly in badges page

- **WHEN** a student views the badges page
- **THEN** each badge SHALL display the award date in `YYYY-MM-DD` format without server errors

<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
-->

<!-- @trace
source: fix-dashboard-and-page-bugs
updated: 2026-03-20
code:
  - src/templates/teacher/template_form.html
  - src/pages/router.py
  - uv.lock
  - src/templates/admin/index.html
  - src/templates/teacher/templates_list.html
  - src/templates/teacher/template_assign.html
  - src/templates/login.html
  - src/templates/admin/users_list.html
  - src/templates/student/submit_task.html
  - src/gamification/badges/router.py
  - src/templates/community/feed.html
  - src/templates/student/dashboard.html
  - src/community/feed/router.py
  - src/templates/admin/layout.html
  - src/templates/admin/user_form.html
  - src/tasks/checkin/router.py
  - src/gamification/leaderboard/router.py
  - src/templates/student/badges.html
  - src/templates/admin/classes_list.html
  - src/templates/teacher/points_manage.html
  - src/templates/admin/system_settings.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_checkin_config_page.py
  - tests/test_ui_polish.py
  - tests/test_setup_wizard.py
  - tests/test_admin_pages.py
  - tests/test_pages.py
  - tests/test_task_scheduling.py
  - tests/test_dashboard_and_page_bugs.py
-->

---
### Requirement: Student dashboard class card displays teacher name

The student dashboard class card SHALL display the owner (teacher) display name for each enrolled class.

#### Scenario: Class card shows teacher display name

- **WHEN** a student views the dashboard
- **THEN** each class card SHALL display the class owner's display name

#### Scenario: Teacher name fallback when owner not found

- **WHEN** the class owner account no longer exists
- **THEN** the class card SHALL display an empty string instead of raising an error

<!-- @trace
source: bug-fixes
updated: 2026-03-20
-->


<!-- @trace
source: bug-fixes
updated: 2026-03-20
code:
  - src/pages/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_bug_fixes.py
-->

---
### Requirement: Sidebar hides create-class shortcut for all-class managers

The sidebar SHALL NOT display the "建立第一個班級" shortcut when the current user has `can_manage_all_classes` permission, even if their class membership list is empty.

#### Scenario: System admin sees no create-class shortcut

- **WHEN** a user with `can_manage_all_classes` is logged in and has no class memberships
- **THEN** the sidebar SHALL NOT show the "建立第一個班級" link under 教師工具

#### Scenario: Teacher with no classes still sees create-class shortcut

- **WHEN** a user with `can_manage_class` but NOT `can_manage_all_classes` has no class memberships
- **THEN** the sidebar SHALL show the "建立第一個班級" link under 教師工具

<!-- @trace
source: bug-fixes
updated: 2026-03-20
-->


<!-- @trace
source: bug-fixes
updated: 2026-03-20
code:
  - src/pages/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_bug_fixes.py
-->

---
### Requirement: Class members page header renders without layout overflow

The class members page header SHALL display the page title and action buttons without wrapping or overflow at standard viewport widths.

#### Scenario: Header buttons are grouped

- **WHEN** the class members page is rendered at any standard viewport width
- **THEN** the action buttons (任務模板, 簽到設定) SHALL be contained in a single flex group and SHALL NOT wrap independently from each other

<!-- @trace
source: bug-fixes
updated: 2026-03-20
-->

<!-- @trace
source: bug-fixes
updated: 2026-03-20
code:
  - src/pages/router.py
  - src/templates/student/dashboard.html
  - src/templates/teacher/class_members.html
  - src/templates/shared/base.html
tests:
  - tests/test_bug_fixes.py
-->
---
### Requirement: Sidebar teacher section shows class list

The sidebar teacher section SHALL display a list of the teacher's classes as navigation items, each linking to the class hub page. When the current page is within a class hub, the sidebar SHALL show that class's tool links indented below the class name.

#### Scenario: Teacher sidebar lists classes

- **WHEN** a teacher with `can_manage_class` is logged in and has one or more classes
- **THEN** the sidebar SHALL display each class name as a link to its hub page under 教師工具

#### Scenario: Active class expands tool links

- **WHEN** the current URL contains a class_id matching one of the teacher's classes
- **THEN** the sidebar SHALL display indented tool links (成員管理, 任務模板, 簽到設定, 排行榜, 積分管理) under that class name

#### Scenario: Add new class button always visible

- **WHEN** a teacher with `can_manage_class` is logged in
- **THEN** the sidebar SHALL always display a "+ 新增班級" button in the 教師工具 section

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
-->

---
### Requirement: Class list supports tab switching between active and archived

The class list page SHALL provide two tabs — 運作中 and 已封存 — to separate active classes from archived ones.

#### Scenario: Default tab shows active classes

- **WHEN** a user opens the class list page
- **THEN** the 運作中 tab SHALL be active by default and SHALL show only non-archived classes

#### Scenario: Archived tab shows only archived classes

- **WHEN** a user clicks the 已封存 tab
- **THEN** only archived classes SHALL be displayed


<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
code:
  - src/templates/shared/base.html
  - src/templates/teacher/class_hub.html
  - src/pages/router.py
  - src/templates/admin/classes_list.html
tests:
  - tests/test_bug_fixes.py
  - tests/test_class_hub_page.py
-->

---
### Requirement: Class list supports search by name and teacher

Each class list tab SHALL provide a text input that filters classes by class name or teacher display name.

#### Scenario: Search filters by class name

- **WHEN** a user types a class name substring into the search input
- **THEN** only matching classes SHALL remain visible in the list

#### Scenario: Search filters by teacher name

- **WHEN** a user types a teacher display name substring into the search input
- **THEN** only classes whose owner display name matches SHALL remain visible

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
-->

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
code:
  - src/templates/shared/base.html
  - src/templates/teacher/class_hub.html
  - src/pages/router.py
  - src/templates/admin/classes_list.html
tests:
  - tests/test_bug_fixes.py
  - tests/test_class_hub_page.py
-->