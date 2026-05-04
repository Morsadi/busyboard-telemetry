#pragma once

#include <Arduino.h>
#include <time.h>
#include "MQTTManager.h"
#include "BuzzerController.h"

struct BeepPattern {
  int count;
  int durationMs;
  int gapMs;
};

// Listens to a peer busyboard's MQTT topics and triggers the buzzer on:
//   - busyboard going offline (LWT)        → offline pattern + publish alarm
//   - busyboard coming online (transition) → online pattern
//   - both trigger switches HIGH together  → alarm pattern + publish alarm
class AlarmListener {
public:
  AlarmListener(MQTTManager& mqtt, BuzzerController& buzzer,
                const String& selfDeviceId, const String& peerDeviceId,
                const char* triggerSwitchA, const char* triggerSwitchB,
                BeepPattern online, BeepPattern offline, BeepPattern alarm)
    : _mqtt(mqtt), _buzzer(buzzer),
      _selfDeviceId(selfDeviceId), _peerDeviceId(peerDeviceId),
      _switchA(triggerSwitchA), _switchB(triggerSwitchB),
      _onlinePat(online), _offlinePat(offline), _alarmPat(alarm) {}

  // Subscribe to peer status and the two trigger switches.
  void subscribe() {
    _mqtt.subscribe(_mqtt.peerTopic(_peerDeviceId, "status"));
    _mqtt.subscribe(_mqtt.peerTopic(_peerDeviceId, String("switch/") + _switchA));
    _mqtt.subscribe(_mqtt.peerTopic(_peerDeviceId, String("switch/") + _switchB));
  }

  // Routes every MQTT message by topic suffix.
  void onMessage(const String& topic, const String& payload) {
    if      (topic.endsWith("/status"))                     handleStatus(payload);
    else if (topic.endsWith(String("/switch/") + _switchA)) handleSwitch(payload, _aOn);
    else if (topic.endsWith(String("/switch/") + _switchB)) handleSwitch(payload, _bOn);
  }

private:
  MQTTManager&      _mqtt;
  BuzzerController& _buzzer;
  String            _selfDeviceId;
  String            _peerDeviceId;
  const char*       _switchA;
  const char*       _switchB;

  BeepPattern _onlinePat;
  BeepPattern _offlinePat;
  BeepPattern _alarmPat;

  String _lastBusyBoardStatus = "";
  bool   _aOn = false;
  bool   _bOn = false;
  bool   _bothPressed = false;  // edge-trigger guard

  void handleStatus(const String& message) {
    if (message == _lastBusyBoardStatus) return;

    if (message == "online") {
      Serial.println("BusyBoard online — single beep");
      play(_onlinePat);
    } else if (message == "offline") {
      Serial.println("BusyBoard offline (LWT) — three beeps");
      publishAlarm("busyboard_offline_lwt");
      play(_offlinePat);
    }

    _lastBusyBoardStatus = message;
  }

  void handleSwitch(const String& payload, bool& stateOut) {
    // Payload: {"event":"switch_changed",...,"value":1,...}
    stateOut = payload.indexOf("\"value\":1") >= 0;

    bool nowBoth = _aOn && _bOn;

    if (nowBoth && !_bothPressed) {
      Serial.println(String("Both ") + _switchA + " and " + _switchB + " ON — alarm");
      play(_alarmPat);
      publishAlarm("both_trigger_switches_on");
    }

    _bothPressed = nowBoth;
  }

  void play(const BeepPattern& p) { _buzzer.buzz(p.count, p.durationMs, p.gapMs); }

  void publishAlarm(const char* reason) {
    String payload =
      "{\"event\":\"alarm_triggered\","
      "\"deviceId\":\"" + _selfDeviceId + "\","
      "\"sourceDeviceId\":\"" + _peerDeviceId + "\","
      "\"reason\":\"" + String(reason) + "\","
      "\"timestamp\":\"" + timestamp() + "\"}";

    _mqtt.publish(_mqtt.eventTopic(), payload);
  }

  String timestamp() const {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) return "19700101000000";
    char buf[15];
    strftime(buf, sizeof(buf), "%Y%m%d%H%M%S", &timeinfo);
    return String(buf);
  }
};
