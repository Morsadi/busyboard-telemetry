# Firmware agent instructions

These instructions apply to `firmware/`, which contains independent BusyBoard and Buzzer ESP32 sketches.

Read the target sketch README plus:

- [Current MQTT contract](../docs/contracts/mqtt.md)
- [Data model and session behavior](../docs/data-model.md)
- [Testing and verification](../docs/testing.md)

## Safe modification boundaries

- Treat MQTT topics and payloads as public cross-subsystem interfaces.
- Do not change GPIOs, active levels, I2C assumptions, trigger switches, device identity, or timing constants as cleanup.
- Never commit Wi-Fi, broker, or target-device credentials.
- Keep the primary loop responsive; be cautious with polling, MQTT servicing, session timing, and buzzer playback.
- Prefer structured JSON parsing over substring inspection when a task touches message parsing.

## Contract changes

Before changing a published or consumed MQTT field/topic:

1. inspect both firmware sketches;
2. inspect ingestion routing and validation;
3. inspect schema/dashboard effects and tests;
4. update the authoritative MQTT contract;
5. compile both sketches when the change is shared.

Current Buzzer alarm-event handling is documented in the MQTT contract; do not change persistence expectations without reviewing ingestion.

## Current constraints

- The firmware target and toolchain are selected outside the repository.
- Startup connectivity and Buzzer playback affect loop timing; keep timing-sensitive changes explicit.
- MQTT and session identity are shared contracts, not sketch-local implementation details.

Keep changes scoped to the requested behavior.

## Verification

No reproducible compile/flash command is tracked. Before claiming firmware verification:

- name the actual ESP32 target/FQBN, core, libraries, and toolchain;
- compile the affected sketch;
- compile both sketches for a shared contract change;
- report relevant serial, broker, and physical-device checks.

If compilation is unavailable, report code-level validation only. Never claim hardware verification without using hardware.
