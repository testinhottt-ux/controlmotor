/*
 * AUTO-LEARNING ENGINE - Motor Parameter Optimization
 * Purpose: Automatic Kp/Ki/Kd tuning using relay method + Ziegler-Nichols
 * Algorithm: Astrom-Hagglund relay identification (30 second convergence)
 * Thread: Core 1 (FreeRTOS priority 1, runs during idle CPU)
 */

#include <Arduino.h>
#include <math.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <EEPROM.h>
#include "types.h"

// ============ CONFIGURATION ============

#define AUTOLEARN_MEASUREMENT_BUFFER_SIZE 1000
#define AUTOLEARN_MEASUREMENT_WINDOW_MS 5000      // 5 second window for relay test
#define AUTOLEARN_ANALYSIS_WINDOW 300             // 300 samples @ 10Hz = 30 seconds
#define AUTOLEARN_INTERVAL_MS 100                 // Check every 100ms
#define AUTOLEARN_CONVERGENCE_TIME_MS 300000      // 5 minutes to declare converged

// External references (from main.cpp)
extern MotorState motor_state;

extern struct TuningParams {
    float kp;
    float ki;
    float kd;
    float max_current;
    float max_voltage;
    uint8_t control_mode;
    uint8_t sensor_mode;
} tuning;

extern SemaphoreHandle_t state_mutex;
extern void handle_ble_command(uint8_t cmd, float value);
extern void eeprom_save_config(void);

// ============ AUTO-LEARNING STATE ============

typedef enum {
    AUTOLEARN_IDLE = 0,
    AUTOLEARN_RELAY_TEST = 1,
    AUTOLEARN_ANALYSIS = 2,
    AUTOLEARN_OPTIMIZATION = 3,
    AUTOLEARN_CONVERGED = 4
} AutoLearnPhase;

// AutoLearnState type is defined in types.h

// Global auto-learning state
static AutoLearnState autolearn = {
    .kp_best = 0.6,
    .ki_best = 0.1,
    .kd_best = 0.05,
    .score_best = 0,
    .converged_time = 0,
    .is_converged = false,
    .phase = AUTOLEARN_IDLE,
    .objective = 0  // Balanced
};

// Measurement buffer
static float rpm_buffer[AUTOLEARN_MEASUREMENT_BUFFER_SIZE];
static float current_buffer[AUTOLEARN_MEASUREMENT_BUFFER_SIZE];
static uint32_t measurement_count = 0;

// Flags for control
static bool user_requested_autotune = false;
static bool autolearn_enabled = false;

// ============ PUBLIC INTERFACE ============

void autolearn_request_tuning(void) {
    user_requested_autotune = true;
    autolearn_enabled = true;
    autolearn.phase = AUTOLEARN_RELAY_TEST;
    measurement_count = 0;
    Serial.println("[AutoLearn] Tuning requested by user");
}

void autolearn_enable_learning(bool enable) {
    autolearn_enabled = enable;
    if (enable) {
        autolearn.phase = AUTOLEARN_OPTIMIZATION;
        Serial.println("[AutoLearn] Continuous learning enabled");
    } else {
        autolearn.phase = AUTOLEARN_IDLE;
        Serial.println("[AutoLearn] Learning disabled");
    }
}

void autolearn_set_objective(uint8_t objective) {
    // 0=balanced, 1=power, 2=efficiency, 3=smoothness
    autolearn.objective = objective;
    Serial.printf("[AutoLearn] Objective set to: %d\n", objective);
}

AutoLearnState* autolearn_get_state(void) {
    return &autolearn;
}

// ============ HELPER FUNCTIONS ============

