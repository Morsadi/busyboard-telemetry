import logging

from db import init_db
from mqtt_client import run_mqtt_client
import cloud_publisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    init_db()
    cloud_publisher.start()
    run_mqtt_client()


if __name__ == "__main__":
    main()