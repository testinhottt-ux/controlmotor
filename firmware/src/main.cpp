/*
 * MOTOR CONTROL INVERTER - Main Firmware
 * Platform: ESP32-WROOM-32E
 * Purpose: Universal PMSM/BLDC controller with Bluetooth tuning
 * Author: OpenCode Motor Control Project
 * Date: 2026-08-13
 *
 * Architecture:
 * - Core 0: Real-time FOC loop (100µs cycle) - HIGH PRIORITY
 * - Core 1: Bluetooth API + telemetry streaming - NORMAL PRIORITY
 * - Both cores share: Motor state, EEPROM configuration
 */

#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <EEPROM.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// SimpleFOC includes (commented out for build without lib)
// #include <SimpleFOC.h>

// Central type definitions
#include "types.h"

// Module forward declarations
void foc_init(void);
void foc_execute(void);
void foc_execute_with_pwm(void);
void foc_set_rpm(float rpm);
void foc_update_tuning(float kp, float ki, float kd);
void ble_init(void);
void ble_publish_telemetry(void);
void autolearn_task(void *pvParameter);
void autolearn_request_tuning(void);
void autolearn_enable_learning(bool enable);
void autolearn_set_objective(uint8_t objective);
AutoLearnState* autolearn_get_state(void);
extern uint16_t foc_pwm_u, foc_pwm_v, foc_pwm_w;

// ============ CONFIGURATION DEFINES ============

#define MOTOR_CONTROL_LOOP_FREQ_HZ 10000       // 10 kHz control frequency (100µs)
#define MOTOR_CONTROL_LOOP_TIME_US 100         // Microseconds per cycle
#define PWM_FREQUENCY_HZ 20000                 // 20 kHz PWM (gate driver)
#define ADC_RESOLUTION 12                      // 12-bit ADC resolution
#define EEPROM_SIZE 4096                       // ESP32 EEPROM partition

#define DEBUG_ENABLED 1
#define LOG_LEVEL 2                            // 0=ERROR, 1=WARN, 2=INFO, 3=DEBUG

// ============ PIN DEFINITIONS ============

// PWM Outputs (to DRV8302 gate driver)
#define GPIO_PWM_U_HS 32                       // Phase U high-side
#define GPIO_PWM_V_HS 33                       // Phase V high-side
#define GPIO_PWM_W_HS 26                       // Phase W high-side
#define GPIO_PWM_EN 25                         // Gate driver enable
#define GPIO_PWM_FAULT 23                      // Fault input (active low)

// ADC Inputs (current sensing + diagnostics)
#define GPIO_ADC_I_U 36                        // Current phase U (ADC1_0)
#define GPIO_ADC_I_V 37                        // Current phase V (ADC1_1)
#define GPIO_ADC_I_W 38                        // Current phase W (ADC1_2)
#define GPIO_ADC_VDC 39                        // DC link voltage (ADC1_3)
#define GPIO_ADC_TEMP_MOTOR 34                 // Motor temperature (ADC1_6)
#define GPIO_ADC_TEMP_DRIVER 35                // Driver temperature (ADC1_7)

// Hall Effect Sensors (rotor position feedback)
#define GPIO_HALL_A 5                          // Hall sensor A
#define GPIO_HALL_B 18                         // Hall sensor B
#define GPIO_HALL_C 19                         // Hall sensor C

// UART Debug
#define UART_TX 17
#define UART_RX 16
#define UART_BAUD 115200

// ============ GLOBAL STATE VARIABLES ============

// Motor control parameters (type defined in types.h)
MotorState motor_state;

// PID Tuning parameters (stored in EEPROM)
struct TuningParams {
    float kp = 0.5;
    float ki = 0.1;
    float kd = 0.05;
    float max_current = 50.0;  // Amperes
    float max_voltage = 400.0;
    uint8_t control_mode = 0;  // 0=FOC, 1=BLDC commutation
    uint8_t sensor_mode = 0;   // 0=Sensorless, 1=Hall
} tuning;

// Mutex for thread-safe state updates
SemaphoreHandle_t state_mutex;

// ============ FORWARD DECLARATIONS ============
void motor_control_task(void *pvParameter);
void bluetooth_task(void *pvParameter);
void setup_adc(void);
void setup_pwm(void);
void setup_hall_sensors(void);
void read_currents(void);
void update_rotor_position(void);
void foc_loop(void);
void safety_check(void);
void eeprom_load_config(void);
void eeprom_save_config(void);
void setup_ble(void);
void handle_ble_command(uint8_t cmd, float value);

