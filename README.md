# BusyBoard

BusyBoard is a full-stack IoT telemetry project that records interactions with a custom ESP32-based control board and presents them in a live web dashboard.

The physical board has 11 toggle switches and an MPU-6050 motion sensor. Firmware publishes telemetry over MQTT, a Python service validates and persists it, and a Next.js dashboard reads the cloud data through Supabase.

**Live dashboard:** [busyboard-telemetry.vercel.app](https://busyboard-telemetry.vercel.app/)

## System overview

```text
BusyBoard ESP32 -> Mosquitto -> Python ingestion -> SQLite
                                      |
                                      -> Supabase/Postgres -> Next.js dashboard

Buzzer ESP32 <- selected BusyBoard MQTT messages
```

SQLite is committed first, and cloud publication runs asynchronously. Persistence changes should be verified in both paths. See [the architecture documentation](docs/architecture.md) for the complete runtime flow.

## Components

| Directory | Responsibility |
|---|---|
| [`firmware/`](firmware/README.md) | BusyBoard publisher and Buzzer subscriber firmware |
| [`ingestion/`](ingestion/README.md) | MQTT validation, session logic, SQLite persistence, and asynchronous Postgres publication |
| [`dashboard/`](dashboard/README.md) | Read-only-intended Next.js dashboard backed by Supabase |

## Getting started

There is not yet a one-command full-system development environment. Set up the component you need:

1. Start a Mosquitto-compatible broker reachable by the ESP32 devices and ingestion host.
2. Follow the [firmware setup](firmware/README.md) for hardware and credentials. The repository does not yet encode a reproducible firmware toolchain.
3. Follow the [ingestion setup](ingestion/README.md) to install Python dependencies, configure credentials, and run the subscriber.
4. Follow the [dashboard setup](dashboard/README.md) to configure Supabase and the Vercel deployment, then start the web application.

Do not commit `.env` files, firmware `secrets.h` files, local databases, or generated build output.

## Engineering documentation

- [Documentation index](docs/README.md)
- [System architecture](docs/architecture.md)
- [Current MQTT contract](docs/contracts/mqtt.md)
- [Data model and session behavior](docs/data-model.md)
- [Testing and verification](docs/testing.md)

Coding agents should also read the root [`AGENTS.md`](AGENTS.md) and the nearest scoped AGENTS file before modifying code.
