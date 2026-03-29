import json
import logging

from constants import (
    EVENT_DEVICE_CONNECTED,
    EVENT_SESSION_ENDED,
    EVENT_SESSION_STARTED,
    EVENT_SWITCH_CHANGED,
    LWT_PAYLOAD_OFFLINE,
    LWT_PAYLOAD_ONLINE,
)
from handlers import (
    handle_device_connected,
    handle_device_offline,
    handle_device_online,
    handle_session_ended,
    handle_session_started,
    handle_switch_changed,
)
from utils import extract_topic_parts, parse_json_payload, utc_now_iso
from validators import (
    validate_device_connected,
    validate_session_ended,
    validate_session_started,
    validate_switch_changed,
)

logger = logging.getLogger(__name__)


def handle_message(topic: str, payload: bytes) -> None:
    topic_info = extract_topic_parts(topic)
    if topic_info is None:
        return

    received_ts = utc_now_iso()
    topic_type = topic_info["topic_type"]
    device_id = topic_info["device_id"]

    if topic_type == "status":
        try:
            status = payload.decode("utf-8").strip().lower()
        except UnicodeDecodeError:
            logger.warning("Failed to decode status payload for device=%s", device_id)
            return

        if status == LWT_PAYLOAD_OFFLINE:
            handle_device_offline(device_id=device_id, received_ts=received_ts)
        elif status == LWT_PAYLOAD_ONLINE:
            handle_device_online(device_id=device_id, received_ts=received_ts)
        else:
            logger.warning("Unknown status value '%s' for device=%s", status, device_id)
        return

    data = parse_json_payload(payload)
    if data is None:
        return

    payload_json = json.dumps(data, separators=(",", ":"))

    device_id_from_payload = data.get("deviceId")
    if device_id_from_payload != device_id:
        logger.warning(
            "deviceId mismatch | topic=%s | payload=%s",
            device_id,
            device_id_from_payload,
        )
        return

    event_name = data.get("event")

    if topic_type == "events" and event_name == EVENT_DEVICE_CONNECTED:
        ok, error = validate_device_connected(data)
        if not ok:
            logger.warning("Invalid device_connected payload: %s", error)
            return
        handle_device_connected(topic=topic, data=data, received_ts=received_ts, payload_json=payload_json)
        return

    if topic_type == "events" and event_name == EVENT_SESSION_STARTED:
        ok, error = validate_session_started(data)
        if not ok:
            logger.warning("Invalid session_started payload: %s", error)
            return
        handle_session_started(topic=topic, data=data, received_ts=received_ts, payload_json=payload_json)
        return

    if topic_type == "events" and event_name == EVENT_SESSION_ENDED:
        ok, error = validate_session_ended(data)
        if not ok:
            logger.warning("Invalid session_ended payload: %s", error)
            return
        handle_session_ended(topic=topic, data=data, received_ts=received_ts, payload_json=payload_json)
        return

    if topic_type == "switch" and event_name == EVENT_SWITCH_CHANGED:
        ok, error = validate_switch_changed(data, topic_info.get("switch_name"))
        if not ok:
            logger.warning("Invalid switch_changed payload: %s", error)
            return
        handle_switch_changed(topic=topic, data=data, received_ts=received_ts, payload_json=payload_json)
        return

    logger.warning("Unhandled message | topic=%s | event=%s", topic, event_name)