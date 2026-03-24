## ADDED Requirements

### Requirement: TaskSubmission stores review state

The `TaskSubmission` document SHALL include the following review-related fields:
- `status`: `"pending" | "approved" | "rejected"` — defaults to `"pending"` on creation
- `rejection_reason`: `str | None` — set when status is `"rejected"`
- `resubmit_deadline`: `datetime | None` — optional deadline set by teacher on rejection
- `parent_submission_id`: `str | None` — set on resubmissions to reference the rejected predecessor

#### Scenario: New submissions have pending status

- **WHEN** a student submits a task
- **THEN** `status` SHALL be `"pending"`, `rejection_reason` SHALL be null, `resubmit_deadline` SHALL be null, and `parent_submission_id` SHALL be null

#### Scenario: Rejection fields populated on reject

- **WHEN** a teacher rejects a submission
- **THEN** `status` SHALL be `"rejected"`, `rejection_reason` SHALL contain the reason text, and `resubmit_deadline` SHALL contain the deadline if provided

#### Scenario: Parent link set on resubmission

- **WHEN** a student creates a resubmission for a previously rejected submission
- **THEN** the new submission's `parent_submission_id` SHALL equal the rejected submission's document ID

## MODIFIED Requirements

### Requirement: Student submits daily task

Students SHALL be able to submit the daily task assigned to the current date in a class they belong to. Each student MUST have at most one non-rejected submission per template-date assignment. Submissions with `status: "rejected"` SHALL NOT count toward the uniqueness constraint, allowing resubmission. The submission MUST capture a snapshot of the template version at submission time. On creation, `status` SHALL default to `"pending"` and points SHALL be awarded immediately.

#### Scenario: Successful first submission

- **WHEN** a student submits a completed form for today's template
- **THEN** the system SHALL persist the submission with `status: "pending"`, a timestamp, and trigger the configured RewardProviders

#### Scenario: Duplicate submission rejected when active submission exists

- **WHEN** a student attempts to submit a second time for the same template-date and a non-rejected submission already exists
- **THEN** the system SHALL return an error and SHALL NOT create a duplicate submission

#### Scenario: Resubmission allowed after rejection

- **WHEN** a student submits for a date where their only existing submission has `status: "rejected"`
- **THEN** the system SHALL allow the new submission and SHALL NOT return a duplicate error

The `TaskSubmission` document SHALL include the following review-related fields:
- `status`: `"pending" | "approved" | "rejected"` — defaults to `"pending"` on creation
- `rejection_reason`: `str | None` — set when status is `"rejected"`
- `resubmit_deadline`: `datetime | None` — optional deadline set by teacher on rejection
- `parent_submission_id`: `str | None` — set on resubmissions to reference the rejected predecessor

#### Scenario: New submissions have pending status

- **WHEN** a student submits a task
- **THEN** `status` SHALL be `"pending"`, `rejection_reason` SHALL be null, `resubmit_deadline` SHALL be null, and `parent_submission_id` SHALL be null

#### Scenario: Rejection fields populated on reject

- **WHEN** a teacher rejects a submission
- **THEN** `status` SHALL be `"rejected"`, `rejection_reason` SHALL contain the reason text, and `resubmit_deadline` SHALL contain the deadline if provided

#### Scenario: Parent link set on resubmission

- **WHEN** a student creates a resubmission for a previously rejected submission
- **THEN** the new submission's `parent_submission_id` SHALL equal the rejected submission's document ID

## ADDED Requirements

### Requirement: Student can view learning history with review status

Students SHALL be able to view their own past submissions including the review status. The history page SHALL display `status`, `rejection_reason`, and a link to the rejection detail page for `"rejected"` submissions.

#### Scenario: History shows review status

- **WHEN** a student views their learning history
- **THEN** each submission SHALL display its current `status` (pending / approved / rejected)

#### Scenario: Rejected submission shows link to detail

- **WHEN** a submission in the history has `status: "rejected"`
- **THEN** the page SHALL display the rejection reason and a link to `GET /pages/student/submissions/{submission_id}/rejection`
