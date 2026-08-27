# System architecture

BusyBoard is an IoT telemetry system with embedded publishers, MQTT transport, a Python ingestion service, local and cloud persistence, and a realtime web dashboard.

## Runtime topology

```text
BusyBoard ESP32
    -> Mosquitto over MQTT
    -> Python ingestion service
       -> SQLite transaction
       -> asynchronous cloud publication
          -> Supabase/Postgres
             -> Next.js API routes
             -> Supabase Realtime
                -> browser dashboard

Buzzer ESP32
    <- selected BusyBoard MQTT status/switch messages
    -> optional alarm event on MQTT
```

The dashboard reads Supabase/Postgres. It does not read the local SQLite database.

## Component responsibilities

### BusyBoard firmware

The BusyBoard sketch owns physical input and session creation. It polls 11 switches, samples the MPU-6050, starts or extends a session on switch or motion activity, and publishes device, session, and switch telemetry over MQTT.

Motion affects the session timer but does not create a switch-interaction row. Topic and payload details live in [the MQTT contract](contracts/mqtt.md).

### Buzzer firmware

The Buzzer sketch subscribes directly to one configured BusyBoard's status and two configured switch topics. It plays beep patterns for configured state transitions and may publish `alarm_triggered` on its own events topic.

The current ingestion router does not persist `alarm_triggered`; the Buzzer otherwise operates independently of Python ingestion.

### MQTT broker

Firmware and ingestion communicate through a Mosquitto-compatible broker. Firmware obtains broker settings from gitignored `secrets.h` files. Ingestion currently connects to `localhost:1883` and can load credentials from its environment.

Broker provisioning, TLS, and access-control configuration are deployment responsibilities.

### Ingestion service

The Python service subscribes to status, lifecycle-event, and switch-event patterns. Processing follows this dependency direction:

```text
MQTT callback -> topic/JSON parsing -> validation -> handler -> repository
```

Accepted messages are committed to SQLite first. A separate background worker publishes corresponding operations to Supabase/Postgres.

Cloud publication is asynchronous and uses a separate transaction boundary. Persistence changes should verify both local and cloud repository paths.

### Persistence

The local database is `ingestion/busyboard.db`, created from the tracked `ingestion/schema.sql`. It remains available when cloud publication is not configured.

Supabase/Postgres supplies the data read by the dashboard. The expected cloud row shapes are represented by the Postgres repositories and dashboard queries; project provisioning is managed outside this repository.

### Dashboard

The Next.js application queries Supabase from server code for device and session data. A shared browser Realtime channel listens for device updates/inserts, switch-event inserts, and event inserts.

The current UI presents a shared switch grid keyed by switch name, a device list, paginated sessions, and per-session event rows.

## Runtime behavior

- Malformed or unsupported MQTT messages are logged and discarded without stopping the MQTT loop.
- Device status messages update presence independently of session lifecycle messages.
- Device offline status does not close an active session in ingestion.
- If cloud publication is unavailable during startup, ingestion continues with local SQLite persistence.
- The dashboard requires Supabase connectivity for its data and realtime views.

## Deployment requirements

A deployed instance must provide:

- a reachable MQTT broker and device credentials;
- a Supabase/Postgres schema compatible with ingestion and dashboard queries;
- Supabase anonymous read policies and protection against anonymous writes;
- Realtime publication for the tables used by the browser;
- Upstash Redis configuration for dashboard API rate limiting;
- Vercel/dashboard and ingestion-host environment configuration.

These services are configured outside the repository's local source tree.
