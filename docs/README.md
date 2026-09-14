# BusyBoard engineering documentation

This directory contains engineering references shared across BusyBoard subsystems. Local setup and module orientation remain in each subsystem README; coding-agent instructions remain in the nearest `AGENTS.md`.

## Documentation map

| Document | Responsibility |
|---|---|
| [Architecture](architecture.md) | Runtime components, ownership, data flow, and deployment boundaries |
| [MQTT contract](contracts/mqtt.md) | Authoritative description of currently supported topics and payloads |
| [Data model](data-model.md) | Entities, session lifecycle, local/cloud persistence, and dashboard projections |
| [Testing](testing.md) | Current verification commands and checks by subsystem |

## Documentation ownership

- MQTT topics and payload fields are documented in [the MQTT contract](contracts/mqtt.md). Other documents link to it rather than repeat it.
- The tracked [`ingestion/schema.sql`](../ingestion/schema.sql) defines the SQLite schema.
- Local installation and run commands belong in subsystem READMEs.
- Safe modification rules and verification expectations belong in AGENTS files.
- Deployment-specific Supabase, Vercel, and broker configuration is managed outside this repository unless a tracked configuration file says otherwise.

The documents describe the current implementation. Future designs should be documented after the corresponding behavior is implemented or an architectural decision is accepted.
