# Current MQTT contract

This is the authoritative documentation of the MQTT topics and payloads currently supported by BusyBoard firmware and Python ingestion.

## Namespace and identifiers

All current topics use this prefix:

```text
busyboard/{deviceId}/...
```

BusyBoard device IDs are generated as `bb-` plus a hexadecimal value derived from the ESP32 MAC address. The Buzzer sketch currently uses `buzzer-bb-01` as its own device ID. The Buzzer target BusyBoard ID comes from its gitignored secrets file.

## Topic summary

| Topic | Publisher | Consumers | Payload |
|---|---|---|---|
| `busyboard/{id}/status` | BusyBoard and Buzzer firmware | Ingestion; Buzzer for its target BusyBoard | UTF-8 text `online` or `offline` |
| `busyboard/{id}/events` | BusyBoard and Buzzer firmware | Ingestion | JSON lifecycle or alarm object |
| `busyboard/{id}/switch/{switchName}` | BusyBoard firmware | Ingestion; Buzzer for two configured switches | JSON `switch_changed` object |

## Status

The status payload is plain text, not JSON:

```text
online
```

or:

```text
offline
```

On MQTT connect, firmware publishes retained `online`. Each firmware client registers retained `offline` as its Last Will with QoS 1. Ingestion accepts values case-insensitively after trimming whitespace and updates the device row using ingestion receipt time.

Offline status does not end an active session in ingestion.

## BusyBoard lifecycle events

Lifecycle events are published to `busyboard/{deviceId}/events`.

### `device_connected`

```json
{
  "event": "device_connected",
  "deviceId": "bb-87c92df4",
  "timestamp": "20260326164347",
  "firmwareVersion": "0.2.0"
}
```

Ingestion requires `event`, `deviceId`, and `timestamp`. It accepts but does not validate or persist `firmwareVersion` separately; the complete payload is stored with the event.

### `session_started`

```json
{
  "event": "session_started",
  "deviceId": "bb-87c92df4",
  "sessionId": "20260326164347",
  "timestamp": "20260326164347"
}
```

Ingestion creates the session if it does not exist. It ignores a start message for a session already marked ended.

### `session_ended`

```json
{
  "event": "session_ended",
  "deviceId": "bb-87c92df4",
  "sessionId": "20260326164347",
  "timestamp": "20260326164352",
  "interactionCount": 3,
  "durationMs": 5000
}
```

`interactionCount` and `durationMs` must be non-negative integers. Ingestion ignores the message when the session is unknown or already ended. On a valid end, the firmware-provided interaction count becomes the stored final count.

## Switch changes

Switch changes are published to `busyboard/{deviceId}/switch/{switchName}`:

```json
{
  "event": "switch_changed",
  "deviceId": "bb-87c92df4",
  "sessionId": "20260326164347",
  "switch": "SW1",
  "value": 1,
  "timestamp": "20260326164348"
}
```

Validation rules:

- `event` must equal `switch_changed`;
- `deviceId` must equal the topic device ID;
- `switch` must be a non-empty string and equal the topic switch name;
- `value` must be `0` or `1`;
- `sessionId` and `timestamp` are required.

The current BusyBoard publishes `SW1` through `SW11`. A valid switch event for an unknown session causes ingestion to synthesize an active session starting at the switch timestamp. A switch event for an ended session is ignored.

## Buzzer alarm events

The Buzzer may publish this object to its own events topic:

```json
{
  "event": "alarm_triggered",
  "deviceId": "buzzer-bb-01",
  "sourceDeviceId": "bb-87c92df4",
  "reason": "both_trigger_switches_on",
  "timestamp": "20260326164348"
}
```

Current reasons are `both_trigger_switches_on` and `busyboard_offline_lwt`.

Ingestion subscribes to the topic but does not currently persist `alarm_triggered`. Buzzer status messages can still create or update its device row.

## Timestamp handling

Firmware emits compact UTC timestamps using `YYYYMMDDHHmmss` during normal operation.

Ingestion also accepts `YYYYMMDDTHHMMSS` and ISO 8601 strings. Naive ISO timestamps are interpreted as UTC, and timezone-aware values are normalized to UTC.

Current BusyBoard session IDs are generated from the compact session-start timestamp and are stored as 14-digit strings. Changes to this format require coordinated updates across firmware, ingestion, persistence, tests, and dashboard routing.

## Delivery and compatibility

- Topic device ID and JSON `deviceId` must match.
- The current payloads do not include a message-level deduplication identifier; persistence changes should account for repeated delivery intentionally.
- Topic, event-name, field-name, switch-name, timestamp, or session-ID changes require coordinated review of BusyBoard firmware, Buzzer firmware, ingestion, schemas, tests, and dashboard consumers.
