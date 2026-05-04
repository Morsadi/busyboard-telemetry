#pragma once

// Firmware
constexpr const char* FIRMWARE_VERSION = "0.2.0";

// Switches
constexpr int  NUM_SWITCHES = 11;
constexpr int  SWITCH_PINS[NUM_SWITCHES]  = { 13, 2, 14, 27, 26, 25, 33, 18, 32, 4, 23 };
constexpr const char* SWITCH_NAMES[NUM_SWITCHES] = {
  "SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9", "SW10", "SW11"
};
constexpr unsigned long DEBOUNCE_MS = 40;

// IMU (MPU-6050)
constexpr int   IMU_ADDR           = 0x68;
constexpr int   IMU_SDA_PIN        = 21;
constexpr int   IMU_SCL_PIN        = 22;
constexpr float IMU_MOVE_THRESHOLD = 2000.0f;

// Session
constexpr unsigned long SESSION_TIMEOUT_MS = 5000;

// MQTT
constexpr int           MQTT_STARTUP_MAX_ATTEMPTS = 4;
constexpr unsigned long MQTT_STARTUP_DELAY_MS     = 2000;
constexpr int           MQTT_BUFFER_SIZE          = 512;

// Status LED
constexpr int STATUS_LED_PIN = 5;

// Loop
constexpr unsigned long LOOP_DELAY_MS = 20;
