import os
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST : str = "localhost"
MQTT_PORT : int = 1883
MQTT_USER : str = os.environ.get("MQTT_USER", "")
MQTT_PASSWORD : str = os.environ.get("MQTT_PASSWORD", "")
MQTT_KEEPALIVE : int = 30
SUPABASE_DB_URL : str = os.environ.get("SUPABASE_DB_URL", "")