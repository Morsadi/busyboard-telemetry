#pragma once

#include <Arduino.h>
#include <Wire.h>

class IMUManager {
public:
  IMUManager(int addr, int sdaPin, int sclPin, float moveThreshold)
    : _addr(addr), _sdaPin(sdaPin), _sclPin(sclPin), _threshold(moveThreshold) {}

  void begin() {
    Wire.begin(_sdaPin, _sclPin);
    wakeUp();
    readAccel();
    // Seed baseline so the first motionDetected() doesn't false-trigger.
    _lastAx = _ax;
    _lastAy = _ay;
    _lastAz = _az;
  }

  // Returns true if the acceleration delta since last call exceeds the threshold.
  bool motionDetected() {
    readAccel();
    float delta = abs(_ax - _lastAx) + abs(_ay - _lastAy) + abs(_az - _lastAz);
    _lastAx = _ax;
    _lastAy = _ay;
    _lastAz = _az;
    return delta > _threshold;
  }

private:
  int   _addr;
  int   _sdaPin;
  int   _sclPin;
  float _threshold;

  int16_t _lastAx = 0, _lastAy = 0, _lastAz = 0;
  int16_t _ax     = 0, _ay     = 0, _az     = 0;

  void wakeUp() {
    Wire.beginTransmission(_addr);
    Wire.write(0x6B);  // PWR_MGMT_1
    Wire.write(0x00);  // clear sleep bit
    Wire.endTransmission(true);
  }

  void readAccel() {
    Wire.beginTransmission(_addr);
    Wire.write(0x3B);  // ACCEL_XOUT_H
    Wire.endTransmission(false);
    Wire.requestFrom(_addr, 6, true);

    if (Wire.available() >= 6) {
      _ax = Wire.read() << 8 | Wire.read();
      _ay = Wire.read() << 8 | Wire.read();
      _az = Wire.read() << 8 | Wire.read();
    }
  }
};
