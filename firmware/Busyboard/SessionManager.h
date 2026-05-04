#pragma once

#include <Arduino.h>
#include <time.h>
#include "MQTTManager.h"

class SessionManager {
public:
  SessionManager(MQTTManager& mqtt, const String& deviceId, unsigned long timeoutMs)
    : _mqtt(mqtt), _deviceId(deviceId), _timeoutMs(timeoutMs) {}

  // Call when any sensor activity occurs. Starts a session if none is active.
  void recordActivity(unsigned long now) {
    if (!_active) start(now);
    _lastActivityMs = now;
  }

  // Call on a confirmed switch state change to publish the event.
  void recordSwitchChange(const char* switchName, int value, unsigned long /*now*/) {
    if (!_active) return;
    _interactionCount++;

    String payload =
      "{\"event\":\"switch_changed\","
      "\"deviceId\":\"" + _deviceId + "\","
      "\"sessionId\":\"" + _sessionId + "\","
      "\"switch\":\"" + String(switchName) + "\","
      "\"value\":" + String(value) + ","
      "\"timestamp\":\"" + timestamp() + "\"}";

    _mqtt.publish(_mqtt.switchTopic(switchName), payload);
  }

  // Call every loop iteration to check for timeout.
  void update(unsigned long now) {
    if (_active && (now - _lastActivityMs) > _timeoutMs) end(now);
  }

  bool isActive() const { return _active; }

private:
  MQTTManager&  _mqtt;
  String        _deviceId;
  unsigned long _timeoutMs;

  bool          _active           = false;
  String        _sessionId        = "";
  unsigned long _sessionStartMs   = 0;
  unsigned long _lastActivityMs   = 0;
  unsigned long _interactionCount = 0;

  void start(unsigned long now) {
    _sessionId        = timestamp();
    _active           = true;
    _sessionStartMs   = now;
    _lastActivityMs   = now;
    _interactionCount = 0;

    String payload =
      "{\"event\":\"session_started\","
      "\"deviceId\":\"" + _deviceId + "\","
      "\"sessionId\":\"" + _sessionId + "\","
      "\"timestamp\":\"" + timestamp() + "\"}";

    _mqtt.publish(_mqtt.eventTopic(), payload);
  }

  void end(unsigned long now) {
    if (!_active || _sessionId.length() == 0) return;
    unsigned long durationMs = now - _sessionStartMs;

    String payload =
      "{\"event\":\"session_ended\","
      "\"deviceId\":\"" + _deviceId + "\","
      "\"sessionId\":\"" + _sessionId + "\","
      "\"timestamp\":\"" + timestamp() + "\","
      "\"interactionCount\":" + String(_interactionCount) + ","
      "\"durationMs\":" + String(durationMs) + "}";

    _mqtt.publish(_mqtt.eventTopic(), payload);

    _active           = false;
    _sessionId        = "";
    _sessionStartMs   = 0;
    _lastActivityMs   = 0;
    _interactionCount = 0;
  }

  String timestamp() const {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) return "19700101000000";
    char buf[15];
    strftime(buf, sizeof(buf), "%Y%m%d%H%M%S", &timeinfo);
    return String(buf);
  }
};
