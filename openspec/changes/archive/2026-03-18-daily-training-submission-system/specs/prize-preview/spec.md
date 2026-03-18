## ADDED Requirements

### Requirement: Teacher creates prize preview

Teachers SHALL be able to create prize previews for a class. Each prize MUST include: title, description, prize type (online or physical), optional image, and an optional point cost for display purposes.

#### Scenario: Teacher creates an online prize

- **WHEN** a teacher submits a prize with type=online and a description
- **THEN** the system SHALL persist the prize and make it visible to class members

#### Scenario: Teacher creates a physical prize

- **WHEN** a teacher submits a prize with type=physical and an optional image
- **THEN** the system SHALL persist the prize with the provided details

### Requirement: Students view prize showcase

Students SHALL be able to view all active prizes for their class. The display MUST include title, description, type, image (if provided), and point cost (if set).

#### Scenario: Student views prize list

- **WHEN** a student navigates to the prizes page for a class
- **THEN** the system SHALL display all active prizes for that class in the configured display order

### Requirement: Teacher manages prize visibility

Teachers SHALL be able to show or hide individual prizes without deleting them. Hidden prizes SHALL NOT appear in the student-facing prize list.

#### Scenario: Teacher hides a prize

- **WHEN** a teacher sets a prize to hidden
- **THEN** the prize SHALL NOT appear in the student prize list but SHALL remain in the teacher's prize management view

### Requirement: Teacher edits and deletes prizes

Teachers SHALL be able to edit prize details at any time. Teachers SHALL be able to delete a prize permanently.

#### Scenario: Teacher edits a prize

- **WHEN** a teacher updates a prize's title or description
- **THEN** the updated details SHALL appear immediately in the student-facing view

#### Scenario: Teacher deletes a prize

- **WHEN** a teacher deletes a prize
- **THEN** the prize SHALL be removed from all views permanently
