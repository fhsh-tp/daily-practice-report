## ADDED Requirements

### Requirement: Teacher can configure Discord Webhook URL for a class

The system SHALL allow a teacher to save a Discord Webhook URL for a class via the class settings UI.

#### Scenario: Webhook URL is saved

- **WHEN** a teacher submits a valid Discord Webhook URL in the class settings
- **THEN** the system SHALL store the URL in the class record

#### Scenario: Webhook URL can be cleared

- **WHEN** a teacher submits an empty value for the Webhook URL
- **THEN** the system SHALL set the field to null and disable Discord sync for that class

### Requirement: Task assignment optionally syncs to Discord

The system SHALL send a Discord embed message to the class Webhook URL when a teacher assigns a task and opts in to Discord sync.

#### Scenario: Message sent on opt-in assignment

- **WHEN** a teacher assigns a task and the "同步到 Discord" option is checked and the class has a Webhook URL
- **THEN** the system SHALL send a POST request to the Webhook URL with an embed containing task name, description, and date

#### Scenario: No message sent when opt-out

- **WHEN** a teacher assigns a task without checking the "同步到 Discord" option
- **THEN** the system SHALL NOT send any Discord message

#### Scenario: No message sent when no Webhook URL

- **WHEN** a class has no Webhook URL configured and a teacher assigns a task with sync checked
- **THEN** the system SHALL silently skip the Discord send

### Requirement: Discord send failure does not block task assignment

If the Discord Webhook request fails, the system SHALL log the error and SHALL NOT cause the task assignment to fail.

#### Scenario: Task assignment succeeds despite Discord failure

- **WHEN** the Discord Webhook returns a non-2xx response or times out
- **THEN** the task assignment SHALL still be persisted and the teacher SHALL receive a success response
