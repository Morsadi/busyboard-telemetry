from validators import (
    validate_device_connected,
    validate_session_started,
    validate_switch_changed,
    validate_session_ended,
)
# Session started
def test_validate_device_connected_valid():
    data = {
        "event": "device_connected",
        "deviceId": "bb-123",
        "timestamp": "20260326164347",
    }

    ok, error = validate_device_connected(data)
    assert ok is True
    assert error is None


def test_validate_device_connected_missing_field():
    data = {
        "event": "device_connected",
        "timestamp": "20260326164347",
    }

    ok, error = validate_device_connected(data)
    assert ok is False
    assert "deviceId" in error
    
# Session started
def test_validate_session_started_valid():
    data = {
        "event": "session_started",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "timestamp": "20260326164347",
    }

    ok, error = validate_session_started(data)
    assert ok is True


def test_validate_session_started_wrong_event():
    data = {
        "event": "wrong_event",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "timestamp": "20260326164347",
    }

    ok, error = validate_session_started(data)
    assert ok is False
    
# Switch Chnaged
def test_validate_switch_changed_valid():
    data = {
        "event": "switch_changed",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "switch": "SW1",
        "value": 1,
        "timestamp": "20260326164347",
    }

    ok, error = validate_switch_changed(data, "SW1")
    assert ok is True


def test_validate_switch_changed_invalid_value():
    data = {
        "event": "switch_changed",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "switch": "SW1",
        "value": 2,
        "timestamp": "20260326164347",
    }

    ok, error = validate_switch_changed(data, "SW1")
    assert ok is False


def test_validate_switch_changed_topic_mismatch():
    data = {
        "event": "switch_changed",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "switch": "SW2",
        "value": 1,
        "timestamp": "20260326164347",
    }

    ok, error = validate_switch_changed(data, "SW1")
    assert ok is False
    
# Session ended
def test_validate_session_ended_valid():
    data = {
        "event": "session_ended",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "timestamp": "20260326164347",
        "interactionCount": 3,
        "durationMs": 5000,
    }

    ok, error = validate_session_ended(data)
    assert ok is True


def test_validate_session_ended_missing_field():
    data = {
        "event": "session_ended",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "timestamp": "20260326164347",
        "durationMs": 5000,
    }

    ok, error = validate_session_ended(data)
    assert ok is False
    assert "interactionCount" in error


def test_validate_session_ended_negative_duration():
    data = {
        "event": "session_ended",
        "deviceId": "bb-123",
        "sessionId": "sess-1",
        "timestamp": "20260326164347",
        "interactionCount": 1,
        "durationMs": -1,
    }

    ok, error = validate_session_ended(data)
    assert ok is False