import os
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 30
SUPABASE_DB_URL: str = os.environ.get("SUPABASE_DB_URL", "")