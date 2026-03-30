# BusyBoard Telemetry

**An IoT system that uses a physical busy board to capture real-world interactions and turn them into events that can trigger and control other connected devices using MQTT (Mosquitto).**

**This project explores how simple physical inputs like switches and movement can act as signals in a larger connected system, where actions are not just recorded but distributed and reacted to in real time. Each interaction is structured as telemetry, allowing it to be streamed, monitored, and used to coordinate behavior across multiple devices.**

**The goal is to bridge the gap between physical interfaces and modern event-driven architectures, building toward a system where hardware becomes a reliable source of real-time data that can power automation, monitoring, and responsive environments.**

---

## Overview

Captures physical interactions from a custom busy board and converts them into structured telemetry.

### Built with:
- ESP32 (firmware)
- MPU6050 (motion detection)
- Session-based event model
- NTP timestamps
- JSON output

### Designed for:
- MQTT publishing (Mosquitto)
- Real-time subscribers
- Data pipelines and dashboards

---

## Architecture (Current)

MQTT → Router → Validators → Handlers → Repositories → SQLite

- Router: parses topics and routes messages
- Validators: ensures payload integrity
- Handlers: applies business logic (sessions, events)
- Repositories: handles all database operations

---

## MQTT Topic Design

busyboard/{deviceId}/events  
busyboard/{deviceId}/switch/{switchName}  
busyboard/{deviceId}/status  

- Topic determines message type
- Payload refines behavior

---

## Supported Events

device_connected  
session_started  
switch_changed  
session_ended  

Status:
online / offline

---

## Data Model

- devices → device state (online/offline, timestamps)
- sessions → start/end, duration, interaction count
- events → raw event log
- switch_events → switch-level interactions

---

## Phase 1 (Telemetry Foundation) ✅

- 11 switches (INPUT_PULLDOWN)
- Accelerometer-based activity detection
- Session lifecycle (start / end)
- Structured JSON events

```json
{"event":"session_started","sessionId":"20260323132158","timestamp":"20260323132158"}
{"sessionId":"20260323132158","switch":"SW5","value":1,"timestamp":"20260323132210"}
{"event":"session_ended","sessionId":"20260323132158","timestamp":"20260323132217"}
```

---

## Phase 2 (Current Progress) ✅

- MQTT ingestion pipeline (Mosquitto)
- Topic-based routing system
- Device online/offline tracking
- Session tracking (start → interactions → end)
- SQLite persistence layer
- Full pytest coverage across:
  - utils
  - validators
  - router (mocked)
  - repositories (real DB)
  - handlers (full lifecycle)

---

## Key Design Decisions

- Validate before writing to DB
- Idempotent operations (safe replays)
- Ignore invalid session transitions
- Do not auto-close sessions on offline
- Strict separation of concerns

---

## Project Structure

ingestion/
  app.py  
  router.py  
  validators.py  
  handlers.py  
  repositories.py  
  utils.py  

tests/
  conftest.py  
  test_utils.py  
  test_validators.py  
  test_router.py  
  test_repositories.py  
  test_handlers.py  

---

## Roadmap

### Phase 3 — Subscriber Devices
Buzzer, LEDs, or other ESP32 devices reacting to MQTT topics

### Phase 4 — Dashboard UI
Real-time visualization, session playback, device state

### Phase 5 — Deployment
Docker, remote broker, authentication, monitoring
