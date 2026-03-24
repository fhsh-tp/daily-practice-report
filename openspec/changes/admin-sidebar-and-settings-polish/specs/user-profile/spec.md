## MODIFIED Requirements

### Requirement: User avatar uses Gravatar

The system SHALL display the user's Gravatar avatar based on their email MD5 hash in the sidebar and profile areas. The settings page avatar section SHALL include a link to `https://gravatar.com/` (opening in a new tab) with the text "前往 Gravatar 更換頭像", visible only when the user has an email set. When the user has an email, a tooltip SHALL indicate "頭像由 Gravatar 提供，綁定您的 Email". When the user has no email, the avatar section SHALL display a subtle inline hint "請聯絡管理員設定 Email 以自訂頭像" instead of a prominent warning banner.

#### Scenario: Gravatar shown when email is set

- **WHEN** a user with a non-empty email is logged in
- **THEN** the sidebar SHALL display their Gravatar image URL computed as `https://www.gravatar.com/avatar/<md5(email.strip().lower())>?d=identicon`

#### Scenario: Identicon shown when email is empty

- **WHEN** a user has no email set
- **THEN** the system SHALL display `https://www.gravatar.com/avatar/?d=identicon` as the avatar

#### Scenario: Settings page shows Gravatar link for user with email

- **WHEN** a user with a non-empty email views the settings page
- **THEN** the avatar section SHALL display a link "前往 Gravatar 更換頭像" that opens `https://gravatar.com/` in a new tab

#### Scenario: Settings page shows tooltip for Gravatar explanation

- **WHEN** a user with a non-empty email views the settings page avatar section
- **THEN** the avatar section SHALL display a tooltip or inline hint "頭像由 Gravatar 提供，綁定您的 Email"

#### Scenario: Settings page shows subtle hint when email is missing

- **WHEN** a user without an email views the settings page
- **THEN** the avatar section SHALL display a subtle gray text hint "請聯絡管理員設定 Email 以自訂頭像" instead of a prominent warning banner
