## ADDED Requirements

### Requirement: Teacher deduct entry type in point ledger

The points system SHALL support a `teacher_deduct` entry type in `PointLedger` to record teacher-initiated point deductions.

#### Scenario: Deduction recorded with entry type

- **WHEN** a teacher deducts points from a student
- **THEN** the system SHALL create a PointLedger entry with `entry_type` set to `"teacher_deduct"`, including the deduction amount (negative) and reason

#### Scenario: Student balance reflects deduction

- **WHEN** a `teacher_deduct` entry is created
- **THEN** the student's point balance returned by `get_balance()` SHALL decrease by the deducted amount
