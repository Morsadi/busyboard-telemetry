# BusyBoard Buzzer firmware

This ESP32 companion sketch subscribes directly to one BusyBoard's MQTT status and two selected switch topics. It plays configured beep patterns and may publish an alarm event on its own events topic.

## Modules

| File | Responsibility |
|---|---|
| `main.ino` | Startup and primary loop |
| `config.h` | Pins, trigger switches, beep patterns, timing, and MQTT limits |
| `secrets.h` | Local Wi-Fi/MQTT credentials and target BusyBoard ID; gitignored |
| `WiFiManager.h` | Blocking startup Wi-Fi connection |
| `MQTTManager.h` | MQTT startup connection, subscriptions, status, and dispatch |
| `AlarmListener.h` | Peer-message routing, trigger state, and alarm publication |
| `BuzzerController.h` | Blocking beep-pattern playback |
| `StatusLed.h` | Connection-state LED behavior |

## Hardware and configuration

| Component | Current configuration |
|---|---|
| MCU | ESP32 DevKit |
| Active buzzer | GPIO 13 |
| Status LED | GPIO 14 |
| Trigger switches | `SW8` and `SW9` |
| Main-loop delay | 20 ms |

The beep count, duration, and gap for online, offline, and two-switch alarms are configured in `config.h`.

## Local setup

Create a local gitignored `secrets.h` that defines:

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `MQTT_SERVER`
- `MQTT_PORT`
- `MQTT_USER`
- `MQTT_PASSWORD`
- `BUSYBOARD_DEVICE_ID`

`BUSYBOARD_DEVICE_ID` selects the peer whose status and configured switch topics are subscribed.

## Behavior

1. Initialize the buzzer and connection LED.
2. Block until Wi-Fi connects.
3. Block until NTP time is available.
4. Attempt MQTT startup connection a configured number of times.
5. On success, subscribe to the target BusyBoard's status topic and the two configured switch topics.
6. Beep on BusyBoard online/offline transitions or when both trigger switches become ON.
7. Publish `alarm_triggered` for offline and two-switch alarms.

Ingestion currently logs `alarm_triggered` as unhandled and does not persist it. Topic and payload details live in [the MQTT contract](../../docs/contracts/mqtt.md).

## Build and physical verification

Use an ESP32 Arduino-compatible toolchain configured outside this repository to compile and flash `main.ino`. No reproducible board/toolchain configuration is tracked.

After flashing, verify subscriptions, retained peer status, both trigger switches, all beep patterns, alarm publication, and LED behavior.

## Runtime notes

Wi-Fi, time synchronization, MQTT connection, and peer subscriptions are established during startup. Beep patterns run synchronously, so timing or reconnect changes should be verified with the broker and physical device.
