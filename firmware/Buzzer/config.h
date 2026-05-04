#pragma once

// Firmware
constexpr const char* FIRMWARE_VERSION = "0.1.0";

// Pins
constexpr int BUZZER_PIN     = 13;
constexpr int STATUS_LED_PIN = 14;

// Buzz patterns: count, durationMs, gapMs
constexpr int           BEEP_BUSYBOARD_ONLINE_COUNT     = 1;
constexpr int           BEEP_BUSYBOARD_ONLINE_DURATION  = 120;
constexpr int           BEEP_BUSYBOARD_ONLINE_GAP       = 0;

constexpr int           BEEP_BUSYBOARD_OFFLINE_COUNT    = 3;
constexpr int           BEEP_BUSYBOARD_OFFLINE_DURATION = 250;
constexpr int           BEEP_BUSYBOARD_OFFLINE_GAP      = 150;

constexpr int           BEEP_SWITCH_ALARM_COUNT         = 2;
constexpr int           BEEP_SWITCH_ALARM_DURATION      = 200;
constexpr int           BEEP_SWITCH_ALARM_GAP           = 120;

// Switches that trigger an alarm when both are HIGH at the same time.
constexpr const char* TRIGGER_SWITCH_A = "SW8";
constexpr const char* TRIGGER_SWITCH_B = "SW9";

// MQTT
constexpr int           MQTT_STARTUP_MAX_ATTEMPTS = 4;
constexpr unsigned long MQTT_STARTUP_DELAY_MS     = 2000;
constexpr int           MQTT_BUFFER_SIZE          = 512;

// Loop
constexpr unsigned long LOOP_DELAY_MS = 20;
