## ADDED Requirements

### Requirement: Sidebar teacher section shows class list

The sidebar teacher section SHALL display a list of the teacher's classes as navigation items, each linking to the class hub page. When the current page is within a class hub, the sidebar SHALL show that class's tool links indented below the class name.

#### Scenario: Teacher sidebar lists classes

- **WHEN** a teacher with `can_manage_class` is logged in and has one or more classes
- **THEN** the sidebar SHALL display each class name as a link to its hub page under 教師工具

#### Scenario: Active class expands tool links

- **WHEN** the current URL contains a class_id matching one of the teacher's classes
- **THEN** the sidebar SHALL display indented tool links (成員管理, 任務模板, 簽到設定, 排行榜, 積分管理) under that class name

#### Scenario: Add new class button always visible

- **WHEN** a teacher with `can_manage_class` is logged in
- **THEN** the sidebar SHALL always display a "+ 新增班級" button in the 教師工具 section

## ADDED Requirements

### Requirement: Class list supports tab switching between active and archived

The class list page SHALL provide two tabs — 運作中 and 已封存 — to separate active classes from archived ones.

#### Scenario: Default tab shows active classes

- **WHEN** a user opens the class list page
- **THEN** the 運作中 tab SHALL be active by default and SHALL show only non-archived classes

#### Scenario: Archived tab shows only archived classes

- **WHEN** a user clicks the 已封存 tab
- **THEN** only archived classes SHALL be displayed

### Requirement: Class list supports search by name and teacher

Each class list tab SHALL provide a text input that filters classes by class name or teacher display name.

#### Scenario: Search filters by class name

- **WHEN** a user types a class name substring into the search input
- **THEN** only matching classes SHALL remain visible in the list

#### Scenario: Search filters by teacher name

- **WHEN** a user types a teacher display name substring into the search input
- **THEN** only classes whose owner display name matches SHALL remain visible
