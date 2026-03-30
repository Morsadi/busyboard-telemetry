from unittest.mock import patch

from router import handle_message


def test_status_online_routes_to_device_online_handler():
    with patch("router.handle_device_online") as mock_handler:
        handle_message("busyboard/bb-123/status", b"online")

        mock_handler.assert_called_once()
        _, kwargs = mock_handler.call_args
        assert kwargs["device_id"] == "bb-123"
        assert "received_ts" in kwargs


def test_status_offline_routes_to_device_offline_handler():
    with patch("router.handle_device_offline") as mock_handler:
        handle_message("busyboard/bb-123/status", b"offline")

        mock_handler.assert_called_once()
        _, kwargs = mock_handler.call_args
        assert kwargs["device_id"] == "bb-123"
        assert "received_ts" in kwargs


def test_device_connected_routes_to_handler():
    payload = (
        b'{"event":"device_connected","deviceId":"bb-123","timestamp":"20260326164347"}'
    )

    with patch("router.handle_device_connected") as mock_handler:
        handle_message("busyboard/bb-123/events", payload)

        mock_handler.assert_called_once()
        _, kwargs = mock_handler.call_args
        assert kwargs["topic"] == "busyboard/bb-123/events"
        assert kwargs["data"]["event"] == "device_connected"
        assert kwargs["data"]["deviceId"] == "bb-123"
        assert "received_ts" in kwargs
        assert "payload_json" in kwargs


def test_session_started_routes_to_handler():
    payload = (
        b'{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}'
    )

    with patch("router.handle_session_started") as mock_handler:
        handle_message("busyboard/bb-123/events", payload)

        mock_handler.assert_called_once()
        _, kwargs = mock_handler.call_args
        assert kwargs["data"]["event"] == "session_started"
        assert kwargs["data"]["sessionId"] == "sess-1"


def test_session_ended_routes_to_handler():
    payload = (
        b'{"event":"session_ended","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347","interactionCount":2,"durationMs":5000}'
    )

    with patch("router.handle_session_ended") as mock_handler:
        handle_message("busyboard/bb-123/events", payload)

        mock_handler.assert_called_once()
        _, kwargs = mock_handler.call_args
        assert kwargs["data"]["event"] == "session_ended"
        assert kwargs["data"]["interactionCount"] == 2
        assert kwargs["data"]["durationMs"] == 5000


def test_switch_changed_routes_to_handler():
    payload = (
        b'{"event":"switch_changed","deviceId":"bb-123","sessionId":"sess-1","switch":"SW1","value":1,"timestamp":"20260326164347"}'
    )

    with patch("router.handle_switch_changed") as mock_handler:
        handle_message("busyboard/bb-123/switch/SW1", payload)

        mock_handler.assert_called_once()
        _, kwargs = mock_handler.call_args
        assert kwargs["topic"] == "busyboard/bb-123/switch/SW1"
        assert kwargs["data"]["event"] == "switch_changed"
        assert kwargs["data"]["switch"] == "SW1"
        assert kwargs["data"]["value"] == 1


def test_invalid_status_does_not_call_handlers():
    with patch("router.handle_device_online") as mock_online, patch("router.handle_device_offline") as mock_offline:
        handle_message("busyboard/bb-123/status", b"weird-status")

        mock_online.assert_not_called()
        mock_offline.assert_not_called()


def test_invalid_json_does_not_call_device_connected_handler():
    with patch("router.handle_device_connected") as mock_handler:
        handle_message("busyboard/bb-123/events", b'{"event":')

        mock_handler.assert_not_called()


def test_payload_device_id_mismatch_does_not_call_handler():
    payload = (
        b'{"event":"device_connected","deviceId":"bb-999","timestamp":"20260326164347"}'
    )

    with patch("router.handle_device_connected") as mock_handler:
        handle_message("busyboard/bb-123/events", payload)

        mock_handler.assert_not_called()


def test_invalid_switch_payload_does_not_call_handler():
    payload = (
        b'{"event":"switch_changed","deviceId":"bb-123","sessionId":"sess-1","switch":"SW2","value":1,"timestamp":"20260326164347"}'
    )

    with patch("router.handle_switch_changed") as mock_handler:
        handle_message("busyboard/bb-123/switch/SW1", payload)

        mock_handler.assert_not_called()