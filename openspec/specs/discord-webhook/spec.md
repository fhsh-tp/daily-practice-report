# discord-webhook Specification

## Purpose

Defines requirements for Discord Webhook integration, including configuration of Webhook URLs per class, opt-in Discord sync when assigning tasks, and failure-tolerant send behavior.

## Requirements

### Requirement: Teacher can configure Discord Webhook URL for a class

The system SHALL allow a teacher to save a Discord Webhook URL for a class via the class settings UI.

#### Scenario: Webhook URL is saved

- **WHEN** a teacher submits a valid Discord Webhook URL in the class settings
- **THEN** the system SHALL store the URL in the class record

#### Scenario: Webhook URL can be cleared

- **WHEN** a teacher submits an empty value for the Webhook URL
- **THEN** the system SHALL set the field to null and disable Discord sync for that class

<!-- @trace
source: discord-integration
updated: 2026-03-21
-->


<!-- @trace
source: discord-integration
updated: 2026-03-21
code:
  - src/integrations/discord/service.py
  - src/tasks/templates/router.py
  - src/core/classes/router.py
  - src/templates/teacher/class_hub.html
  - src/integrations/__init__.py
  - src/templates/teacher/template_assign.html
  - src/core/classes/models.py
  - src/pages/router.py
  - src/integrations/discord/__init__.py
tests:
  - tests/test_discord_integration.py
-->

---
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

<!-- @trace
source: discord-integration
updated: 2026-03-21
-->


<!-- @trace
source: discord-integration
updated: 2026-03-21
code:
  - src/integrations/discord/service.py
  - src/tasks/templates/router.py
  - src/core/classes/router.py
  - src/templates/teacher/class_hub.html
  - src/integrations/__init__.py
  - src/templates/teacher/template_assign.html
  - src/core/classes/models.py
  - src/pages/router.py
  - src/integrations/discord/__init__.py
tests:
  - tests/test_discord_integration.py
-->

---
### Requirement: Discord send failure does not block task assignment

If the Discord Webhook request fails, the system SHALL log the error and SHALL NOT cause the task assignment to fail.

#### Scenario: Task assignment succeeds despite Discord failure

- **WHEN** the Discord Webhook returns a non-2xx response or times out
- **THEN** the task assignment SHALL still be persisted and the teacher SHALL receive a success response

<!-- @trace
source: discord-integration
updated: 2026-03-21
-->

<!-- @trace
source: discord-integration
updated: 2026-03-21
code:
  - src/integrations/discord/service.py
  - src/tasks/templates/router.py
  - src/core/classes/router.py
  - src/templates/teacher/class_hub.html
  - src/integrations/__init__.py
  - src/templates/teacher/template_assign.html
  - src/core/classes/models.py
  - src/pages/router.py
  - src/integrations/discord/__init__.py
tests:
  - tests/test_discord_integration.py
-->
## ADDED Requirements

### Requirement: Discord webhook URL format validation

The system SHALL validate that a Discord webhook URL starts with `https://discord.com/api/webhooks/` or `https://discordapp.com/api/webhooks/` before saving it. URLs that do not match either prefix SHALL be rejected with HTTP 422.

#### Scenario: Invalid webhook URL rejected

- **WHEN** a user submits a webhook URL that does not start with `https://discord.com/api/webhooks/` or `https://discordapp.com/api/webhooks/`
- **THEN** the system SHALL return HTTP 422 and SHALL NOT persist the URL

#### Scenario: Valid discord.com webhook URL accepted

- **WHEN** a user submits a URL beginning with `https://discord.com/api/webhooks/`
- **THEN** the system SHALL accept and persist the URL

#### Scenario: Valid discordapp.com webhook URL accepted

- **WHEN** a user submits a URL beginning with `https://discordapp.com/api/webhooks/`
- **THEN** the system SHALL accept and persist the URL

#### Scenario: Empty URL accepted (disables webhook)

- **WHEN** a user submits an empty string as the webhook URL
- **THEN** the system SHALL accept it (effectively disabling the webhook)

<!-- @trace
source: security-audit-fixes
updated: 2026-03-23
code:
  - src/core/classes/router.py
tests:
  - tests/test_security_audit.py
-->
