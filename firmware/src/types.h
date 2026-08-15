#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>

/**
 * Central type definitions to avoid ODR violations
 */

// Motor state (shared across all modules)
struct MotorState {
    float target_rpm = 0;
    float actual_rpm = 0;
    float target_torque = 0;
    float actual_current_u = 0;
    float actual_current_v = 0;
    float actual_current_w = 0;
    float dc_voltage = 400;
    float temperature_motor = 25;
    float temperature_driver = 25;
    uint32_t loop_count = 0;
    uint32_t error_code = 0;  // Bitmask for faults
    bool motor_brake = true;  // Motor brake / regenerative braking (ON by default)
    bool regen_active = false;    // True while regenerating (braking energy to battery)
    float regen_power_w = 0;      // Instantaneous regen power (W)
    float regen_energy_wh = 0;    // Accumulated regen energy (Wh)
    float dc_voltage_peak = 400;  // Peak DC voltage reached (safety/telemetry)
};

// Auto-learning state
struct AutoLearnState {
    float kp_best, ki_best, kd_best;
    float score_best;
    uint32_t converged_time;
    bool is_converged;
    uint8_t phase;
    uint8_t objective;
};

// PI Controller state
struct PIState {
    float error_integral;
    float error_last;
    float kp, ki, kd;
};

#endif // TYPES_H
