## MODIFIED Requirements

### Requirement: Teacher can view all student submissions for a class

Teachers SHALL be able to view all student submissions for a class via a page at `GET /pages/teacher/class/{class_id}/submissions`. The page SHALL display submissions as a flat card list (not grouped by student). Each submission card SHALL show the student avatar and name, task name, submission timestamp, status badge (pending / approved / rejected), submission content preview, and action buttons. Resubmissions (submissions after rejection) SHALL be marked with a "補繳" badge.

#### Scenario: Submission list shows status badge

- **WHEN** a teacher views the submission review page
- **THEN** each submission card SHALL display a status badge indicating "待審閱" (pending), "已確認" (approved), or "已退回" (rejected)

#### Scenario: Approved submission shows approved state

- **WHEN** a submission has `status: "approved"`
- **THEN** the page SHALL display a green "已確認" badge and the approve button SHALL reflect the confirmed state

#### Scenario: Resubmission shows resubmit badge

- **WHEN** a submission is a resubmission after a previous rejection
- **THEN** the submission card SHALL display a "補繳" badge alongside the student name

## ADDED Requirements

### Requirement: Submission review page provides filter tabs

The submission review page SHALL display filter tabs at the top: "待審閱", "已確認", "已退回", and "全部". The "待審閱" tab SHALL show the count of pending submissions as a badge. Clicking a tab SHALL filter the displayed submission cards to show only submissions matching that status. Filtering SHALL be client-side with no additional API calls. The default active tab SHALL be "待審閱".

#### Scenario: Filter tabs show correct counts

- **WHEN** a teacher views the submission review page
- **THEN** the "待審閱" tab SHALL display the count of pending submissions as a numeric badge

#### Scenario: Teacher filters by status

- **WHEN** a teacher clicks the "已退回" filter tab
- **THEN** the page SHALL display only submissions with "rejected" status and hide all others

#### Scenario: All tab shows all submissions

- **WHEN** a teacher clicks the "全部" filter tab
- **THEN** the page SHALL display all submissions regardless of status
