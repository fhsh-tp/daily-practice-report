## MODIFIED Requirements

### Requirement: Teacher assigns template to a date

Teachers SHALL assign task templates to dates using the schedule rule system (`TaskScheduleRule`) rather than single-date assignment. The assignment UI SHALL present four scheduling modes: once, range (every day), range with weekday filter, and open-ended. All modes SHALL create `TaskAssignment` records through the `expand_schedule_rule()` service function. The previous single-date `AssignTemplateRequest` API endpoint SHALL continue to function for backward compatibility.

#### Scenario: Teacher assigns template using range mode with weekday filter

- **WHEN** a teacher selects "日期區間 + 星期篩選" mode, sets start/end dates, checks weekdays [0,1,3,4], and submits
- **THEN** `POST /classes/{class_id}/schedule-rules` is called with the rule parameters
- **AND** `TaskAssignment` records are created for all qualifying dates in the range
- **AND** the teacher is redirected to the templates list with a success message

#### Scenario: Template assign page shows four scheduling modes

- **WHEN** a teacher opens the schedule assignment page for a template
- **THEN** the page displays a mode selector with options: 一次性、日期區間、星期篩選、開放式
- **AND** the relevant date/weekday inputs update based on the selected mode
