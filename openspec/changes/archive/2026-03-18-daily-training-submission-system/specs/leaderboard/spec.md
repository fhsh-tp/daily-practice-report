## ADDED Requirements

### Requirement: Class leaderboard

Each class SHALL have a leaderboard ranking members by total point balance, displayed in descending order. The leaderboard SHALL be visible to all class members by default.

#### Scenario: Class member views leaderboard

- **WHEN** a class member navigates to the class leaderboard
- **THEN** the system SHALL display a ranked list of students with their point balances

### Requirement: Teacher controls leaderboard visibility

Teachers SHALL be able to disable the leaderboard for their class. When disabled, students SHALL NOT be able to view the leaderboard.

#### Scenario: Leaderboard disabled by teacher

- **WHEN** a teacher disables the leaderboard for a class
- **THEN** the leaderboard page SHALL return an unavailable message to students

### Requirement: Cross-class leaderboard

The system SHALL provide a cross-class leaderboard aggregating point balances across all classes a student belongs to. Cross-class leaderboard entries SHALL only include students whose all relevant classes have leaderboard enabled and are set to public.

#### Scenario: Student appears in cross-class leaderboard

- **WHEN** a student belongs to at least one public class with leaderboard enabled
- **THEN** their aggregated balance SHALL appear in the cross-class leaderboard

#### Scenario: Student in private class excluded from cross-class

- **WHEN** all classes a student belongs to are private or have leaderboard disabled
- **THEN** the student SHALL NOT appear in the cross-class leaderboard

### Requirement: Leaderboard rank display

Each leaderboard entry MUST display: rank number, student display name, total points, and badge count. Tied students MUST share the same rank.

#### Scenario: Tied students share rank

- **WHEN** two students have identical total point balances
- **THEN** both SHALL be assigned the same rank number on the leaderboard
