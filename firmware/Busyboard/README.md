# BusyBoard publisher firmware

This ESP32 sketch reads 11 toggle switches and an MPU-6050, manages activity sessions, and publishes device/session/switch telemetry to MQTT.

## Modules

| File | Responsibility |
|---|---|
| `main.ino` | Startup and primary loop |
| `config.h` | Pins, thresholds, timing, firmware version, and MQTT limits |
| `secrets.h` | Local Wi-Fi/MQTT credentials; gitignored |
| `IMUManager.h` | MPU-6050 initialization and motion threshold detection |
| `MQTTManager.h` | MQTT startup connection, publication, status, and LWT |
| `SessionManager.h` | Session lifecycle and telemetry payload construction |
| `StatusLed.h` | Connection-state LED behavior |
| `SwitchManager.h` | Switch initialization, polling, and debounce |
| `WifiManager.h` | Blocking startup Wi-Fi connection |

## Hardware and configuration

| Component | Current configuration |
|---|---|
| MCU | ESP32 DevKit |
| Switches | 11 toggles, `INPUT_PULLDOWN`, active HIGH |
| Switch names | `SW1` through `SW11` |
| Switch GPIOs | 13, 2, 14, 27, 26, 25, 33, 18, 32, 4, 23 |
| IMU | MPU-6050, I2C address `0x68` |
| I2C pins | SDA 21, SCL 22 |
| Status LED | GPIO 5 |
| Switch debounce | 40 ms |
| Session inactivity timeout | 5 seconds |
| Main-loop delay | 20 ms |

Motion starts or extends a session but is not emitted as a switch interaction. Switch changes are published separately from lifecycle events. See [the data-model documentation](../../docs/data-model.md) and [the current MQTT contract](../../docs/contracts/mqtt.md).

## Local setup

Create a local gitignored `secrets.h` that defines:

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `MQTT_SERVER`
- `MQTT_PORT`
- `MQTT_USER`
- `MQTT_PASSWORD`

The repository does not include safe declaration examples, values, a board FQBN, or pinned toolchain/library versions.

## Build and physical verification

Use an ESP32 Arduino-compatible toolchain configured outside this repository to compile and flash `main.ino`. Record the selected board target and dependency versions when reporting verification.

After flashing, verify as applicable:

- Wi-Fi, NTP, and MQTT startup status in serial output;
- retained online/offline status at the broker;
- all 11 switch inputs and debounce behavior;
- motion starting/extending a session without a switch row;
- session end after inactivity;
- status LED behavior.

## Runtime notes

Wi-Fi, time synchronization, and MQTT connection are established during startup. The current sketch does not reconnect MQTT after a later connection loss, so connectivity changes require device and broker verification.

Session identity and MQTT compatibility requirements are maintained in [the shared data model](../../docs/data-model.md) and [MQTT contract](../../docs/contracts/mqtt.md).
