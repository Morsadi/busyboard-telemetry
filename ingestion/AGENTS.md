# Ingestion agent instructions

These instructions apply to `ingestion/`.

Read the local README plus:

- [System architecture](../docs/architecture.md)
- [Current MQTT contract](../docs/contracts/mqtt.md)
- [Data model and session behavior](../docs/data-model.md)
- [Testing and verification](../docs/testing.md)

## Architecture boundary

Preserve the current dependency direction unless the task explicitly changes architecture:

```text
MQTT input -> router -> validator -> handler -> repository -> persistence
```

Keep broker concerns out of transformation/persistence logic where practical. Handlers own business rules and transaction orchestration; repositories own database operations.

## Input and persistence safety

- Treat topics, JSON, field values, timestamps, ordering, and delivery uniqueness as untrusted.
- One malformed message should not terminate the MQTT service.
- Do not silently coerce malformed telemetry into valid-looking records.
- SQLite commits before a separate asynchronous cloud operation; verify both paths for persistence changes.
- Do not add retry/replay without first defining stable deduplication behavior.
- Keep failure logs diagnosable without exposing credentials or connection strings.

## Schema and contract changes

Before changing a message, table, or row shape:

1. inspect both local and Postgres repositories and available schema evidence;
2. inspect firmware producers and Buzzer consumers;
3. inspect dashboard API/Realtime consumers;
4. inspect existing tests;
5. update the authoritative MQTT/data-model documentation and define compatibility.

Treat production Supabase provisioning as deployment-managed. Do not start persisting a previously unhandled event as unrelated cleanup.

## Verification

Use the commands in `ingestion/README.md`. For a behavior change, run the closest test first and then the full pytest suite.

Cloud-publisher or Postgres changes require direct focused coverage; passing SQLite tests alone does not verify cloud behavior. High-value missing scenarios are tracked in [testing documentation](../docs/testing.md).

## Current constraints

- MQTT delivery may repeat; do not introduce retry/replay behavior without explicit message-identity semantics.
- SQLite and Postgres use separate repositories and transaction boundaries.
- Session lifecycle and identity rules are shared with firmware and the dashboard; use the data-model documentation as the reference.

Keep changes limited to the requested behavior unless broader architectural work is explicit.
