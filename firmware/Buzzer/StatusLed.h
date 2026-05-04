#pragma once

#include <Arduino.h>

enum ConnectionState {
  CONNECTING,
  ONLINE,
  OFFLINE
};

class StatusLed {
public:
  StatusLed(int pin) : _pin(pin) {}

  void begin() {
    ledcAttach(_pin, 5000, 8);
    off();
  }

  void setState(ConnectionState state) {
    _state = state;
  }

  void update() {
    switch (_state) {
      case CONNECTING:
        pulse();
        break;

      case ONLINE:
        on();
        break;

      case OFFLINE:
        off();
        break;
    }
  }

private:
  int _pin;
  ConnectionState _state = CONNECTING;

  void on() {
    ledcWrite(_pin, 255);
  }

  void off() {
    ledcWrite(_pin, 0);
  }

  void pulse() {
    static int brightness = 20;
    static int direction = 1;
    static unsigned long lastUpdate = 0;

    if (millis() - lastUpdate < 20) {
      return;
    }

    lastUpdate = millis();

    brightness += direction * 3;

    if (brightness >= 255) {
      brightness = 255;
      direction = -1;
    }

    if (brightness <= 20) {
      brightness = 20;
      direction = 1;
    }

    ledcWrite(_pin, brightness);
  }
};