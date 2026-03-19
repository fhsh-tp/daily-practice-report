## MODIFIED Requirements

### Requirement: User list API returns paginated user records

The system SHALL provide `GET /admin/users` returning a paginated list of all users. The endpoint MUST require `MANAGE_USERS` permission. Response MUST include `id`, `username`, `display_name`, `name`, `email`, `permissions`, `identity_tags`, `tags`, and `student_profile` (if present) for each user. The endpoint SHALL support `page` and `page_size` query parameters, defaulting to page 1 and page size 20.

#### Scenario: Admin fetches user list

- **WHEN** a user with `MANAGE_USERS` permission sends `GET /admin/users`
- **THEN** the system SHALL return HTTP 200 with a list of user objects including `name`, `email`, `identity_tags`, and `student_profile` fields alongside existing fields

#### Scenario: Unauthorized request is rejected

- **WHEN** a user without `MANAGE_USERS` permission sends `GET /admin/users`
- **THEN** the system SHALL return HTTP 403

---

### Requirement: Single user read API

The system SHALL provide `GET /admin/users/{id}` returning the full user record for the given ID. The endpoint MUST require `MANAGE_USERS` permission. The response MUST include `name`, `email`, `identity_tags`, and `student_profile`. If the user does not exist, the system MUST return HTTP 404.

#### Scenario: Admin reads existing user

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/{id}` for an existing user
- **THEN** the system SHALL return HTTP 200 with the full user record including `name`, `email`, `identity_tags`, and `student_profile`

#### Scenario: Non-existent user returns 404

- **WHEN** `GET /admin/users/{id}` is called with an ID that does not exist
- **THEN** the system SHALL return HTTP 404

---

### Requirement: User update API

The system SHALL provide `PUT /admin/users/{id}` to update `display_name`, `name`, `email`, `permissions`, `identity_tags`, `tags`, and `student_profile`. The endpoint MUST require `MANAGE_USERS` permission. Username MUST NOT be changed via this endpoint. Password update SHALL be performed via a separate field `new_password`; if absent, the password MUST remain unchanged.

#### Scenario: Admin updates user identity tags and real name

- **WHEN** a user with `MANAGE_USERS` sends `PUT /admin/users/{id}` with valid `name`, `email`, and `identity_tags`
- **THEN** the system SHALL update those fields and return HTTP 200 with the updated record

#### Scenario: Admin updates student profile fields

- **WHEN** a user with `MANAGE_USERS` sends `PUT /admin/users/{id}` with a valid `student_profile` object
- **THEN** the system SHALL update `student_profile.class_name` and `student_profile.seat_number` accordingly

#### Scenario: Password unchanged when new_password absent

- **WHEN** `PUT /admin/users/{id}` is submitted without `new_password`
- **THEN** the user's `hashed_password` MUST remain unchanged

---

### Requirement: CSV batch import API

The system SHALL provide `POST /admin/users/import` accepting a multipart file upload of a CSV. The student CSV MUST support columns: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags` (semicolon-separated, optional), `class_name` (optional), `seat_number` (optional). The staff/teacher CSV MUST support: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags` (optional). The endpoint MUST require `MANAGE_USERS` permission. The `preset` column MUST match a defined preset name. The `identity_tag` column MUST match a valid `IdentityTag` value. Rows with invalid preset, invalid identity_tag, or duplicate username SHALL be skipped and reported. The response MUST return `{"success": N, "failed": [{"row": N, "reason": "..."}]}`.

#### Scenario: Valid student CSV import

- **WHEN** a user with `MANAGE_USERS` uploads a valid student CSV file
- **THEN** all valid rows SHALL be created as new users with the correct `identity_tags` and `student_profile` populated, and the response SHALL report the success count

#### Scenario: Invalid identity_tag rows are skipped

- **WHEN** a CSV row contains an unrecognized identity_tag value
- **THEN** that row MUST be skipped and reported in the `failed` list with reason "Unknown identity tag"

#### Scenario: Duplicate username rows are skipped

- **WHEN** a CSV row contains a username that already exists
- **THEN** that row MUST be skipped and reported in the `failed` list with reason "Username already exists"

---

## ADDED Requirements

### Requirement: User profile visibility is controlled by viewer identity

The system SHALL apply visibility rules when returning user data in non-admin contexts. The rules SHALL be enforced via distinct Pydantic response schemas:

- `UserPublicView`: exposes only `id` and `display_name`
- `UserStaffView`: exposes `id`, `display_name`, `name`, `email`, `identity_tags`, and `student_profile`
- `UserAdminView`: exposes all fields (used by admin endpoints)

The viewer's `identity_tags` SHALL determine which schema is applied: viewers with `TEACHER` or `STAFF` identity SHALL receive `UserStaffView`; all other authenticated viewers SHALL receive `UserPublicView`.

#### Scenario: Student views another student's profile

- **WHEN** a user with identity tag `STUDENT` requests another user's profile in a non-admin context
- **THEN** the system SHALL return only `id` and `display_name`

#### Scenario: Teacher views a student's profile

- **WHEN** a user with identity tag `TEACHER` requests a student's profile in a non-admin context
- **THEN** the system SHALL return `id`, `display_name`, `name`, `email`, `identity_tags`, and `student_profile`

#### Scenario: Admin endpoint always returns full profile

- **WHEN** any user with `MANAGE_USERS` requests a user's profile via `GET /admin/users/{id}`
- **THEN** the system MUST return the full `UserAdminView` regardless of identity tags

---

### Requirement: Authenticated user can update own display name

The system SHALL provide `PUT /auth/profile` allowing an authenticated user to update only their `display_name`. All other fields MUST be ignored in this endpoint. The endpoint MUST reject unauthenticated requests with HTTP 401.

#### Scenario: User updates own display name

- **WHEN** an authenticated user sends `PUT /auth/profile` with a new `display_name`
- **THEN** the system SHALL update only `display_name` and return HTTP 200 with the updated value

#### Scenario: User cannot change name via profile endpoint

- **WHEN** an authenticated user sends `PUT /auth/profile` including a `name` field
- **THEN** the system MUST ignore the `name` field and leave it unchanged

---

### Requirement: CSV batch import template download

The system SHALL provide two downloadable CSV template files via `GET /admin/users/import/template?type=student` and `GET /admin/users/import/template?type=staff`. Each response MUST have `Content-Type: text/csv` and `Content-Disposition: attachment` headers. The student template MUST include columns: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags`, `class_name`, `seat_number`. The staff template MUST include columns: `username`, `password`, `display_name`, `name`, `email`, `identity_tag`, `preset`, `tags`.

#### Scenario: Download student CSV template

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/import/template?type=student`
- **THEN** the system SHALL return a CSV file with the student column headers and one example row

#### Scenario: Download staff CSV template

- **WHEN** a user with `MANAGE_USERS` sends `GET /admin/users/import/template?type=staff`
- **THEN** the system SHALL return a CSV file with the staff column headers and one example row
