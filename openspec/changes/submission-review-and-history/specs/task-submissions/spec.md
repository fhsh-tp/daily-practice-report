## ADDED Requirements

### Requirement: Student can view their learning history

The system SHALL provide a learning history page at `/pages/student/history` listing all the student's past task submissions in reverse chronological order.

#### Scenario: History page shows all submissions

- **WHEN** a student navigates to the learning history page
- **THEN** the page SHALL display all their TaskSubmission records with task name, submission date, points earned, and submission content

#### Scenario: Teacher comment shown when present

- **WHEN** a submission has a non-null `teacher_comment`
- **THEN** the history page SHALL display the comment alongside that submission

### Requirement: TaskSubmission stores teacher comment

The TaskSubmission model SHALL include optional fields `teacher_comment` (string, nullable) and `reviewed_at` (datetime, nullable) to support teacher review.

#### Scenario: New submissions have null comment

- **WHEN** a student submits a task
- **THEN** `teacher_comment` SHALL be null and `reviewed_at` SHALL be null

#### Scenario: Comment fields are persisted after review

- **WHEN** a teacher saves a comment for a submission
- **THEN** `teacher_comment` SHALL contain the comment text and `reviewed_at` SHALL record the timestamp
