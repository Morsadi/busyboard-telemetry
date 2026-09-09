# BusyBoard firmware

The firmware directory contains two independent ESP32 Arduino sketches:

| Sketch | Responsibility |
|---|---|
| [`Busyboard/`](Busyboard/README.md) | Reads physical switches and motion, manages sessions, and publishes telemetry |
| [`Buzzer/`](Buzzer/README.md) | Subscribes to one BusyBoard's status/switch messages and plays alarm patterns |

The sketches communicate through MQTT rather than through shared runtime code. Their currently observed topics and payloads are documented in [the MQTT contract](../docs/contracts/mqtt.md).

## Prerequisites

- ESP32-compatible Arduino toolchain;
- ESP32 Arduino core with `WiFi`, `Wire`, and LEDC support;
- `PubSubClient`;
- the hardware described in each sketch README;
- a reachable MQTT broker and Wi-Fi network.

## Build tooling

Board FQBN, Arduino core/library versions, and compile/flash commands are selected in the developer's local ESP32 toolchain. Record those values when reporting firmware verification; an editor-only check is not a firmware build.

## Secrets

Each sketch includes a gitignored `secrets.h`. Both sketches use these names:

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `MQTT_SERVER`
- `MQTT_PORT`
- `MQTT_USER`
- `MQTT_PASSWORD`

The Buzzer also uses `BUSYBOARD_DEVICE_ID` to choose its peer.

Do not commit real credentials. No tracked secret template currently defines the required C++ declarations.

## Local workflow

1. Read the target sketch README and `firmware/AGENTS.md`.
2. Configure its gitignored `secrets.h` locally.
3. Select an ESP32 target and install the required libraries in the local Arduino-compatible toolchain.
4. Compile and flash the affected sketch.
5. Observe serial output and exercise the relevant physical inputs/MQTT behavior.
6. Compile both sketches when changing the shared MQTT contract.

Report the actual board target, toolchain, and physical checks used. If compilation is unavailable, report firmware as code-reviewed only.

## Shared documentation

- [System architecture](../docs/architecture.md)
- [Current MQTT contract](../docs/contracts/mqtt.md)
- [Data model and session behavior](../docs/data-model.md)
- [Testing and verification](../docs/testing.md)
