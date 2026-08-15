/*
 * Bluetooth LE Interface STUB - Minimal for compilation
 */

#include <Arduino.h>

// Stub implementations to avoid compilation errors

void ble_init() {
    Serial.println("BLE init (stub)");
}

void ble_publish_telemetry() {
    // Stub
}

extern "C" {
    void handle_autolearn_command() {
        // Stub
    }
}
