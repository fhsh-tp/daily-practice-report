## MODIFIED Requirements

### Requirement: Teacher manages class members

A user SHALL be able to manage a class's members only if they hold `MANAGE_ALL_CLASSES`, or if they hold `MANAGE_OWN_CLASS` AND have a `ClassMembership` with role `teacher` in that class. Management operations include: removing students, promoting co-teachers, and regenerating the invite code. The system MUST reject management operations from users who do not satisfy these conditions with HTTP 403. The class members page SHALL use a two-column layout: the left column for batch invite search and the right column for the current member list. The page SHALL NOT display the invite code (moved to class hub page).

#### Scenario: Class teacher manages their own class

- **WHEN** a user with `MANAGE_OWN_CLASS` and a `teacher` membership in class C sends a management request for class C
- **THEN** the request MUST proceed normally

#### Scenario: User with MANAGE_OWN_CLASS cannot manage another teacher's class

- **WHEN** a user with `MANAGE_OWN_CLASS` but no `teacher` membership in class C sends a management request for class C
- **THEN** the system MUST return HTTP 403

#### Scenario: ClassManager manages any class

- **WHEN** a user with `MANAGE_ALL_CLASSES` sends a management request for any class
- **THEN** the request MUST proceed regardless of membership

#### Scenario: Teacher removes a student

- **WHEN** an authorized teacher removes a student from a class
- **THEN** the student SHALL no longer appear in the class roster and SHALL NOT be able to submit tasks for that class

#### Scenario: Members page uses two-column layout

- **WHEN** a teacher views the class members page
- **THEN** the page SHALL display a two-column layout with batch invite search on the left and current member list on the right

#### Scenario: Members page does not show invite code

- **WHEN** a teacher views the class members page
- **THEN** the page SHALL NOT display the class invite code section (invite code is on the class hub page)
