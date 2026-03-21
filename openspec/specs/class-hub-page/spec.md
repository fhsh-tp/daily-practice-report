# class-hub-page Specification

## Purpose

Defines the class hub page available to teachers at `/pages/teacher/class/<class_id>`, which aggregates all teacher tools for a given class and displays a class summary.

## Requirements

### Requirement: Class Hub page provides unified tool entry

The system SHALL provide a class hub page at `/pages/teacher/class/<class_id>` that aggregates all teacher tools for the given class.

#### Scenario: Hub page renders tool cards

- **WHEN** a teacher navigates to the class hub page for a class they own or manage
- **THEN** the page SHALL display quick-access cards for: 成員管理, 任務模板, 簽到設定, 排行榜, 積分管理

#### Scenario: Unauthorized access is rejected

- **WHEN** a user without `can_manage_class` for the given class accesses the hub
- **THEN** the system SHALL return a 403 or redirect to the dashboard

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
-->


<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
code:
  - src/templates/shared/base.html
  - src/templates/teacher/class_hub.html
  - src/pages/router.py
  - src/templates/admin/classes_list.html
tests:
  - tests/test_bug_fixes.py
  - tests/test_class_hub_page.py
-->


<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-21
code:
  - CLAUDE.md
-->

---
### Requirement: Class Hub page displays class summary

The class hub page SHALL display the class name, member count, and current open/closed status at the top of the page.

#### Scenario: Hub page shows class summary

- **WHEN** a teacher opens the class hub page
- **THEN** the page SHALL show class name, member count, and checkin open/closed status

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
-->

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-20
code:
  - src/templates/shared/base.html
  - src/templates/teacher/class_hub.html
  - src/pages/router.py
  - src/templates/admin/classes_list.html
tests:
  - tests/test_bug_fixes.py
  - tests/test_class_hub_page.py
-->

<!-- @trace
source: teacher-class-ux-refactor
updated: 2026-03-21
code:
  - CLAUDE.md
-->