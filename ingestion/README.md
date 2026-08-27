# BusyBoard ingestion service

The ingestion service subscribes to BusyBoard MQTT telemetry, validates topics and payloads, applies session rules, commits accepted data to SQLite, and queues separate best-effort writes to Supabase/Postgres.

See [the system architecture](../docs/architecture.md) for cloud failure semantics and [the MQTT contract](../docs/contracts/mqtt.md) for authoritative topic/payload definitions.

## Requirements

- Python with `venv` and `pip` support;
- a Mosquitto-compatible broker available at `localhost:1883`;
- optional Supabase/Postgres connectivity for cloud publication.

Dependencies are currently listed without version pins in `requirements.txt`.

## Environment

The service loads `ingestion/.env` when present. The file is gitignored.

| Variable | Required | Purpose |
|---|---|---|
| `MQTT_USER` | No | Broker username; defaults to an empty string |
| `MQTT_PASSWORD` | No | Broker password; defaults to an empty string |
| `SUPABASE_DB_URL` | No | Direct Postgres connection string; cloud publication is disabled when absent |

MQTT host and port are currently fixed in code as `localhost` and `1883`.

## Install and run

From `ingestion/`, create or select a virtual environment, then run:

```bash
python -m pip install -r requirements.txt
python app.py
```

`app.py` initializes `busyboard.db` from the tracked `schema.sql`, starts cloud publication when configured and reachable, then enters the MQTT loop.

## Modules

| File | Responsibility |
|---|---|
| `app.py` | Process entry point |
| `mqtt_client.py` | Broker connection, subscriptions, and callbacks |
| `router.py` | Topic/JSON parsing and event dispatch |
| `validators.py` | Payload validation |
| `handlers.py` | Session/device business rules and transaction orchestration |
| `repositories.py` | SQLite queries and writes |
| `db.py` / `schema.sql` | SQLite connection and tracked schema |
| `cloud_publisher.py` | In-memory asynchronous cloud queue and worker |
| `supabase_db.py` | Direct Postgres connection |
| `supabase_repositories.py` | Postgres queries and writes |
| `utils.py` | Timestamp, JSON, and topic helpers |
| `constants.py` | Topic, event, device, and session constants |

The detailed session lifecycle and local/cloud differences are documented in [the data model](../docs/data-model.md).

## Testing

Run from `ingestion/`:

```bash
python -m pytest
```

Tests cover helpers, validation, routing, SQLite repositories, and local handlers. They do not verify the cloud publisher, Postgres repositories, a real broker, or live Supabase behavior. See [testing and verification](../docs/testing.md).

## Persistence workflow

Accepted messages commit to SQLite before a background publisher performs the corresponding Postgres operations. If cloud publication is not configured or available during startup, ingestion continues with local persistence.

Changes affecting persistence should verify both repository implementations and the dashboard fields they support. See [the architecture](../docs/architecture.md) and [data model](../docs/data-model.md).