// ============ SETUP FUNCTION ============
void setup() {
    // Initialize serial communication
    Serial.begin(UART_BAUD);
    delay(500);
    
    Serial.println("\n\n=== MOTOR CONTROL INVERTER - STARTUP ===");
    Serial.printf("ESP32 MAC: %llX\n", ESP.getEfuseMac());
    Serial.printf("Free heap: %u bytes\n", ESP.getFreeHeap());
    Serial.printf("Flash size: %u bytes\n", ESP.getFlashChipSize());
    
    // Initialize EEPROM
    EEPROM.begin(EEPROM_SIZE);
    eeprom_load_config();
    
    // Initialize hardware
    setup_adc();
    setup_pwm();
    setup_hall_sensors();
    
    // Initialize Bluetooth LE with tuning interface
    ble_init();
    
    // Initialize FOC controller
    foc_init();
    
    // Create mutex for thread-safe state access
    state_mutex = xSemaphoreCreateMutex();
    if (state_mutex == NULL) {
        Serial.println("ERROR: Failed to create mutex!");
        while(1) delay(1000);
    }
    
    // Create FreeRTOS tasks
    // Task 1: Motor control (Core 0, high priority)
    xTaskCreatePinnedToCore(
        motor_control_task,          // Function
        "motor_control",             // Name
        8192,                        // Stack size (bytes)
        NULL,                        // Parameter
        configMAX_PRIORITIES - 1,    // Priority (highest)
        NULL,                        // Task handle
        0                            // Core ID (0 = Core 0)
    );
    
    // Task 2: Auto-learning (Core 1, normal priority)
    xTaskCreatePinnedToCore(
        autolearn_task,
        "autolearn",
        8192,
        NULL,
        2,                           // Priority
        NULL,
        1                            // Core ID (1 = Core 1)
    );
    
    // Task 3: Bluetooth/telemetry (Core 1, lower priority)
    xTaskCreatePinnedToCore(
        bluetooth_task,
        "bluetooth",
        4096,
        NULL,
        1,                           // Lower priority
        NULL,
        1                            // Core ID (1 = Core 1)
    );
    
    Serial.println("=== STARTUP COMPLETE ===");
}

// ============ LOOP FUNCTION (unused - controlled by FreeRTOS tasks) ============
void loop() {
    // All work done in FreeRTOS tasks; loop is not used
    vTaskDelete(NULL);  // Delete this task
}

// ============ MOTOR CONTROL TASK (Core 0, 10 kHz) ============
void motor_control_task(void *pvParameter) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    Serial.println("Motor control task started on Core 0");
    
    while (1) {
        uint32_t start_time = micros();
        
        // === CONTROL LOOP (target: 100µs) ===
        
        // 1. Read sensors (5µs)
        read_currents();
        
        // 2. FOC algorithm or motor off (50µs)
        //    Freio motor: se o alvo é 0 RPM e o freio motor está ATIVO,
        //    o FOC continua ativo aplicando torque de frenagem (parada ativa).
        //    Se o freio motor está OFF, o motor fica em roda livre (coast).
        bool should_drive = (motor_state.target_rpm != 0 || motor_state.motor_brake)
                            && motor_state.error_code == 0;
        if (should_drive) {
            foc_execute_with_pwm();
            
            // Write PWM outputs (from FOC calculation)
            ledcWrite(0, foc_pwm_u);
            ledcWrite(1, foc_pwm_v);
            ledcWrite(2, foc_pwm_w);
        } else {
            // Motor off: zero PWM (coast)
            ledcWrite(0, 0);
            ledcWrite(1, 0);
            ledcWrite(2, 0);
        }
        
        // 3. Safety checks (15µs)
        safety_check();
        
        // 4. Update diagnostic data
        motor_state.loop_count++;
        
        // Wait for next cycle
        uint32_t elapsed = micros() - start_time;
        if (elapsed > MOTOR_CONTROL_LOOP_TIME_US) {
            Serial.printf("WARNING: Control loop overrun! %lu µs > %u µs\n", 
                         elapsed, MOTOR_CONTROL_LOOP_TIME_US);
        }
        
        // Block until next 100µs boundary
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(MOTOR_CONTROL_LOOP_TIME_US / 1000));
    }
}

// ============ BLUETOOTH TASK (Core 1, ~100 Hz telemetry) ============
void bluetooth_task(void *pvParameter) {
    Serial.println("Bluetooth task started on Core 1");
    
    // Allow time for BLE to initialize
    vTaskDelay(pdMS_TO_TICKS(1000));
    
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    while (1) {
        // Publish telemetry via BLE at 100 Hz
        ble_publish_telemetry();
        
        // Sleep 10ms (100 Hz telemetry rate)
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(10));
    }
}

// ============ HARDWARE SETUP FUNCTIONS ============

void setup_adc(void) {
    Serial.println("Initializing ADC...");
    
    // ADC1 is used for motor sensing
    analogReadResolution(ADC_RESOLUTION);  // 12-bit resolution
    
    // Configure ADC pins
    pinMode(GPIO_ADC_I_U, INPUT);
    pinMode(GPIO_ADC_I_V, INPUT);
    pinMode(GPIO_ADC_I_W, INPUT);
    pinMode(GPIO_ADC_VDC, INPUT);
    pinMode(GPIO_ADC_TEMP_MOTOR, INPUT);
    pinMode(GPIO_ADC_TEMP_DRIVER, INPUT);
    
    Serial.println("ADC initialized");
}

