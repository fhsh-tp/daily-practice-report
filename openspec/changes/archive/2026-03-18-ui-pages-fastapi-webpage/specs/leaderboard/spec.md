## ADDED Requirements

### Requirement: Leaderboard HTML page

The system SHALL serve a leaderboard page at `GET /pages/classes/{class_id}/leaderboard`. The page SHALL require authentication. It SHALL display ranked student entries when the leaderboard is enabled for the class, or a "not enabled" message otherwise.

#### Scenario: Leaderboard page shown when enabled

- **WHEN** an authenticated user navigates to `GET /pages/classes/{class_id}/leaderboard` and the class has `leaderboard_enabled = true`
- **THEN** the system SHALL render an HTML page with ranked student entries by points

#### Scenario: Leaderboard page shows disabled message

- **WHEN** an authenticated user navigates to the leaderboard page and the class does not have leaderboard enabled
- **THEN** the system SHALL render an HTML page indicating the leaderboard is not available
