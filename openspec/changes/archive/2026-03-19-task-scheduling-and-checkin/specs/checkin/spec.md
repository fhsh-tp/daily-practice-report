## ADDED Requirements

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

### Requirement: Teacher sets a single-day check-in override via web UI

Teachers SHALL be able to add a single-day override (activate or deactivate check-in for a specific date, with optional custom time window) through the check-in config page without leaving the browser.

#### Scenario: Teacher disables check-in for a specific date

- **WHEN** a teacher enters a date, sets `active: false`, and submits the override form on the config page
- **THEN** `POST /classes/{class_id}/checkin-overrides` is called with the date and `active: false`
- **AND** students cannot check in on that date even if the weekday is normally active