static float calculate_current_ripple(float *buffer, uint16_t size) {
    /*
     * Calculate RMS deviation from mean
     * Measures how "smooth" current is (lower = better)
     */
    if (size < 2) return 0;
    
    float mean = 0;
    for (uint16_t i = 0; i < size; i++) {
        mean += fabs(buffer[i]);
    }
    mean /= size;
    
    float variance = 0;
    for (uint16_t i = 0; i < size; i++) {
        float dev = fabs(buffer[i]) - mean;
        variance += dev * dev;
    }
    variance /= size;
    
    return sqrt(variance);
}

static float calculate_performance_score(void) {
    /*
     * Composite score: error + overshoot + ripple
     * Scale: 0.0 (worst) to 1.0 (best)
     * 
     * Objective-weighted:
     *   Balanced (0): 50% error + 30% overshoot + 20% ripple
     *   Power (1):    60% error + 25% overshoot + 15% ripple
     *   Efficiency (2): 40% error + 20% overshoot + 40% ripple
     *   Smoothness (3): 30% error + 20% overshoot + 50% ripple
     */
    
    if (motor_state.target_rpm == 0) return 0;
    
    // Steady-state error
    float sse = fabs(motor_state.actual_rpm - motor_state.target_rpm);
    float sse_score = 1.0 - (sse / fmax(motor_state.target_rpm, 1.0));
    sse_score = fmax(0, fmin(1.0, sse_score));
    
    // Overshoot (simplified: any deviation above target is bad)
    float overshoot = fmax(0, (motor_state.actual_rpm - motor_state.target_rpm) / fmax(motor_state.target_rpm, 1.0));
    float overshoot_score = 1.0 - (overshoot * 0.5);  // 50% penalty per overshoot unit
    overshoot_score = fmax(0, fmin(1.0, overshoot_score));
    
    // Current ripple (smoothness)
    float ripple_score = 1.0 / (1.0 + calculate_current_ripple(current_buffer, 50));
    ripple_score = fmax(0, fmin(1.0, ripple_score));
    
    // Apply objective weights
    float score = 0;
    switch(autolearn.objective) {
        case 0:  // Balanced
            score = sse_score * 0.5 + overshoot_score * 0.3 + ripple_score * 0.2;
            break;
        case 1:  // Power
            score = sse_score * 0.6 + overshoot_score * 0.25 + ripple_score * 0.15;
            break;
        case 2:  // Efficiency
            score = sse_score * 0.4 + overshoot_score * 0.2 + ripple_score * 0.4;
            break;
        case 3:  // Smoothness
            score = sse_score * 0.3 + overshoot_score * 0.2 + ripple_score * 0.5;
            break;
        default:
            score = sse_score * 0.5 + overshoot_score * 0.3 + ripple_score * 0.2;
    }
    
    return score;
}

// ============ RELAY AUTO-TUNING ALGORITHM ============

static void autolearn_relay_perturbation(void) {
    /*
     * Phase 1: Apply relay feedback to induce sustained oscillations
     * Duration: 30 seconds at 10kHz = 300,000 control loops
     * The motor oscillates at its resonant frequency with amplitude proportional to gain
     */
    
    if (measurement_count >= AUTOLEARN_ANALYSIS_WINDOW) {
        Serial.println("[AutoLearn] Relay test complete, moving to analysis...");
        autolearn.phase = AUTOLEARN_ANALYSIS;
        measurement_count = 0;
        return;
    }
    
    // Read current error (simplified: just use RPM error)
    float rpm_error = motor_state.actual_rpm - motor_state.target_rpm;
    
    // Relay: max PWM if error positive, zero if negative
    // This forces oscillation around setpoint
    if (rpm_error > 0) {
        motor_state.target_torque = -50;  // Negative torque to pull back down
    } else {
        motor_state.target_torque = 50;   // Positive torque to push up
    }
    
    // Log oscillations for analysis
    if (measurement_count < AUTOLEARN_MEASUREMENT_BUFFER_SIZE) {
        rpm_buffer[measurement_count] = motor_state.actual_rpm;
        current_buffer[measurement_count] = fabs(motor_state.actual_current_u);
        measurement_count++;
    }
}

