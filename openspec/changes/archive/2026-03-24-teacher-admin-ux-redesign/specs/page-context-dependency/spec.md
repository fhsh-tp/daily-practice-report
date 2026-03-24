## ADDED Requirements

### Requirement: Shared page context dependency injects sidebar variables

The system SHALL provide a shared async FastAPI dependency `get_page_context()` in `src/shared/page_context.py` that computes and returns all sidebar-required template context variables. The dependency SHALL return a dictionary containing: `can_manage_class` (bool), `can_manage_all_classes` (bool), `can_manage_tasks` (bool), `can_manage_users` (bool), `is_sys_admin` (bool), and `classes` (list of dicts with `class_id` and `class_name` for non-archived classes the user manages).

#### Scenario: Teacher user receives full sidebar context

- **WHEN** a route handler invokes `get_page_context()` for a user with `MANAGE_OWN_CLASS` and `MANAGE_TASKS` permissions
- **THEN** the returned dictionary SHALL contain `can_manage_class: True`, `can_manage_tasks: True`, and `classes` SHALL list all non-archived classes where the user has a `teacher` membership

#### Scenario: Student user receives empty management context

- **WHEN** a route handler invokes `get_page_context()` for a user with only student permissions
- **THEN** the returned dictionary SHALL contain `can_manage_class: False`, `can_manage_tasks: False`, `can_manage_users: False`, `is_sys_admin: False`, and `classes` SHALL list all non-archived classes where the user is a member

#### Scenario: Admin user receives admin flags

- **WHEN** a route handler invokes `get_page_context()` for a user with `MANAGE_USERS` and `WRITE_SYSTEM` permissions
- **THEN** the returned dictionary SHALL contain `can_manage_users: True` and `is_sys_admin: True`

### Requirement: All teacher and admin page handlers use shared page context

Every route handler that renders a page extending `shared/base.html` for teacher or admin views SHALL use `get_page_context()` via `Depends()` and SHALL merge the returned dictionary into its template context. No teacher or admin page handler SHALL manually compute sidebar permission variables.

#### Scenario: Class members page includes sidebar context

- **WHEN** a teacher navigates to the class members page at `/pages/teacher/classes/{class_id}/members`
- **THEN** the page SHALL render the teacher sidebar with class navigation, not the student sidebar

#### Scenario: Submission review page includes sidebar context

- **WHEN** a teacher navigates to the submission review page at `/pages/teacher/class/{class_id}/submissions`
- **THEN** the page SHALL render the teacher sidebar with the current class expanded and all tool links visible

#### Scenario: All teacher pages render consistent sidebar

- **WHEN** a teacher navigates to any teacher page (class hub, members, templates, submissions, checkin config, attendance, points, leaderboard)
- **THEN** the sidebar SHALL display identical navigation structure with the correct active class highlighted
