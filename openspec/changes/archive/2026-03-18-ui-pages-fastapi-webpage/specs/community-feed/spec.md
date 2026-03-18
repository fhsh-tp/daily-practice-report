## ADDED Requirements

### Requirement: Community feed HTML page

The system SHALL serve a community feed page at `GET /pages/classes/{class_id}/feed`. The page SHALL require authentication and class membership. It SHALL display all posts in reverse chronological order with reactions.

#### Scenario: Member views class feed page

- **WHEN** an authenticated class member navigates to `GET /pages/classes/{class_id}/feed`
- **THEN** the system SHALL render an HTML page displaying all feed posts for that class in reverse chronological order

#### Scenario: Non-member rejected

- **WHEN** a user who is not a member of the class accesses the feed page
- **THEN** the system SHALL return HTTP 403
