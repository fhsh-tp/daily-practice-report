# user-profile Specification

## Purpose

Defines the personal settings page available to all authenticated users, including self-service display name and password updates, and Gravatar-based avatar display.

## Requirements

### Requirement: User can access personal settings page

The system SHALL provide a settings page at `/pages/settings` accessible to all authenticated users.

#### Scenario: Settings page is accessible when logged in

- **WHEN** an authenticated user navigates to `/pages/settings`
- **THEN** the system SHALL render the settings page with the user's current display name and email

#### Scenario: Unauthenticated access is rejected

- **WHEN** an unauthenticated user navigates to `/pages/settings`
- **THEN** the system SHALL redirect to the login page

<!-- @trace
source: user-profile-gravatar
updated: 2026-03-20
-->


<!-- @trace
source: user-profile-gravatar
updated: 2026-03-20
code:
  - src/shared/webpage.py
  - src/shared/gravatar.py
  - src/pages/router.py
  - src/templates/admin/user_form.html
  - src/templates/shared/base.html
  - src/templates/settings.html
tests:
  - tests/test_settings.py
  - tests/test_gravatar_filter.py
-->

---
### Requirement: User can update display name

The system SHALL allow a user to update their display name via the settings page.

#### Scenario: Display name is updated

- **WHEN** a user submits a non-empty display name via the settings form
- **THEN** the system SHALL update the display name and show a success message

<!-- @trace
source: user-profile-gravatar
updated: 2026-03-20
-->


<!-- @trace
source: user-profile-gravatar
updated: 2026-03-20
code:
  - src/shared/webpage.py
  - src/shared/gravatar.py
  - src/pages/router.py
  - src/templates/admin/user_form.html
  - src/templates/shared/base.html
  - src/templates/settings.html
tests:
  - tests/test_settings.py
  - tests/test_gravatar_filter.py
-->

---
### Requirement: User can change password

The system SHALL allow a user to change their password via the settings page.

#### Scenario: Password is changed successfully

- **WHEN** a user provides the correct current password and a new password that meets minimum length requirements
- **THEN** the system SHALL update the password and show a success message

#### Scenario: Wrong current password is rejected

- **WHEN** a user provides an incorrect current password
- **THEN** the system SHALL return an error and SHALL NOT change the password

<!-- @trace
source: user-profile-gravatar
updated: 2026-03-20
-->


<!-- @trace
source: user-profile-gravatar
updated: 2026-03-20
code:
  - src/shared/webpage.py
  - src/shared/gravatar.py
  - src/pages/router.py
  - src/templates/admin/user_form.html
  - src/templates/shared/base.html
  - src/templates/settings.html
tests:
  - tests/test_settings.py
  - tests/test_gravatar_filter.py
-->

---
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

<!-- @trace
source: admin-sidebar-and-settings-polish
updated: 2026-03-24
code:
  - src/shared/page_context 2.py
tests:
  - tests/test_class_hub_stats 2.py
  - tests/test_sidebar_context 2.py
  - tests/test_page_context 2.py
-->