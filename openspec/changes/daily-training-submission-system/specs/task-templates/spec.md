## ADDED Requirements

### Requirement: Teacher creates a task template

Teachers SHALL be able to create a task template for a class. A template MUST include a title, optional description, and one or more field definitions. Each field definition MUST specify: name, field type (text, markdown, number, checkbox), and whether it is required.

#### Scenario: Template with multiple fields created

- **WHEN** a teacher submits a template with a title and at least one field definition
- **THEN** the system SHALL persist the template and associate it with the specified class

#### Scenario: Template with no fields rejected

- **WHEN** a teacher submits a template with zero field definitions
- **THEN** the system SHALL return a validation error and SHALL NOT persist the template

### Requirement: Teacher assigns template to a date

Teachers SHALL be able to assign a task template to one or more specific dates. Students SHALL only see and submit the template assigned to the current date.

#### Scenario: Template assigned to a date

- **WHEN** a teacher assigns a template to a future date
- **THEN** students in that class SHALL see that template on the assigned date and SHALL be able to submit

#### Scenario: No template assigned for today

- **WHEN** no template is assigned for the current date
- **THEN** students SHALL see a message indicating no task is available today

### Requirement: Teacher edits a template

Teachers SHALL be able to edit a template's title, description, and field definitions. Edits SHALL only affect future and unsubmitted assignments; already-submitted entries MUST retain a snapshot of the template version at submission time.

#### Scenario: Template title updated

- **WHEN** a teacher updates the template title
- **THEN** future assignments SHALL use the new title
- **THEN** existing submissions SHALL retain the original title snapshot

### Requirement: Supported field types

The system SHALL support exactly four field types: `text` (single-line plain text), `markdown` (multi-line with WYSIWYG editor), `number` (integer or decimal), `checkbox` (boolean).

#### Scenario: Markdown field rendered in WYSIWYG editor

- **WHEN** a student opens a task submission form with a markdown-type field
- **THEN** the field SHALL render as an EasyMDE editor with live preview

#### Scenario: Number field rejects non-numeric input

- **WHEN** a student enters non-numeric text in a number-type field
- **THEN** the system SHALL display a validation error and SHALL NOT allow submission

### Requirement: Teacher deletes a template

Teachers SHALL be able to delete a template. Deletion SHALL be prevented if the template has any submissions already associated with it.

#### Scenario: Template with submissions cannot be deleted

- **WHEN** a teacher attempts to delete a template that has one or more submissions
- **THEN** the system SHALL return an error and SHALL NOT delete the template
