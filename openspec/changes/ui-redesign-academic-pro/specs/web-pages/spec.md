## MODIFIED Requirements

### Requirement: Dashboard is the unified authenticated entry point

The system SHALL serve a dashboard page at `GET /pages/dashboard`. The page SHALL require authentication. The page content SHALL vary based on the authenticated user's permissions. The dashboard layout SHALL consist of three sections rendered in order:

1. **Widget Grid** — a row of stat cards showing the current user's total points, badge count, consecutive-day streak, and total submission count. When the viewer has `MANAGE_CLASS` permission, the Widget Grid SHALL instead show class-aggregate statistics: total enrolled students, today's checkin count, and today's submission count.
2. **Class Card Grid** — one card per enrolled (or managed) class. Each card SHALL display the class name, today's checkin and submission status, and primary action links (checkin, submit task). Teacher cards SHALL additionally include a teacher toolbar row with links to templates, points management, and member list.
3. **Activity Feed** — a chronological timeline of the authenticated user's recent activity (checkins, submissions, badge awards), limited to the 20 most recent entries.

#### Scenario: Student views dashboard

- **WHEN** a student navigates to `GET /pages/dashboard`
- **THEN** the page SHALL display the Widget Grid with the student's personal stats, the Class Card Grid with enrolled classes, and the Activity Feed with their recent events

#### Scenario: Teacher views dashboard

- **WHEN** a user with `MANAGE_CLASS` permission navigates to `GET /pages/dashboard`
- **THEN** the Widget Grid SHALL show class-aggregate statistics and each class card SHALL include a teacher toolbar with management links

#### Scenario: Error message shown on dashboard

- **WHEN** `GET /pages/dashboard?error=<message>` is requested by an authenticated user
- **THEN** the page SHALL display the error message

---

## ADDED Requirements

### Requirement: Dashboard displays gamified badge strip

The dashboard page SHALL render a horizontal scrollable badge strip below the Widget Grid, showing the user's most recently earned badges (up to 10). Each badge item SHALL display the badge icon and name. Unearned badge slots SHALL be shown in a visually muted locked state to communicate progress.

#### Scenario: Earned badges shown in strip

- **WHEN** a student has earned at least one badge
- **THEN** the badge strip SHALL show those badges with full color and label

#### Scenario: Empty badge strip hidden

- **WHEN** a student has earned no badges
- **THEN** the badge strip section SHALL not render
