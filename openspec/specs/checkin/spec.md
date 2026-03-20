# checkin Specification

## Purpose

TBD - created by archiving change 'daily-training-submission-system'. Update Purpose after archive.

## Requirements

### Requirement: Student check-in

Students SHALL be able to check in once per day when the check-in window is open. Duplicate check-ins on the same calendar day MUST be rejected. A successful check-in SHALL trigger the configured RewardProviders.

#### Scenario: Successful check-in within window

- **WHEN** a student clicks check-in and the current time is within the active window
- **THEN** the system SHALL record the check-in with a timestamp and trigger RewardProviders

#### Scenario: Check-in outside window rejected

- **WHEN** a student attempts to check in outside the active time window
- **THEN** the system SHALL display an informational message and SHALL NOT record the check-in

#### Scenario: Duplicate check-in rejected

- **WHEN** a student who already checked in today attempts to check in again
- **THEN** the system SHALL display a confirmation of their earlier check-in and SHALL NOT create a duplicate record


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Global check-in schedule

Teachers SHALL be able to configure a global check-in schedule per class. The schedule MUST specify: active days of the week (list of weekday integers 0-6) and a default time window (start time, end time, or null for all-day).

#### Scenario: Check-in disabled on excluded weekday

- **WHEN** a student attempts to check in on a weekday not in the active days list
- **THEN** the system SHALL reject the check-in with a message indicating check-in is not available today

#### Scenario: All-day window allows any time

- **WHEN** the global schedule has a null time window for the current weekday
- **THEN** the system SHALL accept check-ins at any time during that day


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Per-day check-in override

Teachers SHALL be able to create a per-day override for a specific calendar date. An override MUST specify active status (enabled/disabled), and optionally a custom time window. The override SHALL take precedence over the global schedule for that specific date.

#### Scenario: Override disables check-in on a normally active day

- **WHEN** an override sets active=false for today
- **THEN** all student check-in attempts SHALL be rejected regardless of the global schedule

#### Scenario: Override extends check-in window

- **WHEN** an override sets a longer time window than the global default for today
- **THEN** students SHALL be able to check in during the extended window


<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Check-in status visibility

Students SHALL be able to see whether check-in is currently open, their check-in status for today, and the closing time of the current window.

#### Scenario: Check-in status shown on dashboard

- **WHEN** a student views their dashboard
- **THEN** the system SHALL display check-in open/closed status and, if open, the closing time

<!-- @trace
source: daily-training-submission-system
updated: 2026-03-18
code:
  - src/gamification/__init__.py
  - src/core/classes/router.py
  - src/core/classes/service.py
  - scripts/__init__.py
  - src/extensions/protocols/reward.py
  - src/extensions/registry/__init__.py
  - src/extensions/protocols/__init__.py
  - src/tasks/checkin/router.py
  - src/templates/teacher/templates_list.html
  - LICENSE
  - uv.lock
  - src/core/users/__init__.py
  - src/gamification/points/service.py
  - src/templates/community/leaderboard.html
  - src/templates/shared/base.html
  - src/templates/teacher/template_form.html
  - src/core/auth/__init__.py
  - src/tasks/templates/models.py
  - src/templates/teacher/points_manage.html
  - src/templates/community/feed.html
  - src/community/feed/router.py
  - src/extensions/protocols/validator.py
  - src/shared/database.py
  - src/core/classes/__init__.py
  - src/tasks/checkin/service.py
  - src/tasks/templates/service.py
  - src/gamification/badges/__init__.py
  - src/gamification/points/models.py
  - src/tasks/checkin/__init__.py
  - src/community/feed/__init__.py
  - src/gamification/prizes/__init__.py
  - src/core/auth/deps.py
  - src/core/auth/jwt.py
  - src/extensions/deps.py
  - docker-compose.yml
  - src/community/__init__.py
  - src/core/auth/local_provider.py
  - src/core/classes/models.py
  - src/gamification/badges/router.py
  - src/gamification/leaderboard/router.py
  - scripts/migrations/__init__.py
  - src/gamification/points/router.py
  - src/main.py
  - src/extensions/registry/core.py
  - src/shared/__init__.py
  - src/tasks/checkin/models.py
  - src/core/users/router.py
  - pytest.ini
  - scripts/migrations/20260317_001_initial_indexes.py
  - src/tasks/submissions/__init__.py
  - src/community/feed/models.py
  - src/core/users/models.py
  - src/gamification/leaderboard/__init__.py
  - src/templates/student/badges.html
  - src/tasks/templates/router.py
  - src/gamification/points/providers.py
  - src/templates/student/dashboard.html
  - src/extensions/protocols/badge.py
  - src/tasks/templates/__init__.py
  - src/core/auth/password.py
  - src/extensions/__init__.py
  - src/gamification/points/__init__.py
  - pyproject.toml
  - src/extensions/protocols/auth.py
  - src/tasks/__init__.py
  - src/gamification/prizes/models.py
  - src/tasks/submissions/router.py
  - src/gamification/badges/service.py
  - src/tasks/submissions/models.py
  - src/gamification/prizes/router.py
  - src/templates/student/submit_task.html
  - scripts/migrate.py
  - src/core/__init__.py
  - src/gamification/badges/models.py
  - src/core/auth/router.py
  - src/tasks/submissions/service.py
  - src/gamification/badges/triggers.py
