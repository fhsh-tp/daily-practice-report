## ADDED Requirements

### Requirement: Migration script structure

Each database migration SHALL be a standalone Python file under `scripts/migrations/` named with format `YYYYMMDD_NNN_description.py`. Each migration file MUST implement `async def forward() -> None` and `async def backward() -> None`.

#### Scenario: Migration file structure valid

- **WHEN** the migration CLI loads a migration file
- **THEN** the file SHALL be importable and SHALL expose both `forward` and `backward` coroutines

### Requirement: Migration tracking collection

The system SHALL maintain a `migrations` collection in MongoDB recording which migrations have been applied. Each document MUST store: migration filename, applied timestamp, and direction (forward/backward).

#### Scenario: Applied migration recorded

- **WHEN** a migration's `forward()` runs successfully
- **THEN** the system SHALL insert a record into the `migrations` collection with the filename and timestamp

### Requirement: Migration CLI

The system SHALL provide `scripts/migrate.py` as a CLI entry point. It MUST support: `init` (create tracking collection), `up` (apply all pending migrations in order), `down` (roll back the last applied migration), and `status` (list applied and pending migrations).

#### Scenario: `migrate.py up` applies pending migrations

- **WHEN** `migrate.py up` is invoked and there are pending migration files not in the tracking collection
- **THEN** the CLI SHALL run each pending migration's `forward()` in filename order and record each one

#### Scenario: `migrate.py down` rolls back last migration

- **WHEN** `migrate.py down` is invoked
- **THEN** the CLI SHALL run the most recently applied migration's `backward()` and remove its tracking record

#### Scenario: `migrate.py status` shows state

- **WHEN** `migrate.py status` is invoked
- **THEN** the CLI SHALL print a list of all migration files with their applied/pending status

### Requirement: Migration idempotency check

The CLI SHALL refuse to apply a migration that is already recorded in the tracking collection. Running `up` when all migrations are applied SHALL succeed without error and print a message.

#### Scenario: Already-applied migration skipped

- **WHEN** `migrate.py up` is invoked and all migrations are already applied
- **THEN** the CLI SHALL print "Nothing to migrate" and exit with code 0
