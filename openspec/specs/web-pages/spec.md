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

The system SHALL serve a dashboard page at `GET /pages/dashboard`. The page SHALL require authentication. The page content SHALL vary based on the authenticated user's permissions. The dashboard layout SHALL consist of three sections rendered in order:

1. **Widget Grid** — a row of stat cards showing the current user's total points, badge count, consecutive-day streak, and total submission count. When the viewer has `MANAGE_CLASS` permission, the Widget Grid SHALL instead show class-aggregate statistics: total enrolled students, today's checkin count, and today's submission count.
2. **Class Card Grid** — one card per enrolled (or managed) class. Each card SHALL display the class name, today's checkin and submission status, and primary action links (checkin, submit task). Teacher cards SHALL additionally include a teacher toolbar row with links to templates, points management, and member list.
3. **Activity Feed** — a chronological timeline of the authenticated user's recent activity (checkins, submissions, badge awards), limited to the 20 most recent entries.

#### Scenario: Student views dashboard

- **WHEN** a student navigates to `GET /pages/dashboard`
- **THEN** the page SHALL display the Widget Grid with the student's personal stats, the Class Card Grid with enrolled classes, and the Activity Feed with their recent events

#### Scenario: Teacher views dashboard

- **WHEN** a user with `MANAGE_CLASS` permission navigates to `GET /pages/dashboard`
- **THEN** the Widget Grid SHALL show class-aggregate statistics and each class card SHALL include a teacher toolbar with management links

#### Scenario: Error message shown on dashboard

- **WHEN** `GET /pages/dashboard?error=<message>` is requested by an authenticated user
- **THEN** the page SHALL display the error message


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