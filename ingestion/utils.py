import json
import logging
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def normalize_timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")

    raw = value.strip()
    if not raw:
        raise ValueError("timestamp cannot be empty")

    compact_formats = (
        "%Y%m%d%H%M%S",
        "%Y%m%dT%H%M%S",
    )

    for fmt in compact_formats:
        try:
            dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            pass

    iso_candidate = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso_candidate)
    except ValueError as exc:
        raise ValueError(f"unsupported timestamp format: {value}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.isoformat()


def parse_json_payload(payload: bytes) -> dict[str, Any] | None:
    try:
        decoded = payload.decode("utf-8")
        data = json.loads(decoded)
        if not isinstance(data, dict):
            logger.warning("Payload is valid JSON but not an object")
            return None
        return data
    except UnicodeDecodeError:
        logger.warning("Failed to decode payload as UTF-8")
        return None
    except json.JSONDecodeError:
        logger.warning("Failed to parse payload as JSON")
        return None


def extract_topic_parts(topic: str) -> dict[str, str] | None:
    parts = topic.split("/")

    if len(parts) < 3 or parts[0] != "busyboard":
        logger.warning("Unexpected topic format: %s", topic)
        return None

    result: dict[str, str] = {
        "device_id": parts[1],
        "topic_type": parts[2],
    }

    if len(parts) == 4 and parts[2] == "switch":
        result["switch_name"] = parts[3]

    return result