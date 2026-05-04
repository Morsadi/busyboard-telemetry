# Buzzer Firmware

ESP32 firmware for the BusyBoard companion buzzer. Subscribes to a BusyBoard's MQTT events and beeps in response to status changes and specific switch triggers.

---

## File Structure

```
Buzzer/
├── main.ino             # Entry point — setup() and loop()
├── config.h             # Pins, beep patterns, target device ID, trigger switches
├── secrets.h            # WiFi & MQTT credentials (gitignored)
├── StatusLed.h          # Connection state LED (CONNECTING / ONLINE / OFFLINE)
├── WiFiManager.h        # WiFi connection
├── MQTTManager.h        # MQTT client wrapper, message dispatch
├── BuzzerController.h   # Non-blocking beep sequencer
└── AlarmListener.h      # Topic subscription + payload → beep mapping
```

---

## Hardware

| Component | Detail |
|-----------|--------|
| MCU | ESP32 DevKit |
| Buzzer | Active buzzer on `BUZZER_PIN` |
| Status LED | On `STATUS_LED_PIN`: blinks while connecting, solid when online |

---

## MQTT Subscriptions

The buzzer subscribes to a single target BusyBoard, identified by `BUSYBOARD_DEVICE_ID` in `config.h`.

| Topic | Listens For |
|-------|-------------|
| `busyboard/{target}/status` | `"online"` / `"offline"` (LWT) |
| `busyboard/{target}/events` | Switch events for `TRIGGER_SWITCH_A` and `TRIGGER_SWITCH_B` |

---

## Beep Patterns

Each pattern is configured in `config.h` as a `(count, duration, gap)` tuple.

| Trigger | Pattern |
|---------|---------|
| BusyBoard comes online | `BEEP_BUSYBOARD_ONLINE_*` |
| BusyBoard goes offline | `BEEP_BUSYBOARD_OFFLINE_*` |
| Trigger switch pattern (A and B both flipped) | `BEEP_SWITCH_ALARM_*` |

---

## Boot Sequence

1. Init buzzer and status LED (`CONNECTING` state).
2. Connect to WiFi, blinking the LED during the wait.
3. Sync time over NTP (`pool.ntp.org`).
4. Connect to MQTT with retry — up to `MQTT_STARTUP_MAX_ATTEMPTS`.
5. On success: LED turns solid (`ONLINE`), `AlarmListener` subscribes.
6. On failure: LED stays off (`OFFLINE`), no subscription. The main loop will reflect any later disconnection but does not auto-reconnect on its own.

---

## Related Components

| Component | Role | Repo |
|-----------|------|------|
| BusyBoard Firmware | Publishes the `status` and `events` topics this buzzer listens to | - |