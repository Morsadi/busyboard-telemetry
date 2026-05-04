#pragma once

#include <Arduino.h>
#include <WiFiClient.h>
#include <PubSubClient.h>

// Callback for incoming MQTT messages on subscribed topics.
using MqttMessageCallback = void (*)(const String& topic, const String& payload);

class MQTTManager {
public:
  MQTTManager(const char* server, int port, const char* user, const char* password,
              const char* clientPrefix = "device", const char* topicPrefix = "busyboard",
              int bufferSize = 512)
    : _user(user), _password(password),
      _clientPrefix(clientPrefix), _topicPrefix(topicPrefix),
      _client(_wifiClient)
  {
    _client.setServer(server, port);
    _client.setBufferSize(bufferSize);
    _client.setCallback(&MQTTManager::dispatch);
    _instance = this;
  }

  // Register a message handler before calling connectAtStartup().
  void onMessage(MqttMessageCallback cb) { _onMessage = cb; }

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

  // Subscribe to a topic. Wildcards (+, #) are supported.
  bool subscribe(const String& topic) {
    if (!_online || !_client.connected()) {
      Serial.println("subscribe(" + topic + ") skipped — MQTT not online");
      return false;
    }
    bool ok = _client.subscribe(topic.c_str());
    Serial.println(ok ? "Subscribed: " + topic : "Subscribe FAILED: " + topic);
    return ok;
  }

  // Topic helpers — use _topicPrefix and _deviceId for this device.
  String eventTopic()                        const { return String(_topicPrefix) + "/" + _deviceId + "/events"; }
  String switchTopic(const char* switchName) const { return String(_topicPrefix) + "/" + _deviceId + "/switch/" + String(switchName); }
  String statusTopic()                       const { return String(_topicPrefix) + "/" + _deviceId + "/status"; }

  // Topic helper for OTHER devices (subscribing to a peer's status, switches, etc.)
  String peerTopic(const String& peerDeviceId, const String& suffix) const {
    return String(_topicPrefix) + "/" + peerDeviceId + "/" + suffix;
  }

private:
  const char*  _user;
  const char*  _password;
  const char*  _clientPrefix;
  const char*  _topicPrefix;
  WiFiClient   _wifiClient;
  PubSubClient _client;

  String _deviceId;
  bool   _online     = false;
  bool   _determined = false;

  MqttMessageCallback _onMessage = nullptr;

  // PubSubClient's callback is a C function pointer with no userdata, so we
  // route through a static dispatcher backed by a singleton pointer. There's
  // only ever one MQTTManager per device.
  static MQTTManager* _instance;

  static void dispatch(char* topic, byte* payload, unsigned int length) {
    if (!_instance || !_instance->_onMessage) return;

    String topicStr(topic);
    String payloadStr;
    payloadStr.reserve(length);
    for (unsigned int i = 0; i < length; i++) payloadStr += (char)payload[i];

    _instance->_onMessage(topicStr, payloadStr);
  }

  bool tryConnect() {
    if (_client.connected()) return true;

    String clientId = String(_clientPrefix) + "-" + _deviceId;
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

// Static member definition. Header-only convention: use inline (C++17).
inline MQTTManager* MQTTManager::_instance = nullptr;
