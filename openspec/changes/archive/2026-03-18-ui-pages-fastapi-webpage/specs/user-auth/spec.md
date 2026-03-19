## ADDED Requirements

### Requirement: Browser-based form login endpoint

The system SHALL accept `POST /pages/login` with `application/x-www-form-urlencoded` body containing `username` and `password`. On success, it SHALL set the JWT cookie and redirect to `GET /pages/dashboard`. On failure, it SHALL redirect to `GET /pages/login?error=<message>`.

#### Scenario: Successful form login

- **WHEN** a user submits valid credentials via the HTML login form at `POST /pages/login`
- **THEN** the system SHALL set an HttpOnly JWT cookie and redirect to `GET /pages/dashboard` (HTTP 302)

#### Scenario: Invalid credentials via form

- **WHEN** a user submits invalid credentials via the HTML login form
- **THEN** the system SHALL redirect to `GET /pages/login?error=帳號或密碼錯誤` (HTTP 302)
- **AND** the JWT cookie SHALL NOT be set

---

### Requirement: Browser-based logout redirects to login

The system SHALL accept `POST /auth/logout` and redirect to `GET /pages/login` after clearing the session cookie.

#### Scenario: Successful logout

- **WHEN** a user submits the logout form via `POST /auth/logout`
- **THEN** the system SHALL clear the JWT cookie and redirect to `GET /pages/login` (HTTP 302)

## MODIFIED Requirements

### Requirement: User login with credentials

The system SHALL authenticate users via username and password. On success, a signed JWT SHALL be issued and stored in an HttpOnly cookie. The API endpoint (`POST /auth/login`) SHALL accept JSON and return JSON. The form endpoint (`POST /pages/login`) SHALL accept form data and redirect.

#### Scenario: Successful API login

- **WHEN** a client submits valid credentials to `POST /auth/login` with JSON body
- **THEN** the system SHALL set an HttpOnly cookie containing a signed JWT and return JSON with permissions

#### Scenario: Successful form login

- **WHEN** a user submits valid credentials via `POST /pages/login` with form data
- **THEN** the system SHALL set an HttpOnly JWT cookie and redirect to `GET /pages/dashboard` (HTTP 302)

#### Scenario: Invalid credentials rejected via API

- **WHEN** a client submits an incorrect password or unknown username to `POST /auth/login`
- **THEN** the system SHALL return HTTP 401 and SHALL NOT set a session cookie

#### Scenario: Invalid credentials rejected via form

- **WHEN** a user submits incorrect credentials via `POST /pages/login`
- **THEN** the system SHALL redirect to `GET /pages/login?error=帳號或密碼錯誤` (HTTP 302) and SHALL NOT set a session cookie
