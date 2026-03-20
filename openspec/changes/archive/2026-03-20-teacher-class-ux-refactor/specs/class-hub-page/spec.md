## ADDED Requirements

### Requirement: Class Hub page provides unified tool entry

The system SHALL provide a class hub page at `/pages/teacher/class/<class_id>` that aggregates all teacher tools for the given class.

#### Scenario: Hub page renders tool cards

- **WHEN** a teacher navigates to the class hub page for a class they own or manage
- **THEN** the page SHALL display quick-access cards for: 成員管理, 任務模板, 簽到設定, 排行榜, 積分管理

#### Scenario: Unauthorized access is rejected

- **WHEN** a user without `can_manage_class` for the given class accesses the hub
- **THEN** the system SHALL return a 403 or redirect to the dashboard

### Requirement: Class Hub page displays class summary

The class hub page SHALL display the class name, member count, and current open/closed status at the top of the page.

#### Scenario: Hub page shows class summary

- **WHEN** a teacher opens the class hub page
- **THEN** the page SHALL show class name, member count, and checkin open/closed status
