## ADDED Requirements

### Requirement: Student sees point balance on dashboard

The dashboard page SHALL display the student's current total point balance. The value SHALL be computed server-side from all `PointTransaction` records for that student and passed into the template context as `stats.total_points`. If no transactions exist, the value SHALL be `0`.

#### Scenario: Dashboard shows correct total points

- **WHEN** a student views the dashboard
- **THEN** the "總積分" stat card displays their actual cumulative point balance
- **AND** the value reflects all completed check-ins and task submissions

### Requirement: Submission confirmation displays points earned

After a student successfully submits a task, the system SHALL display how many points were awarded for that submission. The points earned SHALL be shown in the success state of the submission page.

#### Scenario: Points shown after task submission

- **WHEN** a student submits a task and receives HTTP 201
- **THEN** the UI displays a message indicating points earned (e.g., "獲得 10 積分")
- **AND** the points value reflects the class `submission_points` configuration
