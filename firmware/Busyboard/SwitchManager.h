#pragma once

#include <Arduino.h>

// Callback fires once per confirmed state change.
using SwitchChangeCallback = void (*)(const char* name, int value, unsigned long now);

template <int N>
class SwitchManager {
public:
  SwitchManager(const int (&pins)[N], const char* const (&names)[N], unsigned long debounceMs)
    : _pins(pins), _names(names), _debounceMs(debounceMs) {}

  void begin() {
    for (int i = 0; i < N; i++) {
      pinMode(_pins[i], INPUT_PULLDOWN);
      _state[i]        = digitalRead(_pins[i]);
      _lastDebounce[i] = 0;
    }
  }

  // Call every loop iteration. Fires onChange for each confirmed state change.
  void update(unsigned long now, SwitchChangeCallback onChange) {
    for (int i = 0; i < N; i++) {
      int reading = digitalRead(_pins[i]);

      if (reading != _state[i] && (now - _lastDebounce[i]) >= _debounceMs) {
        _lastDebounce[i] = now;
        _state[i]        = reading;
        if (onChange) onChange(_names[i], reading == HIGH ? 1 : 0, now);
      }
    }
  }

private:
  const int (&_pins)[N];
  const char* const (&_names)[N];
  unsigned long _debounceMs;

  int           _state[N]        = {};
  unsigned long _lastDebounce[N] = {};
};
