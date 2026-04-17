# BusyBoard

A full-stack IoT system that captures physical interactions from a custom hardware device and streams them as structured telemetry through an event-driven pipeline, ending in a real-time web dashboard.

Built to explore how physical interfaces can become reliable data sources in connected systems.

**Live dashboard:** [busyboard-telemetry.vercel.app](https://busyboard-telemetry.vercel.app/)

---

## What it does

A physical board with 11 toggle switches and an accelerometer sits on a desk. Every interaction, a switch flip, a session starting, a device going offline, is captured by embedded firmware, published over MQTT, ingested by a Python server, persisted to a database, and streamed live to a web dashboard. The entire chain from physical input to browser UI happens in under a second.

---

## Stack

| Layer            | Technology                           |
| ---------------- | ------------------------------------ |
| Firmware         | C++ / Arduino on ESP32               |
| Motion sensor    | MPU6050 (I2C)                        |
| Message broker   | Mosquitto (MQTT)                     |
| Ingestion server | Python                               |
| Local database   | SQLite                               |
| Cloud database   | Supabase (Postgres)                  |
| Dashboard        | Next.js 14, TypeScript, Tailwind CSS |
| Realtime         | Supabase Realtime (postgres_changes) |
| Deployment       | Vercel                               |
| Rate limiting    | Upstash Redis                        |

---

## Architecture

```
ESP32 firmware
    |  MQTT over WiFi
    v
Mosquitto broker
    |
    v
Python ingestion server
    |-- Router        parses topics, routes messages
    |-- Validators    enforces payload integrity
    |-- Handlers      applies session and event logic
    +-- Repositories  writes to SQLite + Supabase
            |
            |-- SQLite (local, primary)
            +-- Supabase / Postgres (cloud, sync)
                    |
                    v  postgres_changes
              Next.js dashboard
                    |-- Switch grid    live toggle state
                    |-- Device list    online/offline status
                    |-- Session list   searchable, paginated
                    +-- Event table    full interaction audit log
```

The ingestion server runs at the edge alongside the broker and owns all business logic. The dashboard is a pure read layer that never writes to the database.

---

## MQTT topic structure

```
busyboard/{deviceId}/events
busyboard/{deviceId}/switch/{switchName}
busyboard/{deviceId}/status
```

Topic determines message type. Payload refines behavior. This separation keeps the broker dumb and the ingestion layer in control.

---

## Session model

Every physical interaction is scoped to a session, a continuous period of activity on the board.

```
device_connected -> session_started -> switch_changed (xN) -> session_ended
```

Each session captures start time, end time, duration, interaction count, and which switches were used. Ghost sessions caused by dropped connections are automatically closed by a pg_cron job running in Postgres every minute.

---

## Data model

```
devices       device_id, status, first_seen_at, last_seen_at
sessions      session_id, device_id, started_at, ended_at, duration_ms, interaction_count, status
events        id, device_id, session_id, event_type, event_ts, topic, payload_json
switch_events id, session_id, device_id, switch_name, value, event_ts
```

session_id is a YYYYMMDDHHmmss timestamp string. Human-readable and naturally sortable without an additional created_at column.

---

## Key design decisions

**Edge-first.** The ingestion server processes and persists locally before syncing to the cloud. The dashboard degrades gracefully if Supabase is unreachable. The ingestion pipeline does not.

**Validate before writing.** Every MQTT payload passes through a validator before touching the database. Invalid or malformed messages are logged and discarded.

**Idempotent operations.** Handlers are safe to replay. Duplicate messages produce the same result as a single message.

**Strict separation of concerns.** Router routes, validators validate, handlers apply logic, repositories write data. No layer reaches into another's responsibility.

**Read-only dashboard.** The Next.js app holds no write path to the database. Row Level Security on Supabase enforces this at the database level regardless of what the client sends.

---

## Dashboard

Deployed on Vercel and connected to Supabase for both historical data and live updates.

**Live switches** reflect the current ON/OFF state of all 11 switches. Seeded from the latest switch event per switch on load, then updated in real time via Supabase Realtime.

**Device status** shows each device as online or offline and updates the moment the ingestion server publishes a status change.

**Session list** is paginated and searchable by session ID, date, or time. Filters out empty sessions. New sessions appear at the top automatically when they start.

**Event audit table** shows every interaction in a session in chronological order: absolute timestamp, relative offset from session start, source device, event type, value, and gap since the previous event. Gaps over 60 seconds are highlighted.

Live sessions update in real time as switches are toggled. New rows prepend to the table without a page refresh.

---

## Security

**Row Level Security.** The Supabase anon key is read-only. The service role key used by the ingestion server is never exposed to the client.

**Rate limiting.** Upstash Redis sliding window on all /api routes via Next.js middleware. 60 requests per minute per IP.

**Input validation.** Session IDs are validated against a 14-digit pattern before reaching Supabase. Search inputs are sanitized and length-capped.

**MQTT authentication.** The broker requires username and password. ACLs restrict publish and subscribe permissions per client.

---

## Testing

Full pytest coverage across the ingestion server:

- test_utils.py — timestamp normalization, payload parsing
- test_validators.py — payload integrity, edge cases
- test_router.py — topic routing with a mocked broker
- test_repositories.py — database operations against a real SQLite instance
- test_handlers.py — full session lifecycle

---

## Roadmap

- Subscriber devices: buzzer and LED reactions to MQTT events
- Analytics: session heatmaps, switch usage patterns over time
- Remote broker with TLS and full cloud deployment

---

## Project structure

```
firmware/
  sketch.ino              ESP32 Arduino sketch

ingestion/
  app.py                  Entry point
  router.py               Topic parser and dispatcher
  validators.py           Payload validation
  handlers.py             Session and event business logic
  repositories.py         SQLite + Supabase writes
  utils.py                Timestamp normalization, helpers

tests/
  conftest.py
  test_utils.py
  test_validators.py
  test_router.py
  test_repositories.py
  test_handlers.py

dashboard/
  src/
    app/
      api/sessions/
        route.ts          GET /api/sessions — paginated session list
        [id]/route.ts     GET /api/sessions/:id — session + audit rows
      layout.tsx          Root layout, bootstraps RealtimeProvider
      page.tsx            Dashboard entry with Suspense boundary + shell, holds selected session state and URL sync
      globals.css
    components/
      layout/
        Topbar.tsx        Logo and connection status
        HardwareState.tsx Switch grid and device list banner
      switches/
        SwitchGrid.tsx    Live read-only switch state
      devices/
        DeviceList.tsx    Device online/offline status
      sessions/
        SessionList.tsx   Searchable paginated session index
        SessionItem.tsx   Individual session row
      events/
        EventPanel.tsx    Fetches and renders selected session
        EventStats.tsx    Session header and stat strip
        EventTable.tsx    Chronological audit table
    context/
      RealtimeContext.tsx Single Supabase Realtime channel, shared app-wide
    lib/
      supabase.ts         Browser client
      supabase-server.ts  Server client for API routes
      utils.ts            Timestamp formatting, gap calculation
      styles.ts           Shared Tailwind design tokens
    types/
      index.ts            Shared TypeScript types
    middleware.ts         Upstash rate limiting on /api routes
```
