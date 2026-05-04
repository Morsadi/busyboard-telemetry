#pragma once

#include <Arduino.h>
#include <WiFi.h>

class WiFiManager {
public:
  // Blocks until connected. Calls onWaiting() repeatedly while waiting.
  void connect(const char* ssid, const char* password, void (*onWaiting)() = nullptr) {
    Serial.print("\nConnecting to Wi-Fi");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
      if (onWaiting) onWaiting();
      Serial.print(".");
      delay(20);
    }

    Serial.println("\nWi-Fi connected! IP: " + localIP());
  }

  bool   isConnected() const { return WiFi.status() == WL_CONNECTED; }
  String localIP()     const { return WiFi.localIP().toString(); }
};
