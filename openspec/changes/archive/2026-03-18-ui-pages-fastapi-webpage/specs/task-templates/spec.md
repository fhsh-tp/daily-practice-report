## ADDED Requirements

### Requirement: Teacher template list HTML page

The system SHALL serve a task template management page at `GET /pages/teacher/classes/{class_id}/templates`. The page SHALL require `MANAGE_TASKS` permission. It SHALL display all templates for the class and provide links to create new templates.

#### Scenario: Teacher views template list

- **WHEN** a user with `MANAGE_TASKS` permission navigates to `GET /pages/teacher/classes/{class_id}/templates`
- **THEN** the system SHALL display all existing task templates for that class

#### Scenario: Unauthorized user rejected

- **WHEN** a user without `MANAGE_TASKS` permission accesses the templates list page
- **THEN** the system SHALL return HTTP 403

---

### Requirement: Teacher template form HTML page

The system SHALL serve a task template creation form at `GET /pages/teacher/classes/{class_id}/templates/new`. The page SHALL require `MANAGE_TASKS` permission. If an `error` query parameter is present, the page SHALL display it.

#### Scenario: Teacher views new template form

- **WHEN** a user with `MANAGE_TASKS` permission navigates to `GET /pages/teacher/classes/{class_id}/templates/new`
- **THEN** the system SHALL display an HTML form for creating a new task template

#### Scenario: Error shown after failed creation

- **WHEN** `GET /pages/teacher/classes/{class_id}/templates/new?error=<message>` is requested
- **THEN** the page SHALL display the error message
