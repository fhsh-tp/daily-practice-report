## ADDED Requirements

### Requirement: Teacher points management HTML page

The system SHALL serve a points management page at `GET /pages/classes/{class_id}/points`. The page SHALL require `MANAGE_TASKS` permission. It SHALL display all students' current point balances and the class point configuration.

#### Scenario: Teacher views class points page

- **WHEN** a user with `MANAGE_TASKS` permission navigates to `GET /pages/classes/{class_id}/points`
- **THEN** the system SHALL render an HTML page showing all students' point balances and the current checkin/submission point config for that class
