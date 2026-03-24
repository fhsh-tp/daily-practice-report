## ADDED Requirements

### Requirement: Teacher views daily attendance list

Teachers with `MANAGE_OWN_CLASS` or `MANAGE_ALL_CLASSES` permission SHALL be able to view all class members' attendance status for any given date via a dedicated page at `GET /pages/teacher/classes/{class_id}/attendance`. The page SHALL display each student's name and whether they have a `CheckinRecord` for that date. Students with a `CheckinRecord` SHALL be shown as "checked in" by default. Students without a `CheckinRecord` SHALL be shown as "absent" by default.

#### Scenario: Teacher views attendance for a past date

- **WHEN** a teacher navigates to the attendance page and selects a date
- **THEN** the page SHALL display a list of all class members with their check-in status for that date
- **AND** students with a `CheckinRecord` SHALL be shown as "checked in"
- **AND** students without a `CheckinRecord` SHALL be shown as "absent"

#### Scenario: Page defaults to today's date

- **WHEN** a teacher navigates to the attendance page without specifying a date
- **THEN** the page SHALL default to today's date

### Requirement: Teacher marks absent student as late

Teachers SHALL be able to mark a student who has no `CheckinRecord` for a given date as "late" and award a partial point amount between 1 and the class's configured `checkin_points` (inclusive). This SHALL create an `AttendanceCorrection` record and a positive `PointTransaction` with `source_event: "checkin_manual_late"`.

#### Scenario: Teacher awards partial points for late arrival

- **WHEN** a teacher marks a student without a check-in record as "late" with a specified point amount
- **THEN** the system SHALL create an `AttendanceCorrection` record with `status: "late"` and the specified `partial_points`
- **AND** the system SHALL create a positive `PointTransaction` for the specified amount

#### Scenario: Partial points must be between 1 and checkin_points

- **WHEN** a teacher attempts to award 0 or more than `checkin_points` points for a late mark
- **THEN** the system SHALL reject the request with a validation error

### Requirement: Teacher revokes check-in for student who was actually absent

Teachers SHALL be able to mark a student who has a `CheckinRecord` for a given date as "actually absent". This SHALL create an `AttendanceCorrection` record with `status: "absent"` and a negative `PointTransaction` with `source_event: "checkin_manual_revoke"` to cancel the previously awarded check-in points.

#### Scenario: Teacher revokes check-in points

- **WHEN** a teacher marks a checked-in student as "actually absent"
- **THEN** the system SHALL create an `AttendanceCorrection` record with `status: "absent"`
- **AND** the system SHALL create a negative `PointTransaction` equal to the class `checkin_points` amount

#### Scenario: Existing correction is overwritten

- **WHEN** a teacher submits a new correction for a student-date pair that already has an `AttendanceCorrection`
- **THEN** the system SHALL update the existing `AttendanceCorrection` record and adjust the corresponding `PointTransaction` accordingly

### Requirement: AttendanceCorrection document

The system SHALL store manual attendance adjustments in an `AttendanceCorrection` Beanie document with fields: `class_id` (str), `student_id` (str), `date` (date), `status` ("late" | "absent"), `partial_points` (int | None, required when status is "late"), `created_by` (teacher user_id), `created_at` (datetime).

#### Scenario: AttendanceCorrection created on first correction

- **WHEN** a teacher submits an attendance correction for a student-date pair with no existing correction
- **THEN** the system SHALL persist a new `AttendanceCorrection` document with the specified fields

#### Scenario: AttendanceCorrection reflects current status on attendance page

- **WHEN** the attendance page loads for a date that has existing corrections
- **THEN** the page SHALL display each student's status reflecting any existing `AttendanceCorrection` overriding their default check-in status
