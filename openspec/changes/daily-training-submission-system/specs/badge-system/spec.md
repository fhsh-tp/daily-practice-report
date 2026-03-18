## ADDED Requirements

### Requirement: Badge definition by teacher

Teachers SHALL be able to define badges for a class. Each badge definition MUST include: name, description, icon identifier, and one or more trigger conditions expressed as a registered BadgeTrigger key.

#### Scenario: Teacher creates a badge

- **WHEN** a teacher submits a badge definition with a name and at least one trigger key
- **THEN** the system SHALL persist the badge definition for that class

### Requirement: Badge awarded automatically on trigger

The system SHALL evaluate all registered BadgeTriggers after each reward event. If a trigger condition is met and the student does not already hold that badge, the badge SHALL be awarded automatically.

#### Scenario: Badge awarded after trigger condition met

- **WHEN** a reward event occurs and a BadgeTrigger's condition evaluates to true for a student who does not yet hold the badge
- **THEN** the system SHALL create a badge award record for that student

#### Scenario: Badge not awarded if already held

- **WHEN** a reward event occurs and the student already holds the badge
- **THEN** the system SHALL NOT create a duplicate award record

### Requirement: Student views earned badges

Students SHALL be able to view all badges they have earned, including badge name, icon, description, and date awarded.

#### Scenario: Student views badge collection

- **WHEN** a student navigates to their profile or badge page
- **THEN** the system SHALL display all earned badges with award dates

### Requirement: BadgeTrigger extension point

The system SHALL define a `BadgeTrigger` Protocol with method `evaluate(student_id, event: RewardEvent, context: TriggerContext) -> bool`. Registered triggers SHALL be evaluated after every reward event. Built-in triggers SHALL include: consecutive check-in streak (configurable threshold) and total submission count (configurable threshold).

#### Scenario: Consecutive check-in trigger evaluated

- **WHEN** a student checks in and a ConsecutiveCheckinTrigger is registered with threshold=7
- **THEN** the trigger SHALL evaluate whether the student has checked in for 7 consecutive days

#### Scenario: Custom trigger registered

- **WHEN** a custom BadgeTrigger is registered in the ExtensionRegistry at startup
- **THEN** the system SHALL evaluate it after every reward event alongside built-in triggers

### Requirement: Teacher awards badge manually

Teachers SHALL be able to manually award any defined badge to any student in their class, with an optional reason note.

#### Scenario: Teacher manually awards badge

- **WHEN** a teacher selects a student and a badge and submits the manual award
- **THEN** the system SHALL create a badge award record with manual award source
