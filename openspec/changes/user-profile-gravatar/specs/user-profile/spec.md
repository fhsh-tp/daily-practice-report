## ADDED Requirements

### Requirement: User can access personal settings page

The system SHALL provide a settings page at `/pages/settings` accessible to all authenticated users.

#### Scenario: Settings page is accessible when logged in

- **WHEN** an authenticated user navigates to `/pages/settings`
- **THEN** the system SHALL render the settings page with the user's current display name and email

#### Scenario: Unauthenticated access is rejected

- **WHEN** an unauthenticated user navigates to `/pages/settings`
- **THEN** the system SHALL redirect to the login page

### Requirement: User can update display name

The system SHALL allow a user to update their display name via the settings page.

#### Scenario: Display name is updated

- **WHEN** a user submits a non-empty display name via the settings form
- **THEN** the system SHALL update the display name and show a success message

### Requirement: User can change password

The system SHALL allow a user to change their password via the settings page.

#### Scenario: Password is changed successfully

- **WHEN** a user provides the correct current password and a new password that meets minimum length requirements
- **THEN** the system SHALL update the password and show a success message

#### Scenario: Wrong current password is rejected

- **WHEN** a user provides an incorrect current password
- **THEN** the system SHALL return an error and SHALL NOT change the password

### Requirement: User avatar uses Gravatar

The system SHALL display the user's Gravatar avatar based on their email MD5 hash in the sidebar and profile areas.

#### Scenario: Gravatar shown when email is set

- **WHEN** a user with a non-empty email is logged in
- **THEN** the sidebar SHALL display their Gravatar image URL computed as `https://www.gravatar.com/avatar/<md5(email.strip().lower())>?d=identicon`

#### Scenario: Identicon shown when email is empty

- **WHEN** a user has no email set
- **THEN** the system SHALL display `https://www.gravatar.com/avatar/?d=identicon` as the avatar
