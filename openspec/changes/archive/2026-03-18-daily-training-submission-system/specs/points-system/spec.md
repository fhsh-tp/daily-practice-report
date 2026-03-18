## ADDED Requirements

### Requirement: Points awarded on check-in and submission

The system SHALL award points to a student when they successfully check in or submit a daily task. The point amounts SHALL be configurable per class by the teacher. Points SHALL be recorded as individual transactions with a reason, source event, and timestamp.

#### Scenario: Points awarded after check-in

- **WHEN** a student successfully checks in
- **THEN** the system SHALL create a point transaction crediting the configured check-in points to the student

#### Scenario: Points awarded after task submission

- **WHEN** a student successfully submits a daily task
- **THEN** the system SHALL create a point transaction crediting the configured submission points to the student

### Requirement: Teacher revokes points

Teachers SHALL be able to deduct points from a student's balance by creating a negative point transaction. The teacher MUST provide a reason for the deduction. The student's balance MUST NOT go below zero as a result of a single revocation (the revocation amount SHALL be capped at the student's current balance).

#### Scenario: Teacher revokes points with reason

- **WHEN** a teacher submits a point deduction with a reason and amount
- **THEN** the system SHALL create a negative point transaction and update the student's balance accordingly

#### Scenario: Revocation capped at current balance

- **WHEN** a teacher attempts to revoke more points than the student currently has
- **THEN** the system SHALL deduct only the student's current balance and log the capped amount

### Requirement: Student views point history

Students SHALL be able to view their complete point transaction history, including amount, reason, source event, and timestamp for each entry.

#### Scenario: Student views transaction list

- **WHEN** a student navigates to their points page
- **THEN** the system SHALL display a chronological list of all their point transactions

### Requirement: RewardProvider extension point

The system SHALL define a `RewardProvider` Protocol with method `award(event: RewardEvent) -> PointTransaction | None`. All registered providers SHALL be invoked for each reward-triggering event. The default providers (CheckinRewardProvider, SubmissionRewardProvider) SHALL be registered at startup.

#### Scenario: Custom reward provider registered

- **WHEN** a custom RewardProvider is registered in the ExtensionRegistry at startup
- **THEN** the system SHALL invoke it for every reward event alongside the default providers

### Requirement: Point balance computed from transactions

A student's point balance SHALL be the sum of all their point transactions. There SHALL be no separate balance field; the balance MUST always be computed from the transaction log.

#### Scenario: Balance reflects all transactions

- **WHEN** a student's balance is requested
- **THEN** the system SHALL return the sum of all their point transaction amounts (positive and negative)
