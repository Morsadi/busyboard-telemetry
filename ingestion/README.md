# BusyBoard Ingestion Server

Python MQTT ingestion server. Subscribes to a local Mosquitto broker, validates payloads, applies session lifecycle logic, and dual-writes to SQLite (local) and Supabase (cloud).

---

## File Structure

```
ingestion/
├── app.py             # Entry point: MQTT client setup, dispatch loop
├── router.py          # Topic parser and message dispatcher
├── validators.py      # Payload integrity and shape checks
├── handlers.py        # Session lifecycle and event business logic
├── repositories.py    # SQLite + Supabase writes
└── utils.py           # Timestamp normalization, helpers

tests/
├── conftest.py
├── test_utils.py         # Timestamp normalization, payload parsing
├── test_validators.py    # Payload integrity, edge cases
├── test_router.py        # Topic routing with mocked broker
├── test_repositories.py  # DB operations against real SQLite
└── test_handlers.py      # Full session lifecycle
```

---

## Pipeline

```
MQTT message
  → Router         parses topic, picks message type
  → Validator      enforces payload shape
  → Handler        applies session/event logic
  → Repository     writes to SQLite + Supabase
```

Each layer has one job. The router never touches the database. The repository never parses topics. Idempotent throughout. Duplicate messages produce the same result as a single message.

---

## Subscribed Topics

```
busyboard/{deviceId}/events
busyboard/{deviceId}/switch/{switchName}
busyboard/{deviceId}/status
```

Topic determines message type. Payload refines behavior.

---

## Session Model

Every interaction is scoped to a session: a continuous period of activity on the board.

```
device_connected → session_started → switch_changed (×N) → session_ended
```

Sessions capture `started_at`, `ended_at`, `duration_ms`, `interaction_count`, and which switches were used. Session IDs are `YYYYMMDDHHmmss` strings, which are human-readable and naturally sortable.

**Ghost sessions** (caused by ungraceful disconnects) are auto-closed by a `pg_cron` job in Postgres running every minute. The MQTT broker's LWT publishes the offline status that triggers cleanup.

---

## Storage

| Store | Role |
|-------|------|
| SQLite | Local primary store. All writes go here first. |
| Supabase (Postgres) | Cloud sync for the dashboard. Writes happen in a background daemon thread so MQTT processing is never blocked. |

If Supabase is unreachable, ingestion continues uninterrupted. The local store is always source of truth.

---

## Schema

```
devices        device_id, status, first_seen_at, last_seen_at
sessions       session_id, device_id, started_at, ended_at, duration_ms,
               interaction_count, status
events         id, device_id, session_id, event_type, event_ts, topic,
               payload_json
switch_events  id, session_id, device_id, switch_name, value, event_ts
```

---

## Design Principles

- **Validate before writing.** Malformed payloads are logged and discarded. They never reach the database.
- **Idempotent handlers.** Replay-safe. Same input produces same outcome regardless of how many times it arrives.
- **Edge-first.** SQLite is primary; Supabase is sync. The dashboard degrades if the cloud is down; ingestion does not.
- **Strict separation of concerns.** Router routes, validators validate, handlers apply logic, repositories write. No layer reaches into another's responsibility.

---

## Testing

Full pytest coverage across every layer. Repository tests run against a real SQLite instance; router tests use a mocked broker.

---

## Related Components

| Component | Role | Dir |
|-----------|------|------|
| BusyBoard Firmware | Publishes the events this server consumes | [`Link`](../firmware/Busyboard/README.md) |
| Dashboard | Reads from the Supabase tables this server writes | [`Link`](../dashboard/README.md) |