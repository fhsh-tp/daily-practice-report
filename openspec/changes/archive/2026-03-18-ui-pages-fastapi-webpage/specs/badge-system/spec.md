## ADDED Requirements

### Requirement: Student badges HTML page

The system SHALL serve a badge display page at `GET /pages/students/me/badges`. The page SHALL require authentication. It SHALL display all badges earned by the authenticated student.

#### Scenario: Student views own badges page

- **WHEN** an authenticated student navigates to `GET /pages/students/me/badges`
- **THEN** the system SHALL render an HTML page displaying all badge awards for that student with badge name, icon, and award date
