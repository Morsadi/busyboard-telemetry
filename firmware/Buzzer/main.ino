#include <Arduino.h>
#include <time.h>

#include "config.h"
#include "secrets.h"
#include "StatusLed.h"
#include "WiFiManager.h"
#include "MQTTManager.h"
#include "BuzzerController.h"
#include "AlarmListener.h"

// ─── Globals ─────────────────────────────────────────────────────────────────

String deviceId;

StatusLed statusLed(STATUS_LED_PIN);
WiFiManager wifiManager;
MQTTManager mqttManager(MQTT_SERVER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, "buzzer", "busyboard", MQTT_BUFFER_SIZE);
BuzzerController buzzer(BUZZER_PIN);

// AlarmListener needs deviceId, so it's constructed lazily inside setup().
AlarmListener* alarms = nullptr;

// ─── Helpers ─────────────────────────────────────────────────────────────────

void ledBlink() { statusLed.update(); }

void onMqttMessage(const String& topic, const String& payload) {
  if (alarms) alarms->onMessage(topic, payload);
}

void syncTime() {
  configTime(0, 0, "pool.ntp.org");
  Serial.print("Syncing time");

  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    statusLed.update();
    Serial.print(".");
    delay(20);
  }
  Serial.println("\nTime synced!");
}

// ─── Setup ───────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);

  buzzer.begin();
  statusLed.begin();
  statusLed.setState(CONNECTING);

  deviceId = "buzzer-bb-01";

  wifiManager.connect(WIFI_SSID, WIFI_PASSWORD, ledBlink);
  syncTime();

  mqttManager.onMessage(onMqttMessage);

  static AlarmListener listener(
    mqttManager, buzzer,
    deviceId, BUSYBOARD_DEVICE_ID,
    TRIGGER_SWITCH_A, TRIGGER_SWITCH_B,
    { BEEP_BUSYBOARD_ONLINE_COUNT,  BEEP_BUSYBOARD_ONLINE_DURATION,  BEEP_BUSYBOARD_ONLINE_GAP  },
    { BEEP_BUSYBOARD_OFFLINE_COUNT, BEEP_BUSYBOARD_OFFLINE_DURATION, BEEP_BUSYBOARD_OFFLINE_GAP },
    { BEEP_SWITCH_ALARM_COUNT,      BEEP_SWITCH_ALARM_DURATION,      BEEP_SWITCH_ALARM_GAP      }
  );
  alarms = &listener;

  statusLed.setState(CONNECTING);
  mqttManager.connectAtStartup(deviceId, MQTT_STARTUP_MAX_ATTEMPTS, MQTT_STARTUP_DELAY_MS, ledBlink);
  statusLed.setState(mqttManager.isOnline() ? ONLINE : OFFLINE);

  if (mqttManager.isOnline()) alarms->subscribe();

  Serial.println("Buzzer ready — device: " + deviceId);
}

// ─── Loop ────────────────────────────────────────────────────────────────────

void loop() {
  statusLed.update();
  mqttManager.loop();

  if (!mqttManager.isOnline()) statusLed.setState(OFFLINE);

  delay(LOOP_DELAY_MS);
}
