## MODIFIED Requirements

### Requirement: Teacher can view all student submissions for a class

Teachers SHALL be able to view all student submissions for a class via a page at `GET /pages/teacher/class/{class_id}/submissions`. The page SHALL display submissions grouped by student with each submission's status badge (pending / approved / rejected), submission content, and review actions.

#### Scenario: Submission list shows status badge

- **WHEN** a teacher views the submission review page
- **THEN** each submission SHALL display a status badge indicating "pending", "approved", or "rejected"

#### Scenario: Approved submission shows approved state

- **WHEN** a submission has `status: "approved"`
- **THEN** the page SHALL display a green "已確認" badge and the approve button SHALL reflect the confirmed state

## ADDED Requirements

### Requirement: Teacher approves submission from review page

The teacher submission review page SHALL provide an "確認" (approve) button per submission. Clicking it SHALL call `POST /api/submissions/{submission_id}/approve` and update the submission's status in the UI without a full page reload.

#### Scenario: Teacher clicks approve

- **WHEN** a teacher clicks "確認" on a pending or rejected submission
- **THEN** the system SHALL call the approve endpoint, update the submission status badge to "已確認", and remain on the review page

### Requirement: Teacher rejects submission from review page

The teacher submission review page SHALL provide a "退回" (reject) flow per submission. The flow SHALL open an inline panel or modal where the teacher writes the rejection reason and optionally sets a resubmit deadline before confirming. Confirming SHALL call `POST /api/submissions/{submission_id}/reject`.

#### Scenario: Teacher opens reject panel

- **WHEN** a teacher clicks "退回" on a submission
- **THEN** the page SHALL show an inline panel or modal with a required text area for rejection reason and an optional date-time picker for resubmit deadline

#### Scenario: Teacher confirms rejection

- **WHEN** a teacher fills in the rejection reason and confirms
- **THEN** the system SHALL call the reject endpoint, update the status badge to "已退回", and remain on the review page

#### Scenario: Empty rejection reason blocked

- **WHEN** a teacher confirms rejection without a reason
- **THEN** the UI SHALL show a validation error and SHALL NOT submit the request
