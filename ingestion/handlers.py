import logging
from typing import Any

from constants import (
    DEVICE_STATUS_OFFLINE,
    DEVICE_STATUS_ONLINE,
    EVENT_DEVICE_CONNECTED,
    EVENT_SESSION_ENDED,
    EVENT_SESSION_STARTED,
    EVENT_SWITCH_CHANGED,
    SESSION_STATUS_ENDED,
)
from db import get_connection
from repositories import (
    create_session_if_missing,
    end_session,
    get_active_sessions_for_device,
    get_session_row,
    increment_session_interaction_count,
    insert_event,
    insert_switch_event,
    upsert_device,
)
from utils import normalize_timestamp

logger = logging.getLogger(__name__)


def handle_device_connected(*, topic: str, data: dict[str, Any], received_ts: str, payload_json: str) -> None:
    device_id = data["deviceId"]
    event_ts = normalize_timestamp(data["timestamp"])

    with get_connection() as conn:
        upsert_device(conn=conn, device_id=device_id, seen_ts=received_ts, status=DEVICE_STATUS_ONLINE)
        insert_event(
            conn=conn,
            device_id=device_id,
            session_id=None,
            event_type=EVENT_DEVICE_CONNECTED,
            event_ts=event_ts,
            received_ts=received_ts,
            topic=topic,
            payload_json=payload_json,
        )
        conn.commit()

    logger.info("device_connected | device=%s | event_ts=%s", device_id, event_ts)


def handle_session_started(*, topic: str, data: dict[str, Any], received_ts: str, payload_json: str) -> None:
    device_id = data["deviceId"]
    session_id = data["sessionId"]
    event_ts = normalize_timestamp(data["timestamp"])

    with get_connection() as conn:
        upsert_device(conn=conn, device_id=device_id, seen_ts=received_ts, status=DEVICE_STATUS_ONLINE)

        existing_session = get_session_row(conn=conn, session_id=session_id)
        if existing_session is not None and existing_session["status"] == SESSION_STATUS_ENDED:
            logger.warning(
                "session_started ignored | device=%s | session=%s | reason=session already ended",
                device_id,
                session_id,
            )
            conn.commit()
            return

        create_session_if_missing(
            conn=conn,
            session_id=session_id,
            device_id=device_id,
            started_at=event_ts,
        )
        insert_event(
            conn=conn,
            device_id=device_id,
            session_id=session_id,
            event_type=EVENT_SESSION_STARTED,
            event_ts=event_ts,
            received_ts=received_ts,
            topic=topic,
            payload_json=payload_json,
        )
        conn.commit()

    logger.info("session_started | device=%s | session=%s | event_ts=%s", device_id, session_id, event_ts)


def handle_switch_changed(*, topic: str, data: dict[str, Any], received_ts: str, payload_json: str) -> None:
    device_id = data["deviceId"]
    session_id = data["sessionId"]
    event_ts = normalize_timestamp(data["timestamp"])
    switch_name = data["switch"]
    value = data["value"]

    with get_connection() as conn:
        upsert_device(conn=conn, device_id=device_id, seen_ts=received_ts, status=DEVICE_STATUS_ONLINE)

        session_row = get_session_row(conn=conn, session_id=session_id)
        if session_row is None:
            create_session_if_missing(
                conn=conn,
                session_id=session_id,
                device_id=device_id,
                started_at=event_ts,
            )
        elif session_row["status"] == SESSION_STATUS_ENDED:
            logger.warning(
                "switch_changed ignored | device=%s | session=%s | switch=%s | reason=session already ended",
                device_id,
                session_id,
                switch_name,
            )
            conn.commit()
            return

        event_id = insert_event(
            conn=conn,
            device_id=device_id,
            session_id=session_id,
            event_type=EVENT_SWITCH_CHANGED,
            event_ts=event_ts,
            received_ts=received_ts,
            topic=topic,
            payload_json=payload_json,
        )
        insert_switch_event(
            conn=conn,
            session_id=session_id,
            device_id=device_id,
            switch_name=switch_name,
            value=value,
            event_ts=event_ts,
            event_id=event_id,
        )
        increment_session_interaction_count(conn=conn, session_id=session_id)
        conn.commit()

    logger.info(
        "switch_changed | device=%s | session=%s | switch=%s | value=%s | event_ts=%s",
        device_id,
        session_id,
        switch_name,
        value,
        event_ts,
    )


def handle_session_ended(*, topic: str, data: dict[str, Any], received_ts: str, payload_json: str) -> None:
    device_id = data["deviceId"]
    session_id = data["sessionId"]
    event_ts = normalize_timestamp(data["timestamp"])
    interaction_count = data["interactionCount"]
    duration_ms = data["durationMs"]

    with get_connection() as conn:
        upsert_device(conn=conn, device_id=device_id, seen_ts=received_ts, status=DEVICE_STATUS_ONLINE)

        session_row = get_session_row(conn=conn, session_id=session_id)

        if session_row is None:
            logger.warning(
                "session_ended ignored | device=%s | session=%s | reason=unknown session",
                device_id,
                session_id,
            )
            conn.commit()
            return

        if session_row["status"] == SESSION_STATUS_ENDED:
            logger.warning(
                "session_ended ignored | device=%s | session=%s | reason=already ended",
                device_id,
                session_id,
            )
            conn.commit()
            return

        insert_event(
            conn=conn,
            device_id=device_id,
            session_id=session_id,
            event_type=EVENT_SESSION_ENDED,
            event_ts=event_ts,
            received_ts=received_ts,
            topic=topic,
            payload_json=payload_json,
        )
        end_session(
            conn=conn,
            session_id=session_id,
            ended_at=event_ts,
            duration_ms=duration_ms,
            interaction_count=interaction_count,
        )
        conn.commit()

    logger.info(
        "session_ended | device=%s | session=%s | interaction_count=%s | duration_ms=%s | event_ts=%s",
        device_id,
        session_id,
        interaction_count,
        duration_ms,
        event_ts,
    )


def handle_device_offline(*, device_id: str, received_ts: str) -> None:
    with get_connection() as conn:
        upsert_device(conn=conn, device_id=device_id, seen_ts=received_ts, status=DEVICE_STATUS_OFFLINE)
        active_sessions = get_active_sessions_for_device(conn=conn, device_id=device_id)
        conn.commit()

    if active_sessions:
        active_session_ids = [str(row["session_id"]) for row in active_sessions]
        logger.warning(
            "device_offline | device=%s | received_ts=%s | active_sessions=%s | note=session left active awaiting real session_ended",
            device_id,
            received_ts,
            ",".join(active_session_ids),
        )
    else:
        logger.info("device_offline | device=%s | received_ts=%s", device_id, received_ts)


def handle_device_online(*, device_id: str, received_ts: str) -> None:
    with get_connection() as conn:
        upsert_device(conn=conn, device_id=device_id, seen_ts=received_ts, status=DEVICE_STATUS_ONLINE)
        conn.commit()

    logger.info("device_online | device=%s | received_ts=%s", device_id, received_ts)