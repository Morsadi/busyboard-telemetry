# Data model and session behavior

This document describes the entities and lifecycle shared by ingestion and the dashboard. The tracked SQLite schema, repository implementations, tests, and dashboard queries are the implementation references.

## Schema ownership

- [`ingestion/schema.sql`](../ingestion/schema.sql) defines the SQLite tables and constraints.
- `ingestion/repositories.py` implements SQLite operations.
- `ingestion/supabase_repositories.py` implements the corresponding Postgres operations.
- Dashboard API and Realtime code define the cloud fields consumed by the UI.
- Production Supabase migrations and policies are managed outside this repository.

## Entities

### Devices

One row represents each MQTT device observed by ingestion:

- `device_id` is the primary identifier;
- `first_seen_at` is retained from the first insert;
- `last_seen_at` and `status` are updated on later messages;
- supported statuses are `online` and `offline`.

Handlers use ingestion receipt time for device-presence timestamps.

### Sessions

A session represents a period of BusyBoard activity. It stores the device, start/end timestamps, duration, interaction count, and lifecycle status.

Ingestion and the SQLite schema use `active` and `ended`. The current dashboard detail route expects a 14-digit session ID.

### Events

The events table is the general audit log for accepted `device_connected`, `session_started`, `switch_changed`, and `session_ended` messages. Each row stores event and receipt timestamps, the MQTT topic, and the serialized payload.

Device-level events may have no session ID. `alarm_triggered` is not currently accepted by the ingestion router.

### Switch events

Switch events provide a query-oriented projection containing session, device, switch name, value, and timestamp.

SQLite also stores a unique `event_id` reference to the corresponding general event row. The current Postgres write path stores the switch projection without that field.

## Session lifecycle

```text
first motion or switch activity
    -> session_started
    -> zero or more switch_changed messages
    -> five seconds without motion/switch activity
    -> session_ended
```

Motion starts or extends a firmware session but does not produce a stored interaction row.

Ingestion applies these rules:

- `session_started` creates a missing active session;
- `switch_changed` creates a missing active session using the switch timestamp;
- `session_ended` for an unknown session is ignored;
- lifecycle or switch messages do not reopen an ended session;
- device offline status updates the device without closing active sessions.

## Identity and timestamps

Firmware uses a 14-digit UTC session-start timestamp as the current `sessionId`. The value is stored as the session primary key and is validated by the dashboard detail route.

Ingestion accepts compact and ISO 8601 event timestamps, normalizes them to UTC ISO 8601, and persists the normalized value. SQLite stores timestamps as text; Postgres operations use timestamp-compatible values.

Changes to session identity or timestamp formats require coordinated updates to firmware, ingestion, schemas, tests, dashboard routes, and [the MQTT contract](contracts/mqtt.md).

## Interaction counts

Ingestion increments the active session's interaction count for each accepted switch change. On `session_ended`, the firmware-provided `interactionCount` becomes the stored final count.

## Local and cloud persistence

| Concern | SQLite | Supabase/Postgres path |
|---|---|---|
| Write order | First, in the handler transaction | Later, through the background publisher |
| Implementation | `schema.sql` and `repositories.py` | `supabase_repositories.py` and deployed cloud schema |
| Switch/event link | `switch_events.event_id` | Switch projection does not include `event_id` |
| Dashboard reads | No | Yes |

Because cloud publication is asynchronous, persistence work should validate both repository paths and the dashboard fields they support.

## Dashboard projections

- The session-list API queries sessions plus related switch names and calculates a distinct `switch_count`.
- The session-detail API combines switch rows with `session_started` and `session_ended` event rows.
- The browser seeds the shared switch grid from the newest cloud row for each switch name.
- Realtime device, event, and switch inserts update UI state or trigger refetches.

Deployments must provide compatible Supabase tables, read policies, write protection, and Realtime publication.
