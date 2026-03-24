## ADDED Requirements

### Requirement: Student dashboard class card displays teacher name

The student dashboard class card SHALL display the owner (teacher) display name for each enrolled class.

#### Scenario: Class card shows teacher display name

- **WHEN** a student views the dashboard
- **THEN** each class card SHALL display the class owner's display name

#### Scenario: Teacher name fallback when owner not found

- **WHEN** the class owner account no longer exists
- **THEN** the class card SHALL display an empty string instead of raising an error

### Requirement: Sidebar hides create-class shortcut for all-class managers

The sidebar SHALL NOT display the "建立第一個班級" shortcut when the current user has `can_manage_all_classes` permission, even if their class membership list is empty.

#### Scenario: System admin sees no create-class shortcut

- **WHEN** a user with `can_manage_all_classes` is logged in and has no class memberships
- **THEN** the sidebar SHALL NOT show the "建立第一個班級" link under 教師工具

#### Scenario: Teacher with no classes still sees create-class shortcut

- **WHEN** a user with `can_manage_class` but NOT `can_manage_all_classes` has no class memberships
- **THEN** the sidebar SHALL show the "建立第一個班級" link under 教師工具

### Requirement: Class members page header renders without layout overflow

The class members page header SHALL display the page title and action buttons without wrapping or overflow at standard viewport widths.

#### Scenario: Header buttons are grouped

- **WHEN** the class members page is rendered at any standard viewport width
- **THEN** the action buttons (任務模板, 簽到設定) SHALL be contained in a single flex group and SHALL NOT wrap independently from each other
