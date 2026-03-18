## ADDED Requirements

### Requirement: Protocol definitions for extension points

The system SHALL define four Python Protocols in `src/extensions/protocols/`: `AuthProvider`, `RewardProvider`, `BadgeTrigger`, and `SubmissionValidator`. Each Protocol SHALL specify the exact method signatures that implementors MUST satisfy.

#### Scenario: Protocol checked at registration

- **WHEN** an implementation is registered that does not satisfy the Protocol interface
- **THEN** the ExtensionRegistry SHALL raise a TypeError at registration time

### Requirement: ExtensionRegistry singleton

The system SHALL provide an `ExtensionRegistry` class instantiated as a module-level singleton. The registry SHALL allow registering and retrieving implementations by protocol type and key string.

#### Scenario: Implementation registered and retrieved

- **WHEN** an implementation is registered with a key under a protocol type
- **THEN** `registry.get(ProtocolType, key)` SHALL return that implementation

#### Scenario: Unknown key raises error

- **WHEN** `registry.get(ProtocolType, key)` is called with an unregistered key
- **THEN** the registry SHALL raise a KeyError

### Requirement: Startup registration in lifespan

All default implementations SHALL be registered in the FastAPI lifespan function before the application begins handling requests. Extensions SHALL be registered after defaults, allowing overrides.

#### Scenario: Default providers registered at startup

- **WHEN** the FastAPI application starts
- **THEN** all default implementations (LocalAuthProvider, CheckinRewardProvider, SubmissionRewardProvider, ConsecutiveCheckinTrigger, SubmissionCountTrigger) SHALL be available in the registry before the first request is handled

### Requirement: FastAPI dependency injection via registry

The system SHALL provide FastAPI `Depends` factory functions that retrieve implementations from the registry. Routers and services SHALL use these factories rather than importing implementations directly.

#### Scenario: Router uses injected provider

- **WHEN** a router endpoint declares a dependency on `get_reward_provider()`
- **THEN** FastAPI SHALL inject the registered RewardProvider for that event type

### Requirement: Test registry helper

The system SHALL provide a `TestRegistry` helper that replaces the singleton registry with a clean instance for test isolation. After the test, the original registry SHALL be restored.

#### Scenario: Test replaces registry

- **WHEN** a test uses the `TestRegistry` context manager
- **THEN** the registry within that context SHALL be a fresh instance with only explicitly registered test implementations
- **THEN** after the context exits, the original registry SHALL be restored
