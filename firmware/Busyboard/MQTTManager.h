#pragma once

#include <Arduino.h>
#include <WiFiClient.h>
#include <PubSubClient.h>

class MQTTManager {
public:
  MQTTManager(const char* server, int port, const char* user, const char* password, int bufferSize = 512)
    : _user(user), _password(password), _client(_wifiClient)
  {
    _client.setServer(server, port);
    _client.setBufferSize(bufferSize);
  }

  // Tries up to maxAttempts to connect, with delayMs between each.
  // Registers LWT and publishes "online" status on success.
  void connectAtStartup(const String& deviceId, int maxAttempts, unsigned long delayMs,
                        void (*onWaiting)() = nullptr) {
    _deviceId = deviceId;
    Serial.print("Connecting to MQTT");

    for (int i = 0; i < maxAttempts; i++) {
      if (tryConnect()) {
        _online = _determined = true;
        Serial.println("\nMQTT online");
        return;
      }
      Serial.print(".");

      unsigned long start = millis();
      while (millis() - start < delayMs) {
        if (onWaiting) onWaiting();
        delay(20);
      }
    }

    _online = false;
    _determined = true;
    Serial.println("\nMQTT offline — continuing without broker");
  }

  // Call every loop iteration to service incoming messages.
  void loop() {
    if (!_online) return;
    _client.loop();
    if (!_client.connected()) {
      _online = false;
      Serial.println("MQTT connection lost");
    }
  }

  bool isOnline() const { return _online; }

  // Publishes payload to topic. Logs to serial regardless of success.
  bool publish(const String& topic, const String& payload) {
    if (_online && _client.connected()) {
      bool ok = _client.publish(topic.c_str(), payload.c_str());
      Serial.println(ok ? payload : payload + " [PUBLISH FAILED]");
      return ok;
    }
    Serial.println(payload + (_determined ? " [MQTT OFFLINE]" : " [MQTT NOT READY]"));
    return false;
  }

  // Topic helpers
  String eventTopic()                          const { return "busyboard/" + _deviceId + "/events"; }
  String switchTopic(const char* switchName)   const { return "busyboard/" + _deviceId + "/switch/" + String(switchName); }
  String statusTopic()                         const { return "busyboard/" + _deviceId + "/status"; }

private:
  const char*  _user;
  const char*  _password;
  WiFiClient   _wifiClient;
  PubSubClient _client;

  String _deviceId;
  bool   _online     = false;
  bool   _determined = false;

  bool tryConnect() {
    if (_client.connected()) return true;

    String clientId = "busyboard-" + _deviceId;
    bool ok = _client.connect(
      clientId.c_str(),
      _user, _password,
      statusTopic().c_str(),  // LWT topic
      1,                      // LWT QoS
      true,                   // LWT retain
      "offline"               // LWT payload
    );

    if (ok) publishStatus("online");
    return ok;
  }

  void publishStatus(const char* value) {
    bool ok = _client.publish(statusTopic().c_str(), value, true);
    Serial.println(ok
      ? String("{\"status\":\"") + value + "\"}"
      : String("{\"status\":\"") + value + "\",\"note\":\"STATUS PUBLISH FAILED\"}");
  }
};
