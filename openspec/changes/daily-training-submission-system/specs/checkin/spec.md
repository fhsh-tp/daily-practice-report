## ADDED Requirements

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

### Requirement: Global check-in schedule

Teachers SHALL be able to configure a global check-in schedule per class. The schedule MUST specify: active days of the week (list of weekday integers 0-6) and a default time window (start time, end time, or null for all-day).

#### Scenario: Check-in disabled on excluded weekday

- **WHEN** a student attempts to check in on a weekday not in the active days list
- **THEN** the system SHALL reject the check-in with a message indicating check-in is not available today

#### Scenario: All-day window allows any time

- **WHEN** the global schedule has a null time window for the current weekday
- **THEN** the system SHALL accept check-ins at any time during that day

### Requirement: Per-day check-in override

Teachers SHALL be able to create a per-day override for a specific calendar date. An override MUST specify active status (enabled/disabled), and optionally a custom time window. The override SHALL take precedence over the global schedule for that specific date.

#### Scenario: Override disables check-in on a normally active day

- **WHEN** an override sets active=false for today
- **THEN** all student check-in attempts SHALL be rejected regardless of the global schedule

#### Scenario: Override extends check-in window

- **WHEN** an override sets a longer time window than the global default for today
- **THEN** students SHALL be able to check in during the extended window

### Requirement: Check-in status visibility

Students SHALL be able to see whether check-in is currently open, their check-in status for today, and the closing time of the current window.

#### Scenario: Check-in status shown on dashboard

- **WHEN** a student views their dashboard
- **THEN** the system SHALL display check-in open/closed status and, if open, the closing time