static void autolearn_analysis(void) {
    /*
     * Phase 2: Analyze recorded oscillations to find resonant frequency and gain
     * Uses Astrom-Hagglund method: measure zero crossings and amplitude
     */
    
    Serial.println("[AutoLearn] Analyzing oscillation data...");
    
    if (measurement_count == 0) {
        Serial.println("[AutoLearn] ERROR: No measurement data!");
        autolearn.phase = AUTOLEARN_IDLE;
        return;
    }
    
    // Find peak-to-peak amplitude
    float max_rpm = -999999, min_rpm = 999999;
    for (uint16_t i = 0; i < measurement_count; i++) {
        max_rpm = fmax(max_rpm, rpm_buffer[i]);
        min_rpm = fmin(min_rpm, rpm_buffer[i]);
    }
    float amplitude = (max_rpm - min_rpm) / 2.0;
    
    // Find zero crossings (oscillations around setpoint)
    int crossing_count = 0;
    uint16_t crossing_indices[100];
    float setpoint = (max_rpm + min_rpm) / 2.0;
    
    for (uint16_t i = 1; i < measurement_count; i++) {
        // Zero crossing detection: sign change
        if ((rpm_buffer[i-1] < setpoint && rpm_buffer[i] >= setpoint) ||
            (rpm_buffer[i-1] >= setpoint && rpm_buffer[i] < setpoint)) {
            if (crossing_count < 100) {
                crossing_indices[crossing_count++] = i;
            }
        }
    }
    
    // Calculate period from zero crossings
    float period_samples = 0;
    if (crossing_count > 2) {
        for (int i = 1; i < crossing_count; i++) {
            period_samples += (crossing_indices[i] - crossing_indices[i-1]);
        }
        period_samples /= (crossing_count - 1);
    }
    
    // Convert sample period to seconds (at 10Hz measurement = 100ms per sample)
    float period_sec = period_samples * 0.1;  // Each sample is 0.1 seconds
    
    // Astrom-Hagglund gain calculation
    // Kc = (4 * Max_Output) / (π * Amplitude)
    float Kc = (4.0 * 50.0) / (3.14159 * fmax(amplitude, 0.1));
    
    // Ziegler-Nichols tuning (classic PID from Kc and period)
    autolearn.kp_best = 0.6 * Kc;
    autolearn.ki_best = (1.2 * Kc) / fmax(period_sec, 0.1);
    autolearn.kd_best = 0.075 * Kc * fmax(period_sec, 0.1);
    
    // Clamp to reasonable ranges
    autolearn.kp_best = fmax(0.1, fmin(5.0, autolearn.kp_best));
    autolearn.ki_best = fmax(0.01, fmin(1.0, autolearn.ki_best));
    autolearn.kd_best = fmax(0.01, fmin(0.5, autolearn.kd_best));
    
    // Apply new tuning
    xSemaphoreTake(state_mutex, portMAX_DELAY);
    tuning.kp = autolearn.kp_best;
    tuning.ki = autolearn.ki_best;
    tuning.kd = autolearn.kd_best;
    xSemaphoreGive(state_mutex);
    
    // Save to EEPROM
    eeprom_save_config();
    
    Serial.printf("[AutoLearn] Analysis complete!\n");
    Serial.printf("  Amplitude: %.1f RPM, Period: %.2f s, Crossing count: %d\n", 
                  amplitude, period_sec, crossing_count);
    Serial.printf("  Kc=%.3f, Kp=%.3f Ki=%.3f Kd=%.3f\n",
                  Kc, autolearn.kp_best, autolearn.ki_best, autolearn.kd_best);
    
    // Move to optimization phase
    motor_state.target_torque = 0;  // Stop relay
    autolearn.phase = AUTOLEARN_OPTIMIZATION;
    autolearn.score_best = calculate_performance_score();
    autolearn.converged_time = xTaskGetTickCount();
    measurement_count = 0;
}

