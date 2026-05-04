#pragma once

#include <Arduino.h>

class BuzzerController {
public:
  explicit BuzzerController(int pin) : _pin(pin) {}

  void begin() {
    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW);
  }

  // Plays a pattern: `count` beeps, each `durationMs` long, with `gapMs` between.
  void buzz(int count, int durationMs, int gapMs) {
    for (int i = 0; i < count; i++) {
      digitalWrite(_pin, HIGH);
      delay(durationMs);
      digitalWrite(_pin, LOW);
      if (i < count - 1) delay(gapMs);
    }
  }

private:
  int _pin;
};
