## ADDED Requirements

### Requirement: Class list view separates active and archived classes

The class management view SHALL visually separate active classes from archived classes using a tab interface.

#### Scenario: Active and archived classes in separate tabs

- **WHEN** the class list is rendered
- **THEN** active (non-archived) classes SHALL appear in the 運作中 tab and archived classes SHALL appear in the 已封存 tab

#### Scenario: Tab counts reflect actual class counts

- **WHEN** the class list is rendered
- **THEN** each tab label SHALL display the count of classes in that category
