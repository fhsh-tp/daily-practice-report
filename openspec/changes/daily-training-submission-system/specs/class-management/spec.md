## ADDED Requirements

### Requirement: Teacher creates a class

Teachers SHALL be able to create a class with a name, description, and visibility setting (public or private). The creating teacher SHALL automatically become a class owner.

#### Scenario: Successful class creation

- **WHEN** a teacher submits a valid class name and visibility setting
- **THEN** the system SHALL create the class and assign the teacher as owner

### Requirement: Student joins a class

Students SHALL be able to join a class using a class invite code or by browsing public classes. A student MUST be able to join multiple classes simultaneously.

#### Scenario: Student joins via invite code

- **WHEN** a student submits a valid invite code
- **THEN** the system SHALL add the student as a member of that class

#### Scenario: Student joins a public class

- **WHEN** a student selects a public class from the class browser
- **THEN** the system SHALL add the student as a member

#### Scenario: Student already a member

- **WHEN** a student attempts to join a class they already belong to
- **THEN** the system SHALL return an informational message and SHALL NOT create a duplicate membership

### Requirement: Class visibility control

Teachers SHALL be able to set a class as public (visible to all students) or private (invite-only). This setting SHALL apply to leaderboard and community feed visibility outside the class.

#### Scenario: Private class not shown in public listing

- **WHEN** a student browses the public class list
- **THEN** private classes SHALL NOT appear in the results

### Requirement: Teacher manages class members

Class owners SHALL be able to remove students from a class and promote co-teachers. Removed students MUST lose access to class-specific content immediately.

#### Scenario: Teacher removes a student

- **WHEN** a teacher removes a student from a class
- **THEN** the student SHALL no longer appear in the class roster and SHALL NOT be able to submit tasks for that class

### Requirement: Class invite code regeneration

Class owners SHALL be able to regenerate the invite code. The old code MUST become invalid immediately upon regeneration.

#### Scenario: Invite code regenerated

- **WHEN** a teacher regenerates the invite code
- **THEN** the new code SHALL be active and the previous code SHALL be rejected for all future join attempts