void setup_pwm(void) {
    Serial.println("Initializing PWM...");
    
    // Setup PWM using ledc (LED Control peripheral)
    // Frequency: 20 kHz, Resolution: 10-bit
    
    ledcSetup(0, PWM_FREQUENCY_HZ, 10);  // Channel 0
    ledcSetup(1, PWM_FREQUENCY_HZ, 10);  // Channel 1
    ledcSetup(2, PWM_FREQUENCY_HZ, 10);  // Channel 2
    
    ledcAttachPin(GPIO_PWM_U_HS, 0);
    ledcAttachPin(GPIO_PWM_V_HS, 1);
    ledcAttachPin(GPIO_PWM_W_HS, 2);
    
    // Gate driver enable pin
    pinMode(GPIO_PWM_EN, OUTPUT);
    digitalWrite(GPIO_PWM_EN, LOW);  // Initially disabled
    
    // Fault input pin
    pinMode(GPIO_PWM_FAULT, INPUT);
    
    // Set initial PWM to 0%
    ledcWrite(0, 0);
    ledcWrite(1, 0);
    ledcWrite(2, 0);
    
    Serial.println("PWM initialized at 20 kHz");
}

void setup_hall_sensors(void) {
    Serial.println("Initializing Hall sensors...");
    
    pinMode(GPIO_HALL_A, INPUT);
    pinMode(GPIO_HALL_B, INPUT);
    pinMode(GPIO_HALL_C, INPUT);
    
    // Interrupt handlers would be attached here for real Hall commutation
    // For now: polling in read_rotor_position()
    
    Serial.println("Hall sensors initialized");
}

// ============ MOTOR CONTROL FUNCTIONS ============

void read_currents(void) {
    // Read ADC and convert to amperes
    // Sensitivity: 1V = 100A (0.001Ω shunt)
    // ADC range: 0-4095 (0-3.3V)
    // Conversion: (ADC * 3.3 / 4095) / 0.033 Ω ≈ A
    
    uint16_t adc_u = analogRead(GPIO_ADC_I_U);
    uint16_t adc_v = analogRead(GPIO_ADC_I_V);
    uint16_t adc_w = analogRead(GPIO_ADC_I_W);
    
    // Scale to amperes (simplification)
    motor_state.actual_current_u = (adc_u - 2048) * 100.0 / 2048.0;
    motor_state.actual_current_v = (adc_v - 2048) * 100.0 / 2048.0;
    motor_state.actual_current_w = (adc_w - 2048) * 100.0 / 2048.0;
}

void update_rotor_position(void) {
    // Read Hall sensors and update rotor angle
    uint8_t hall_state = 0;
    hall_state |= (digitalRead(GPIO_HALL_A) << 0);
    hall_state |= (digitalRead(GPIO_HALL_B) << 1);
    hall_state |= (digitalRead(GPIO_HALL_C) << 2);
    
    // Store for FOC algorithm
    // Actual hall-to-angle mapping would go here
}

// Note: foc_loop() has been replaced with foc_execute() in motor_foc.cpp module

void safety_check(void) {
    // Monitor for faults and apply protective measures
    
    // Check DC link voltage
    uint16_t adc_vdc = analogRead(GPIO_ADC_VDC);
    motor_state.dc_voltage = adc_vdc * 400.0 / 4095.0;  // Assuming 400V nominal
    
    if (motor_state.dc_voltage < 300 || motor_state.dc_voltage > 480) {
        // Over/under voltage
        motor_state.error_code |= 0x01;
        digitalWrite(GPIO_PWM_EN, LOW);  // Disable gate driver
    }
    
    // Check currents
    float max_i = fmax(fmax(abs(motor_state.actual_current_u),
                            abs(motor_state.actual_current_v)),
                       abs(motor_state.actual_current_w));
    
    if (max_i > tuning.max_current) {
        motor_state.error_code |= 0x02;
        digitalWrite(GPIO_PWM_EN, LOW);
    }
    
    // Check temperatures
    uint16_t adc_temp = analogRead(GPIO_ADC_TEMP_MOTOR);
    motor_state.temperature_motor = (adc_temp / 4095.0) * 100.0;  // Simplified
    
    if (motor_state.temperature_motor > 100) {
        motor_state.error_code |= 0x04;
        digitalWrite(GPIO_PWM_EN, LOW);
    }
    
    // Check gate driver fault
    if (digitalRead(GPIO_PWM_FAULT) == LOW) {
        motor_state.error_code |= 0x08;
        digitalWrite(GPIO_PWM_EN, LOW);
    }
}

// ============ EEPROM FUNCTIONS ============

void eeprom_load_config(void) {
    Serial.println("Loading configuration from EEPROM...");
    
    // Read tuning parameters from EEPROM
    EEPROM.get(0, tuning);
    
    Serial.printf("Loaded: kp=%.3f ki=%.3f kd=%.3f max_i=%.1f\n",
                 tuning.kp, tuning.ki, tuning.kd, tuning.max_current);
}

void eeprom_save_config(void) {
    Serial.println("Saving configuration to EEPROM...");
    
    EEPROM.put(0, tuning);
    EEPROM.commit();
}

// Note: BLE setup is now in ble_interface.cpp module
// The old setup_ble() function has been replaced with ble_init()
// The old handle_ble_command() has been replaced with class callbacks

// ============ END OF FILE ============
