## ADDED Requirements

### Requirement: User registration by teacher

Teachers SHALL be able to create student accounts. Each account MUST include a unique username, hashed password, display name, and role (student or teacher).

#### Scenario: Teacher creates student account

- **WHEN** a teacher submits a valid username, password, and display name
- **THEN** the system SHALL create the account with role=student and return the new user ID

#### Scenario: Duplicate username rejected

- **WHEN** a teacher submits a username that already exists
- **THEN** the system SHALL return an error and SHALL NOT create a duplicate account

### Requirement: User login with credentials

The system SHALL authenticate users via username and password. On success, a signed JWT SHALL be issued and stored in an HttpOnly cookie.

#### Scenario: Successful login

- **WHEN** a user submits valid credentials
- **THEN** the system SHALL set an HttpOnly cookie containing a signed JWT and redirect to the dashboard

#### Scenario: Invalid credentials rejected

- **WHEN** a user submits an incorrect password or unknown username
- **THEN** the system SHALL return a 401 response and SHALL NOT set a session cookie

### Requirement: JWT-based session management

The system SHALL validate the JWT on every protected request. Tokens MUST include expiry (exp), user ID, and role claims. Expired tokens MUST be rejected.

#### Scenario: Expired token rejected

- **WHEN** a request arrives with an expired JWT cookie
- **THEN** the system SHALL redirect the user to the login page

#### Scenario: Valid token accepted

- **WHEN** a request arrives with a valid, non-expired JWT cookie
- **THEN** the system SHALL allow the request and provide the authenticated user context

### Requirement: Role-based access control

The system SHALL enforce role-based access. Pages and endpoints designated for teachers MUST reject requests from students, and vice versa.

#### Scenario: Student accesses teacher-only endpoint

- **WHEN** a student sends a request to a teacher-only endpoint
- **THEN** the system SHALL return a 403 response

### Requirement: AuthProvider extension point

The system SHALL define an `AuthProvider` Protocol with method `authenticate(credentials) -> User`. The local (username/password) implementation SHALL be registered by default. Additional providers (e.g., Google OAuth) MUST be registerable without modifying core auth code.

#### Scenario: Default local provider authenticates

- **WHEN** the app starts with no additional providers configured
- **THEN** the LocalAuthProvider SHALL handle all authentication requests

#### Scenario: Additional provider registered

- **WHEN** a new AuthProvider implementation is registered in the ExtensionRegistry at startup
- **THEN** the auth router SHALL delegate to that provider when the corresponding login method is selected

### Requirement: Password change

Users SHALL be able to change their own password. The current password MUST be verified before accepting a new one.

#### Scenario: Successful password change

- **WHEN** a user submits their current password and a valid new password
- **THEN** the system SHALL update the stored hash and invalidate existing sessions

#### Scenario: Wrong current password

- **WHEN** a user submits an incorrect current password
- **THEN** the system SHALL return an error and SHALL NOT update the password
