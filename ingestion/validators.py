from typing import Any

from constants import (
    EVENT_DEVICE_CONNECTED,
    EVENT_SESSION_ENDED,
    EVENT_SESSION_STARTED,
    EVENT_SWITCH_CHANGED,
)
from utils import normalize_timestamp


def validate_device_connected(data: dict[str, Any]) -> tuple[bool, str | None]:
    required_fields = ["event", "deviceId", "timestamp"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if data["event"] != EVENT_DEVICE_CONNECTED:
        return False, f"event must be {EVENT_DEVICE_CONNECTED}"

    if not isinstance(data["deviceId"], str) or not data["deviceId"].strip():
        return False, "Invalid deviceId"

    try:
        normalize_timestamp(data["timestamp"])
    except ValueError as exc:
        return False, str(exc)

    return True, None


def validate_common_session_fields(data: dict[str, Any]) -> tuple[bool, str | None]:
    required_fields = ["event", "deviceId", "sessionId", "timestamp"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if not isinstance(data["event"], str) or not data["event"].strip():
        return False, "Invalid event"

    if not isinstance(data["deviceId"], str) or not data["deviceId"].strip():
        return False, "Invalid deviceId"

    if not isinstance(data["sessionId"], str) or not data["sessionId"].strip():
        return False, "Invalid sessionId"

    try:
        normalize_timestamp(data["timestamp"])
    except ValueError as exc:
        return False, str(exc)

    return True, None


def validate_session_started(data: dict[str, Any]) -> tuple[bool, str | None]:
    ok, error = validate_common_session_fields(data)
    if not ok:
        return False, error

    if data["event"] != EVENT_SESSION_STARTED:
        return False, f"event must be {EVENT_SESSION_STARTED}"

    return True, None


def validate_switch_changed(
    data: dict[str, Any], topic_switch_name: str | None
) -> tuple[bool, str | None]:
    ok, error = validate_common_session_fields(data)
    if not ok:
        return False, error

    if data["event"] != EVENT_SWITCH_CHANGED:
        return False, f"event must be {EVENT_SWITCH_CHANGED}"

    if "switch" not in data:
        return False, "Missing required field: switch"

    if "value" not in data:
        return False, "Missing required field: value"

    if not isinstance(data["switch"], str) or not data["switch"].strip():
        return False, "Invalid switch"

    if data["value"] not in (0, 1):
        return False, "value must be 0 or 1"

    if topic_switch_name and data["switch"] != topic_switch_name:
        return False, "Switch in payload does not match switch in topic"

    return True, None


def validate_session_ended(data: dict[str, Any]) -> tuple[bool, str | None]:
    ok, error = validate_common_session_fields(data)
    if not ok:
        return False, error

    if data["event"] != EVENT_SESSION_ENDED:
        return False, f"event must be {EVENT_SESSION_ENDED}"

    if "interactionCount" not in data:
        return False, "Missing required field: interactionCount"

    if "durationMs" not in data:
        return False, "Missing required field: durationMs"

    if not isinstance(data["interactionCount"], int) or data["interactionCount"] < 0:
        return False, "interactionCount must be a non-negative integer"

    if not isinstance(data["durationMs"], int) or data["durationMs"] < 0:
        return False, "durationMs must be a non-negative integer"

    return True, None