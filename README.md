# BusyBoard

A full-stack IoT system that captures physical interactions from a custom hardware device and streams them as structured telemetry through an event-driven pipeline, ending in a real-time web dashboard.

**Live dashboard:** [busyboard-telemetry.vercel.app](https://busyboard-telemetry.vercel.app/)

---

## What It Does

A physical board with 11 toggle switches and an accelerometer sits on a desk. Every interaction is captured by embedded firmware, published over MQTT, ingested by a Python server, persisted to a database, and streamed live to a web dashboard. The full chain from physical input to browser UI happens in under a second.

---

## Architecture

```
ESP32 Firmware
    │  MQTT over WiFi
    ▼
Mosquitto Broker
    │
    ▼
Python Ingestion Server
    │  SQLite (local) + Supabase (cloud sync)
    ▼
Next.js Dashboard
```

Three independent components, each with its own repository.

---

## Components

| Folder | Description |
|--------|-------------|
| [`firmware/Busyboard`](./firmware/Busyboard) | ESP32 firmware. Reads 11 switches and an MPU-6050, publishes events over MQTT. |
| [`firmware/Buzzer`](./firmware/Buzzer) | ESP32 companion device. Subscribes to BusyBoard MQTT events and plays beep patterns on status changes and switch triggers. |
| [`ingestion/`](./ingestion) | Python MQTT subscriber. Validates, applies session logic, dual-writes to SQLite and Supabase. |
| [`dashboard/`](./dashboard) | Next.js read-only dashboard. Live switch state, device status, session history, audit logs. |

---

## Stack

| Layer | Technology |
|-------|------------|
| Firmware | C++ / Arduino on ESP32 |
| Motion sensor | MPU-6050 (I2C) |
| Message broker | Mosquitto (MQTT) |
| Ingestion | Python |
| Local store | SQLite |
| Cloud store | Supabase (Postgres) |
| Realtime | Supabase Realtime (`postgres_changes`) |
| Dashboard | Next.js 14, TypeScript, Tailwind CSS |
| Rate limiting | Upstash Redis |
| Hosting | Vercel |