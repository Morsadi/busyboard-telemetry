"""Regression checks for the test harness's application-data isolation."""

import dotenv
import pytest

import cloud_publisher
import config
import db
import supabase_db


def test_application_configuration_and_connections_are_isolated():
    assert config.SUPABASE_DB_URL == supabase_db.SUPABASE_DB_URL == ""
    assert config.MQTT_USER == config.MQTT_PASSWORD == ""
    assert dotenv.load_dotenv() is False
    with pytest.raises(AssertionError, match="explicit pg_connect fixture"):
        supabase_db.get_connection()


def test_local_database_and_publisher_state_start_isolated(test_db):
    assert db.DB_PATH == test_db
    assert db.DB_PATH.parent != db.BASE_DIR
    assert cloud_publisher._enabled is False
    assert cloud_publisher._queue.empty()
