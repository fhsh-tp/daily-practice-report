## ADDED Requirements

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

---

### Requirement: Badge award date rendered correctly in HTML templates

When rendering `BadgeAward.awarded_at` in a Jinja2 template, the value SHALL be formatted using `.strftime('%Y-%m-%d')` rather than string slicing. The `awarded_at` field is a Python `datetime` object and does not support subscript access.

#### Scenario: Badge date displays correctly in badges page

- **WHEN** a student views the badges page
- **THEN** each badge SHALL display the award date in `YYYY-MM-DD` format without server errors

## MODIFIED Requirements

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
