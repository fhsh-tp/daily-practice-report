## ADDED Requirements

### Requirement: Student shares a submission to feed

Students SHALL be able to publish a task submission to the class community feed. A student MUST opt in explicitly; submissions SHALL NOT be shared automatically.

#### Scenario: Student shares submission

- **WHEN** a student explicitly shares a submission to the class feed
- **THEN** the system SHALL create a feed post linked to that submission visible to class members

#### Scenario: Submission not shared by default

- **WHEN** a student submits a task without choosing to share
- **THEN** the submission SHALL NOT appear on the community feed

### Requirement: Class members view the feed

Students and teachers belonging to a class SHALL be able to view the class community feed. Posts SHALL be displayed in reverse chronological order by default.

#### Scenario: Class member views feed

- **WHEN** a class member navigates to the class feed
- **THEN** the system SHALL display all shared posts for that class in reverse chronological order

#### Scenario: Non-member cannot view feed

- **WHEN** a user who is not a member of the class attempts to access the class feed
- **THEN** the system SHALL return a 403 response

### Requirement: Reactions on feed posts

Students and teachers SHALL be able to add emoji reactions to feed posts. Each user MUST add at most one reaction per post. Removing a reaction SHALL be allowed.

#### Scenario: User adds a reaction

- **WHEN** a user adds an emoji reaction to a post they have not yet reacted to
- **THEN** the system SHALL record the reaction and update the reaction count displayed on the post

#### Scenario: User removes a reaction

- **WHEN** a user removes their existing reaction from a post
- **THEN** the system SHALL delete the reaction record and update the count

#### Scenario: Duplicate reaction rejected

- **WHEN** a user attempts to add a second reaction to the same post
- **THEN** the system SHALL return an error and SHALL NOT create a duplicate record

### Requirement: Teacher removes feed posts

Teachers SHALL be able to remove any feed post from the class feed. The underlying submission SHALL NOT be deleted.

#### Scenario: Teacher removes a post

- **WHEN** a teacher removes a feed post
- **THEN** the post SHALL no longer appear on the feed
- **THEN** the original submission SHALL remain accessible in the teacher's submission view

### Requirement: Student removes own post

Students SHALL be able to remove their own feed posts at any time.

#### Scenario: Student removes own post

- **WHEN** a student removes a post they created
- **THEN** the post SHALL no longer appear on the feed
