## ADDED Requirements

### Requirement: Student submits daily task

Students SHALL be able to submit the daily task assigned to the current date in a class they belong to. Each student MUST submit at most once per template-date assignment. The submission MUST capture a snapshot of the template version at submission time.

#### Scenario: Successful first submission

- **WHEN** a student submits a completed form for today's template
- **THEN** the system SHALL persist the submission with a timestamp and trigger the configured RewardProviders

#### Scenario: Duplicate submission rejected

- **WHEN** a student attempts to submit a second time for the same template-date
- **THEN** the system SHALL return an error and SHALL NOT create a duplicate submission

### Requirement: Required fields enforced

The system SHALL reject a submission if any required field is empty or fails type validation.

#### Scenario: Required field left empty

- **WHEN** a student submits a form with a required field left empty
- **THEN** the system SHALL return a validation error identifying the field and SHALL NOT persist the submission

### Requirement: Student views submission history

Students SHALL be able to view their own past submissions, including the original field values and the date submitted.

#### Scenario: Student views past submission

- **WHEN** a student navigates to their submission history
- **THEN** the system SHALL display a list of past submissions with date, template title, and field values

### Requirement: Teacher views class submissions

Teachers SHALL be able to view all student submissions for a given date and class. The view MUST include student name, submission time, and all field values.

#### Scenario: Teacher views submissions for a date

- **WHEN** a teacher selects a class and date on the teacher dashboard
- **THEN** the system SHALL display all submissions for that date, including students who have not yet submitted

### Requirement: SubmissionValidator extension point

The system SHALL define a `SubmissionValidator` Protocol with method `validate(submission_data, template) -> ValidationResult`. Registered validators SHALL be invoked before persisting a submission. If any validator returns invalid, the submission SHALL be rejected with the validator's error message.

#### Scenario: Custom validator rejects submission

- **WHEN** a registered SubmissionValidator returns invalid for a submission
- **THEN** the system SHALL return the validator's error message and SHALL NOT persist the submission
