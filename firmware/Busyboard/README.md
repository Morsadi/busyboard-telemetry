# BusyBoard Firmware

ESP32 firmware for the BusyBoard. Reads 11 toggle switches and an MPU-6050 accelerometer, publishes structured events over MQTT to a local Mosquitto broker.

---

## File Structure

```
Busyboard/
├── main.ino           # Entry point — setup() and loop()
├── config.h           # Pin definitions, thresholds, topic strings
├── secrets.h          # WiFi & MQTT credentials (gitignored)
├── IMUManager.h       # MPU-6050 read + threshold detection
├── MQTTManager.h      # MQTT connection, publish, LWT registration
├── SessionManager.h   # Session lifecycle and event tracking
├── StatusLed.h        # Connection and activity LED feedback
├── SwitchManager.h    # Switch polling, debounce, state change
└── WifiManager.h      # WiFi connection and reconnect
```

---

## Hardware

| Component | Detail |
|-----------|--------|
| MCU | ESP32 DevKit |
| Switches | 11 toggles (SW1–SW11), `INPUT_PULLDOWN`, active HIGH |
| IMU | MPU-6050 over I2C (SDA = GPIO 21, SCL = GPIO 22, addr 0x68) |
| Switch GPIOs | 13, 2, 14, 27, 26, 25, 33, 18, 32, 4, 23 |
| Status LED | GPIO 5 — on when connected to MQTT, off otherwise |

---

## MQTT Topics

Topics follow `busyboard/{deviceId}/...`. Device ID is derived from the MAC address (`bb-{hex}`, e.g. `bb-87c92df4`).

| Topic | Payload | When |
|-------|---------|------|
| `busyboard/{id}/status` | `"online"` / `"offline"` (retained) | On connect / LWT |
| `busyboard/{id}/events` | JSON event object | On switch or IMU state change |

Timestamps use `YYYYMMDDHHmmss` and are normalized to ISO 8601 at ingest.

---

## LWT (Last Will and Testament)

The firmware registers an MQTT Last Will on connect:

- **Topic:** `busyboard/{id}/status`
- **Payload:** `"offline"` (retained)

The broker publishes this automatically on ungraceful disconnects (USB unplug, power loss, network drop). On a clean connect, the firmware publishes a retained `"online"` to the same topic. The ingestion server uses these to track device state and close orphaned sessions.

---

## Subscribers

Other components in the BusyBoard system that consume these MQTT messages:

| Component | Role | Dir |
|-----------|------|------|
| Ingestion Server | Subscribes to events + status, writes to database, closes sessions on LWT | [`Link`](../../ingestion/README.md) |
| Dashboard | Real-time web UI for telemetry visualization | [`Link`](../../dashboard/README.md) |
| Buzzer | ESP32 subscriber with its own connection LED. Reacts to BusyBoard status and specific switch events. | [`Link`](../Buzzer/README.md) |