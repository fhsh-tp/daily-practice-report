## ADDED Requirements

### Requirement: PERMISSION_SCHEMA defines domain-to-flag mapping

The system SHALL define a module-level constant `PERMISSION_SCHEMA` in `src/core/auth/permissions.py` as a list of dicts, each with keys `domain` (str), `read` (Permission), and `write` (Permission). This structure MUST cover all five domains: Self, Class, Task, User, and System. When a developer adds a new `Permission` flag, they MUST add it to `PERMISSION_SCHEMA` to make it visible in the admin UI.

#### Scenario: PERMISSION_SCHEMA covers all existing domains

- **WHEN** `PERMISSION_SCHEMA` is imported from `permissions.py`
- **THEN** it MUST contain exactly one entry per domain: Self, Class, Task, User, System

#### Scenario: New flag added to schema appears in API response

- **WHEN** a developer adds a new `Permission` flag and includes it in `PERMISSION_SCHEMA`
- **THEN** `GET /admin/permissions/schema` MUST return the updated domain entry including the new flag value

---

### Requirement: Permission schema API endpoint

The system SHALL provide `GET /admin/permissions/schema` returning the serialized `PERMISSION_SCHEMA` as a JSON array. Each element MUST include `domain` (string), `read` (integer bitmask), and `write` (integer bitmask). The endpoint MUST require `MANAGE_USERS` permission.

#### Scenario: Schema endpoint returns domain list

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/permissions/schema`
- **THEN** the system SHALL return HTTP 200 with a JSON array where each object has `domain`, `read`, and `write` integer fields

---

### Requirement: Permission presets API endpoint

The system SHALL provide `GET /admin/permissions/presets` returning all named Role Presets as a JSON array. Each element MUST include `name` (string, e.g. `"STUDENT"`) and `value` (integer). The endpoint MUST require `MANAGE_USERS` permission.

#### Scenario: Presets endpoint returns all presets

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/permissions/presets`
- **THEN** the system SHALL return HTTP 200 with a JSON array containing at minimum `STUDENT`, `TEACHER`, `USER_ADMIN`, `SYS_ADMIN`, and `SITE_ADMIN` entries
