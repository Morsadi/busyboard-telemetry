# BusyBoard Telemetry

**An IoT system that uses a physical busy board to capture real-world interactions and turn them into events that can trigger and control other connected devices using MQTT (Mosquitto).**

**This project explores how simple physical inputs like switches and movement can act as signals in a larger connected system, where actions are not just recorded but distributed and reacted to in real time. Each interaction is structured as telemetry, allowing it to be streamed, monitored, and used to coordinate behavior across multiple devices.**

**The goal is to bridge the gap between physical interfaces and modern event-driven architectures, building toward a system where hardware becomes a reliable source of real-time data that can power automation, monitoring, and responsive environments.**

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

## Phase 1 (Current)

- 11 switches (INPUT_PULLDOWN)
- Accelerometer-based activity detection
- Session lifecycle (start / end)
- Structured JSON events via Serial

```json
{"event":"session_started","sessionId":"20260323132158","timestamp":"20260323132158"}
{"sessionId":"20260323132158","switch":"SW5","value":1,"timestamp":"20260323132210"}
{"event":"session_ended","sessionId":"20260323132158","timestamp":"20260323132217"}
```

## Roadmap

### Phase 1 — Telemetry Foundation ✅
Switch + motion input, session model, JSON output

### Phase 2 — MQTT Streaming
ESP32 → Mosquitto broker, topic structure, real-time publish

### Phase 3 — Subscriber Service
Node.js / Python consumer, session storage, processing

### Phase 4 — Dashboard UI
Real-time visualization, session playback, device state
