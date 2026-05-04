#include <Arduino.h>
#include <time.h>

#include "config.h"
#include "secrets.h"
#include "StatusLed.h"
#include "WiFiManager.h"
#include "MQTTManager.h"
#include "SessionManager.h"
#include "SwitchManager.h"
#include "IMUManager.h"

// ─── Globals ─────────────────────────────────────────────────────────────────

String deviceId;

StatusLed statusLed(STATUS_LED_PIN);
WiFiManager wifiManager;
MQTTManager mqttManager(MQTT_SERVER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_BUFFER_SIZE);
IMUManager imuManager(IMU_ADDR, IMU_SDA_PIN, IMU_SCL_PIN, IMU_MOVE_THRESHOLD);
SwitchManager<NUM_SWITCHES> switchManager(SWITCH_PINS, SWITCH_NAMES, DEBOUNCE_MS);

// SessionManager needs deviceId, so it's constructed lazily inside setup().
SessionManager* sessions = nullptr;

// ─── Helpers ─────────────────────────────────────────────────────────────────

void ledBlink() { statusLed.update(); }

void onSwitchChange(const char* name, int value, unsigned long now) {
  sessions->recordActivity(now);
  sessions->recordSwitchChange(name, value, now);
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

void publishDeviceConnected() {
  struct tm timeinfo;
  char ts[15] = "19700101000000";
  if (getLocalTime(&timeinfo)) strftime(ts, sizeof(ts), "%Y%m%d%H%M%S", &timeinfo);

  String payload =
    "{\"event\":\"device_connected\","
    "\"deviceId\":\"" + deviceId + "\","
    "\"timestamp\":\"" + String(ts) + "\","
    "\"firmwareVersion\":\"" + String(FIRMWARE_VERSION) + "\"}";

  mqttManager.publish(mqttManager.eventTopic(), payload);
}

// ─── Setup ───────────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);

  statusLed.begin();
  statusLed.setState(CONNECTING);

  deviceId = "bb-" + String((uint32_t)ESP.getEfuseMac(), HEX);

  wifiManager.connect(WIFI_SSID, WIFI_PASSWORD, ledBlink);
  syncTime();

  imuManager.begin();
  switchManager.begin();

  static SessionManager s(mqttManager, deviceId, SESSION_TIMEOUT_MS);
  sessions = &s;

  statusLed.setState(CONNECTING);
  mqttManager.connectAtStartup(deviceId, MQTT_STARTUP_MAX_ATTEMPTS, MQTT_STARTUP_DELAY_MS, ledBlink);
  statusLed.setState(mqttManager.isOnline() ? ONLINE : OFFLINE);

  if (mqttManager.isOnline()) publishDeviceConnected();

  Serial.println("BusyBoard ready — device: " + deviceId);
}

// ─── Loop ────────────────────────────────────────────────────────────────────

void loop() {
  statusLed.update();
  mqttManager.loop();

  if (!mqttManager.isOnline()) statusLed.setState(OFFLINE);

  unsigned long now = millis();

  if (imuManager.motionDetected()) sessions->recordActivity(now);
  switchManager.update(now, onSwitchChange);
  sessions->update(now);

  delay(LOOP_DELAY_MS);
}