// ============ CONTINUOUS OPTIMIZATION ============

static void autolearn_continuous_optimization(void) {
    /*
     * Phase 3: Fine-tune parameters using small random perturbations
     * Keeps best parameters that improve performance score
     * Converges when no improvement for 5 minutes
     */
    
    // Measure current performance
    float current_score = calculate_performance_score();
    
    // If performance improved, accept and save
    if (current_score > autolearn.score_best * 1.01) {  // 1% improvement threshold
        autolearn.score_best = current_score;
        autolearn.converged_time = xTaskGetTickCount();
        
        // Small exploratory adjustment
        if (random(0, 10) < 3) {  // 30% chance of small Kp adjustment
            float delta_kp = (random(-100, 100) / 1000.0);  // ±0.1
            autolearn.kp_best += delta_kp;
            autolearn.kp_best = fmax(0.1, fmin(5.0, autolearn.kp_best));
            
            xSemaphoreTake(state_mutex, portMAX_DELAY);
            tuning.kp = autolearn.kp_best;
            xSemaphoreGive(state_mutex);
        }
        
        // Save periodically
        if (autolearn.score_best > 0.8) {  // Only save if good
            eeprom_save_config();
            Serial.printf("[AutoLearn] Score improved to %.2f, saving...\n", autolearn.score_best);
        }
    }
    
    // Check for convergence (no improvement for 5 minutes)
    uint32_t time_since_improvement = xTaskGetTickCount() - autolearn.converged_time;
    if (time_since_improvement > AUTOLEARN_CONVERGENCE_TIME_MS) {
        autolearn.is_converged = true;
        autolearn.phase = AUTOLEARN_CONVERGED;
        Serial.printf("[AutoLearn] Converged! Final score: %.2f\n", autolearn.score_best);
    }
}

// ============ MAIN AUTO-LEARNING TASK ============

void autolearn_task(void *pvParameter) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    Serial.println("[AutoLearn] Task started on Core 1");
    
    while(1) {
        // Only process if enabled
        if (autolearn_enabled) {
            
            switch(autolearn.phase) {
                
                case AUTOLEARN_IDLE:
                    // Wait for user request
                    if (user_requested_autotune) {
                        user_requested_autotune = false;
                        autolearn.phase = AUTOLEARN_RELAY_TEST;
                        measurement_count = 0;
                        Serial.println("[AutoLearn] Starting relay auto-tuning...");
                    }
                    break;
                
                case AUTOLEARN_RELAY_TEST:
                    autolearn_relay_perturbation();
                    break;
                
                case AUTOLEARN_ANALYSIS:
                    autolearn_analysis();
                    break;
                
                case AUTOLEARN_OPTIMIZATION:
                    autolearn_continuous_optimization();
                    break;
                
                case AUTOLEARN_CONVERGED:
                    // Occasional exploration
                    if (random(0, 1000) < 5) {  // 0.5% chance
                        float trial_kp = autolearn.kp_best + (random(-50, 50) / 1000.0);
                        trial_kp = fmax(0.1, fmin(5.0, trial_kp));
                        
                        xSemaphoreTake(state_mutex, portMAX_DELAY);
                        float saved_kp = tuning.kp;
                        tuning.kp = trial_kp;
                        xSemaphoreGive(state_mutex);
                        
                        float trial_score = calculate_performance_score();
                        if (trial_score > autolearn.score_best) {
                            autolearn.kp_best = trial_kp;
                            autolearn.score_best = trial_score;
                            eeprom_save_config();
                        } else {
                            xSemaphoreTake(state_mutex, portMAX_DELAY);
                            tuning.kp = saved_kp;
                            xSemaphoreGive(state_mutex);
                        }
                    }
                    break;
            }
        }
        
        // Task delay
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(AUTOLEARN_INTERVAL_MS));
    }
}

// ============ END OF FILE ============
