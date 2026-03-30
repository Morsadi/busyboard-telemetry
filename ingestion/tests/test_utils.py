from utils import extract_topic_parts, normalize_timestamp, parse_json_payload


def test_extract_topic_parts_for_events():
    result = extract_topic_parts("busyboard/bb-123/events")

    assert result == {
        "device_id": "bb-123",
        "topic_type": "events",
    }


def test_extract_topic_parts_for_switch():
    result = extract_topic_parts("busyboard/bb-123/switch/SW1")

    assert result == {
        "device_id": "bb-123",
        "topic_type": "switch",
        "switch_name": "SW1",
    }


def test_extract_topic_parts_for_status():
    result = extract_topic_parts("busyboard/bb-123/status")

    assert result == {
        "device_id": "bb-123",
        "topic_type": "status",
    }


def test_extract_topic_parts_invalid_root():
    result = extract_topic_parts("wrong/bb-123/events")
    assert result is None


def test_extract_topic_parts_too_short():
    result = extract_topic_parts("busyboard/bb-123")
    assert result is None


def test_normalize_timestamp_compact():
    result = normalize_timestamp("20260326164347")
    assert result == "2026-03-26T16:43:47+00:00"


def test_normalize_timestamp_iso():
    result = normalize_timestamp("2026-03-26T16:43:47+00:00")
    assert result == "2026-03-26T16:43:47+00:00"


def test_normalize_timestamp_iso_z():
    result = normalize_timestamp("2026-03-26T16:43:47Z")
    assert result == "2026-03-26T16:43:47+00:00"


def test_normalize_timestamp_empty_string():
    try:
        normalize_timestamp("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "timestamp cannot be empty"


def test_parse_json_payload_valid_object():
    result = parse_json_payload(b'{"event":"session_started"}')
    assert result == {"event": "session_started"}


def test_parse_json_payload_valid_but_not_object():
    result = parse_json_payload(b'["not","an","object"]')
    assert result is None


def test_parse_json_payload_invalid_json():
    result = parse_json_payload(b'{"event":')
    assert result is None