tests:
  - tests/test_checkin.py
  - tests/test_database.py
  - tests/test_extensions.py
  - tests/test_points.py
  - tests/test_task_templates.py
  - tests/test_classes.py
  - tests/test_submissions.py
  - tests/test_leaderboard.py
  - tests/test_feed.py
  - tests/test_prizes.py
  - tests/test_migration.py
  - tests/test_module_structure.py
  - tests/test_auth.py
  - tests/test_badges.py
  - scripts/migrations/test_example_migration.py
-->

---
### Requirement: Teacher configures check-in schedule via web UI

Teachers with `MANAGE_OWN_CLASS` or `MANAGE_ALL_CLASSES` permission SHALL be able to view and update their class's check-in schedule through a dedicated web page at `/pages/teacher/classes/{class_id}/checkin-config`. The page SHALL display the current `CheckinConfig` (active weekdays and time window) and allow the teacher to update it by submitting a form that calls `POST /classes/{class_id}/checkin-config`.

#### Scenario: Teacher views current check-in configuration

- **WHEN** a teacher navigates to `/pages/teacher/classes/{class_id}/checkin-config`
- **THEN** the page displays the currently configured active weekdays
- **AND** the page displays the currently configured window start and end times (if set)
- **AND** if no config exists, sensible defaults are shown (all weekdays, no time restriction)

#### Scenario: Teacher updates active weekdays

- **WHEN** a teacher selects weekdays and submits the configuration form
- **THEN** `POST /classes/{class_id}/checkin-config` is called with the selected weekdays
- **AND** the page reloads with a success message confirming the update

---
### Requirement: Teacher sets a single-day check-in override via web UI

Teachers SHALL be able to add a single-day override (activate or deactivate check-in for a specific date, with optional custom time window) through the check-in config page without leaving the browser.

#### Scenario: Teacher disables check-in for a specific date

- **WHEN** a teacher enters a date, sets `active: false`, and submits the override form on the config page
- **THEN** `POST /classes/{class_id}/checkin-overrides` is called with the date and `active: false`
- **AND** students cannot check in on that date even if the weekday is normally active

<!-- @trace
source: task-scheduling-and-checkin
updated: 2026-03-19
-->

---
### Requirement: Student performs daily check-in via browser form

The system SHALL accept check-in via `POST /classes/{class_id}/checkin/browser` from browser form submissions. The endpoint SHALL redirect after processing (PRG pattern). The redirect behavior SHALL differ based on outcome:

- **Success**: Record created → redirect to `GET /pages/dashboard` (HTTP 302, no error parameter)
- **Already checked in**: Duplicate attempt → redirect to `GET /pages/dashboard` (HTTP 302, **no error parameter**)
- **Window closed or other error**: → redirect to `GET /pages/dashboard?error=<message>` (HTTP 302, with error parameter)

The "already checked in" state MUST NOT be treated as an error condition in the redirect. It is an expected idempotent state.

#### Scenario: Successful check-in redirects to dashboard

- **WHEN** a student submits the check-in form and the check-in window is open
- **THEN** the system SHALL record the check-in and redirect to `GET /pages/dashboard` (HTTP 302)
- **AND** the redirect SHALL NOT include an `error` query parameter

#### Scenario: Already checked in redirects to dashboard without error

- **WHEN** a student who already checked in today submits the check-in form
- **THEN** the system SHALL redirect to `GET /pages/dashboard` (HTTP 302) without creating a duplicate record
- **AND** the redirect SHALL NOT include an `error` query parameter

#### Scenario: Check-in window closed redirects with error

- **WHEN** a student submits the check-in form outside the check-in window
- **THEN** the system SHALL redirect to `GET /pages/dashboard?error=簽到時間已關閉` (HTTP 302)
- **AND** the redirect SHALL include the `error` query parameter with a descriptive message

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