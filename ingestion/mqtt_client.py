import logging

import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_KEEPALIVE, MQTT_PORT
from constants import TOPIC_EVENTS, TOPIC_STATUS, TOPIC_SWITCHES
from router import handle_message

logger = logging.getLogger(__name__)


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logger.info("Connected to MQTT broker at %s:%s", MQTT_HOST, MQTT_PORT)
        client.subscribe(TOPIC_EVENTS)
        client.subscribe(TOPIC_SWITCHES)
        client.subscribe(TOPIC_STATUS)
        logger.info(
            "Subscribed to %s, %s, and %s",
            TOPIC_EVENTS,
            TOPIC_SWITCHES,
            TOPIC_STATUS,
        )
    else:
        logger.error("Failed to connect to MQTT broker. rc=%s", reason_code)


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    try:
        handle_message(msg.topic, msg.payload)
    except Exception:
        logger.exception("Unhandled error while processing message on topic %s", msg.topic)


def run_mqtt_client() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        logger.info("Ingestion server started")
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping server...")
    except Exception:
        logger.exception("Fatal error in MQTT client")
        raise
    finally:
        try:
            client.loop_stop()
        except Exception:
            pass

        try:
            client.disconnect()
        except Exception:
            pass

        logger.info("Server stopped")