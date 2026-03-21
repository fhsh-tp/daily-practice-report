## ADDED Requirements

### Requirement: Task assignment form includes Discord sync option

The task assignment form SHALL include a checkbox "同步到 Discord" that is visible only when the class has a configured Webhook URL.

#### Scenario: Sync checkbox shown when webhook is configured

- **WHEN** a teacher opens the task assignment form for a class with a Webhook URL
- **THEN** the "同步到 Discord" checkbox SHALL be visible

#### Scenario: Sync checkbox hidden when no webhook

- **WHEN** a teacher opens the task assignment form for a class without a Webhook URL
- **THEN** the "同步到 Discord" checkbox SHALL NOT be displayed
