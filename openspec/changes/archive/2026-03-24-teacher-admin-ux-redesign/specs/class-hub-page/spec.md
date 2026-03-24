## MODIFIED Requirements

### Requirement: Class Hub page provides unified tool entry

The system SHALL provide a class hub page at `/pages/teacher/class/<class_id>` that aggregates all teacher tools for the given class.

#### Scenario: Hub page renders tool cards

- **WHEN** a teacher navigates to the class hub page for a class they own or manage
- **THEN** the page SHALL display quick-access cards for: 成員管理, 任務模板, 任務審查, 簽到設定, 出席紀錄, 排行榜, 積分管理

#### Scenario: Unauthorized access is rejected

- **WHEN** a user without `can_manage_class` for the given class accesses the hub
- **THEN** the system SHALL return a 403 or redirect to the dashboard

### Requirement: Class Hub page displays class summary

The class hub page SHALL display the class name, member count, current checkin open/closed status, pending submission count, today's checkin rate, and weekly submission rate at the top of the page as statistics cards.

#### Scenario: Hub page shows statistics cards

- **WHEN** a teacher opens the class hub page
- **THEN** the page SHALL show four statistics cards: member count, today's checkin rate (checked-in / total), pending submission count, and weekly submission rate as a percentage

## ADDED Requirements

### Requirement: Class Hub page displays invite code

The class hub page SHALL display the class invite code in a compact inline bar below the page title and above the statistics cards. The bar SHALL include a copy-to-clipboard button and a regenerate button. The invite code display SHALL replace the invite code section previously shown on the class members page.

#### Scenario: Teacher sees invite code on class hub

- **WHEN** a teacher opens the class hub page
- **THEN** the page SHALL display the class invite code with a description "學生輸入即可加入" and buttons for copying and regenerating

#### Scenario: Teacher copies invite code

- **WHEN** a teacher clicks the copy button next to the invite code
- **THEN** the invite code SHALL be copied to the system clipboard and a success toast SHALL appear

#### Scenario: Teacher regenerates invite code

- **WHEN** a teacher clicks the regenerate button
- **THEN** the system SHALL call the regeneration API and display the new invite code without a page reload

### Requirement: Class Hub page displays Discord Webhook integration

The class hub page SHALL display a Discord Webhook integration section below the quick-access tool cards. The section SHALL show the current webhook URL (if configured) and a configure/edit button.

#### Scenario: Class with no webhook shows setup prompt

- **WHEN** a teacher views the class hub for a class with no Discord webhook configured
- **THEN** the integration section SHALL display a setup prompt with an input field and save button

#### Scenario: Class with webhook shows current URL

- **WHEN** a teacher views the class hub for a class with a configured Discord webhook
- **THEN** the integration section SHALL display the current webhook URL with edit and remove options
