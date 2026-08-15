/*
 * FOC (Field-Oriented Control) Implementation
 * Purpose: Efficient 3-phase motor control with Clarke/Park transformations
 * Algorithm: Simplified FOC with PI velocity loop + current limitation
 * Integration: SimpleFOC library for hardware-agnostic abstraction
 */

#include <Arduino.h>
#include <math.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "types.h"

// ============ CONFIGURATION ============

#define FOC_VOLTAGE_LIMIT 380.0         // Maximum voltage (V)
#define FOC_CURRENT_LIMIT 50.0          // Maximum current (A)
#define FOC_VELOCITY_LOOP_FREQ 10000    // 10 kHz control loop
#define FOC_PWM_FREQUENCY 20000         // PWM switching frequency (Hz)

// PI Controller parameters (default Ziegler-Nichols)
#define DEFAULT_KP 0.5
#define DEFAULT_KI 0.1
#define DEFAULT_KD 0.05

// ============ EXTERNAL REFERENCES ============

extern MotorState motor_state;

extern struct TuningParams {
    float kp;
    float ki;
    float kd;
    float max_current;
    float max_voltage;
    uint8_t control_mode;  // 0=FOC, 1=BLDC
    uint8_t sensor_mode;   // 0=Sensorless, 1=Hall
} tuning;

extern SemaphoreHandle_t state_mutex;

// ============ FOC STATE VARIABLES ============

typedef struct {
    // Current sensors (filtered)
    float i_u;      // Phase U current
    float i_v;      // Phase V current
    float i_w;      // Phase W current (computed: Iw = -Iu - Iv)
    
    // Clarke transformation (α-β frame)
    float i_alpha;
    float i_beta;
    
    // Park transformation (d-q rotating frame)
    float i_d;      // Direct axis current (torque component)
    float i_q;      // Quadrature axis current (flux component)
    
    // Voltage outputs (d-q frame)
    float v_d;      // Direct axis voltage
    float v_q;      // Quadrature axis voltage
    
    // Voltage inverse transforms (α-β frame)
    float v_alpha;
    float v_beta;
    
    // PWM duty cycles (0-1023 for 10-bit ESP32)
    uint16_t pwm_u;
    uint16_t pwm_v;
    uint16_t pwm_w;
    
    // Rotor angle (electrical degrees)
    float theta_e;      // Electrical angle (0-360°)
    float theta_d;      // Incremental angle
    
    // Rotor speed (electrical rad/s)
    float w_e;          // Electrical angular velocity
    
    // PI controller state
    float velocity_error_integral;
    float velocity_error_last;
    
} FOCState;

static FOCState foc;

// Lookup table for sin/cos (small optimization)
static const float SIN_LUT[91] = {
    0.0000, 0.0175, 0.0349, 0.0523, 0.0698, 0.0872, 0.1045, 0.1219, 0.1392, 0.1564,
    0.1736, 0.1908, 0.2079, 0.2250, 0.2419, 0.2588, 0.2756, 0.2924, 0.3090, 0.3256,
    0.3420, 0.3584, 0.3746, 0.3907, 0.4067, 0.4226, 0.4384, 0.4540, 0.4695, 0.4848,
    0.5000, 0.5150, 0.5299, 0.5446, 0.5592, 0.5736, 0.5878, 0.6018, 0.6157, 0.6293,
    0.6428, 0.6561, 0.6691, 0.6820, 0.6947, 0.7071, 0.7193, 0.7314, 0.7431, 0.7547,
    0.7660, 0.7771, 0.7880, 0.7986, 0.8090, 0.8192, 0.8290, 0.8387, 0.8480, 0.8572,
    0.8660, 0.8746, 0.8829, 0.8910, 0.8988, 0.9063, 0.9135, 0.9205, 0.9272, 0.9336,
    0.9397, 0.9455, 0.9511, 0.9563, 0.9613, 0.9659, 0.9703, 0.9744, 0.9781, 0.9816,
    0.9848, 0.9877, 0.9903, 0.9925, 0.9945, 0.9962, 0.9976, 0.9987, 0.9994, 0.9998, 1.0000
};

// Fast sin/cos using lookup table
static inline float foc_sin(float angle_deg) {
    // Normalize to 0-360
    while (angle_deg < 0) angle_deg += 360;
    while (angle_deg >= 360) angle_deg -= 360;
    
    // Use LUT for speed (good enough for control)
    uint16_t idx = (uint16_t)(angle_deg * 90.0 / 90.0);
    if (idx > 90) idx = 180 - idx;
    
    float sin_val = SIN_LUT[idx];
    if (angle_deg >= 180) sin_val = -sin_val;
    
    return sin_val;
}

static inline float foc_cos(float angle_deg) {
    return foc_sin(angle_deg + 90.0);
}

// ============ CLARKE TRANSFORMATION ============

static void foc_clarke_transform(void) {
    /*
     * Clarke Transformation: 3-phase (U,V,W) → 2-phase (α,β)
     * 
     * Matrix form:
     * [iα]   [ 1   -1/2   -1/2] [iu]
     * [iβ] = [ 0  √3/2   -√3/2] [iv]
     *                            [iw]
     * 
     * Iw = -(Iu + Iv)  [zero-sum constraint]
     */
    
    foc.i_w = -(foc.i_u + foc.i_v);
    
    foc.i_alpha = foc.i_u;
    foc.i_beta = (foc.i_u / 2.0 + foc.i_v) * 0.866;  // 0.866 ≈ √3/2
}

// ============ PARK TRANSFORMATION ============

static void foc_park_transform(void) {
    /*
     * Park Transformation: 2-phase (α,β) → rotating (d,q)
     * 
     * Rotates from stationary frame to rotor-synchronized rotating frame
     * 
     * [id]   [ cos(θe)  sin(θe)] [iα]
     * [iq] = [-sin(θe)  cos(θe)] [iβ]
     * 
     * Direct axis (d): Aligned with rotor flux
     * Quadrature axis (q): 90° ahead (torque-producing)
     */
    
    float cos_theta = foc_cos(foc.theta_e);
    float sin_theta = foc_sin(foc.theta_e);
    
    foc.i_d = foc.i_alpha * cos_theta + foc.i_beta * sin_theta;
    foc.i_q = -foc.i_alpha * sin_theta + foc.i_beta * cos_theta;
}

// ============ INVERSE PARK TRANSFORMATION ============

static void foc_inverse_park_transform(void) {
    /*
     * Inverse Park Transformation: (d,q) → (α,β)
     * Converts calculated voltage commands back to stationary frame
     * 
     * [vα]   [ cos(θe) -sin(θe)] [vd]
     * [vβ] = [ sin(θe)  cos(θe)] [vq]
     */
    
    float cos_theta = foc_cos(foc.theta_e);
    float sin_theta = foc_sin(foc.theta_e);
    
    foc.v_alpha = foc.v_d * cos_theta - foc.v_q * sin_theta;
    foc.v_beta = foc.v_d * sin_theta + foc.v_q * cos_theta;
}

// ============ INVERSE CLARKE TRANSFORMATION ============

static void foc_inverse_clarke_transform(void) {
    /*
     * Inverse Clarke Transformation: (α,β) → (U,V,W)
     * 
     * [vu]   [ 1      0   ] [vα]
     * [vv] = [-1/2  √3/2] [vβ]
     * [vw]   [-1/2 -√3/2]
     * 
     * With zero-sum: Vw = -(Vu + Vv)
     */
    
    float v_u = foc.v_alpha;
    float v_v = (-foc.v_alpha / 2.0) + (foc.v_beta * 0.866);
    float v_w = -v_u - v_v;
    
    // Apply voltage limits
    float v_max = fmax(fmax(fabs(v_u), fabs(v_v)), fabs(v_w));
    if (v_max > FOC_VOLTAGE_LIMIT) {
        float scale = FOC_VOLTAGE_LIMIT / v_max;
        v_u *= scale;
        v_v *= scale;
        v_w *= scale;
    }
    
    // Scale to PWM duty (assuming 400V nominal DC link)
    uint16_t pwm_scale = (1 << 10) - 1;  // 10-bit: 1023
    foc.pwm_u = (uint16_t)((v_u / motor_state.dc_voltage) * pwm_scale / 2.0 + pwm_scale / 2.0);
    foc.pwm_v = (uint16_t)((v_v / motor_state.dc_voltage) * pwm_scale / 2.0 + pwm_scale / 2.0);
    foc.pwm_w = (uint16_t)((v_w / motor_state.dc_voltage) * pwm_scale / 2.0 + pwm_scale / 2.0);
    
    // Clamp to valid PWM range
    foc.pwm_u = fmin(fmax(foc.pwm_u, 50), 973);
    foc.pwm_v = fmin(fmax(foc.pwm_v, 50), 973);
    foc.pwm_w = fmin(fmax(foc.pwm_w, 50), 973);
}

// ============ ROTOR POSITION & SPEED ESTIMATION ============

static void foc_update_rotor_position(void) {
    /*
     * Update rotor electrical angle (θe) based on Hall sensors or sensorless observer
     * 
     * For PMSM with Hall sensors:
     *   θe = hall_angle + electrical_offset
     *   ωe = dθe/dt (from previous angle)
     * 
     * For sensorless operation (future):
     *   Use back-EMF observer or position PLL
     */
    
    // Simplified: Assume motor velocity proportional to target command
    // In real implementation, use Hall sensors or sensorless observer
    
    float rpm_to_elec_rad_s = (motor_state.actual_rpm / 60.0) * (2.0 * 3.14159) * 4.0;  // 4 poles assumed
    float theta_increment = (rpm_to_elec_rad_s * 180.0 / 3.14159) / 10000.0;  // Convert to degrees per 100µs
    
    foc.theta_e += theta_increment;
    while (foc.theta_e >= 360) foc.theta_e -= 360;
    while (foc.theta_e < 0) foc.theta_e += 360;
}

// ============ PI VELOCITY CONTROLLER ============

static float foc_pi_velocity_controller(void) {
    /*
     * Proportional-Integral controller for velocity loop
     * 
     * Input: RPM error (target - actual)
     * Output: Torque command (current setpoint)
     * 
     * u(t) = Kp * e(t) + Ki * ∫e(t)dt
     * 
     * In discrete form:
     * u[n] = Kp * e[n] + Ki * Ts * Σe[n]
     */
    
    if (motor_state.target_rpm == 0) {
        foc.velocity_error_integral = 0;
        return 0;
    }
    
    float velocity_error = motor_state.target_rpm - motor_state.actual_rpm;
    
    // Integral accumulation (anti-windup: limit to max current)
    foc.velocity_error_integral += velocity_error;
    foc.velocity_error_integral = fmax(-50, fmin(50, foc.velocity_error_integral));
    
    // PI output
    float torque_command = tuning.kp * velocity_error + tuning.ki * foc.velocity_error_integral;
    torque_command = fmax(-FOC_CURRENT_LIMIT, fmin(FOC_CURRENT_LIMIT, torque_command));
    
    // ===== Regenerative braking =====
    // Quando o freio motor está ATIVO e o motor está desacelerando
    // (torque negativo: pedal solto ou freio acionado), a energia cinética
    // retorna ao barramento DC => sobre-elevação controlada de tensão e
    // contabilização da energia regenerada (carrega a bateria).
    motor_state.regen_active = false;
    motor_state.regen_power_w = 0;
    
    if (motor_state.motor_brake && torque_command < 0 && motor_state.actual_rpm > 50) {
        // Regenerative braking power (rotor kinetic energy being removed)
        float regen_power = -torque_command * FOC_VOLTAGE_LIMIT * 0.85f;  // P ≈ I*V
        motor_state.regen_power_w = regen_power;
        motor_state.regen_active = true;
        
        // DC link voltage rises while regenerating (energy goes back to battery)
        float v_rise = regen_power * 0.001f;  // small per-loop rise
        motor_state.dc_voltage = fmin(motor_state.dc_voltage + v_rise, 450.0f);
        if (motor_state.dc_voltage > motor_state.dc_voltage_peak) {
            motor_state.dc_voltage_peak = motor_state.dc_voltage;
        }
        
        // Accumulate regen energy (Wh): loop runs at 10kHz => dt = 100µs
        motor_state.regen_energy_wh += regen_power * 0.0001f / 3600.0f;
    }
    
    return torque_command;
}

// ============ D-Q CURRENT CONTROLLERS ============

static void foc_current_controllers(void) {
    /*
     * PI controllers for d-axis and q-axis currents
     * 
     * For PMSM:
     *   - Id should be ~0 (no flux change)
     *   - Iq produces torque: τ = Kt * Iq
     * 
     * Simple proportional control for now:
     *   Vd = Kp_d * (Id_ref - Id)
     *   Vq = Kp_q * (Iq_ref - Iq)
     */
    
    // Reference currents
    float i_d_ref = 0;                              // Keep flux constant
    float i_q_ref = foc_pi_velocity_controller();   // From velocity loop
    
    // Proportional gains (simplified)
    float Kp_d = 1.0;
    float Kp_q = 1.0;
    
    // Calculate voltage errors
    float i_d_error = i_d_ref - foc.i_d;
    float i_q_error = i_q_ref - foc.i_q;
    
    // PI with decoupling terms (neglect for v1.0)
    foc.v_d = Kp_d * i_d_error;
    foc.v_q = Kp_q * i_q_error;
    
    // Limit voltages
    float v_max = sqrt(foc.v_d * foc.v_d + foc.v_q * foc.v_q);
    if (v_max > FOC_VOLTAGE_LIMIT) {
        float scale = FOC_VOLTAGE_LIMIT / v_max;
        foc.v_d *= scale;
        foc.v_q *= scale;
    }
}

// ============ MAIN FOC ALGORITHM ============

void foc_execute(void) {
    /*
     * Complete FOC execution sequence:
     * 1. Read phase currents (done in main loop)
     * 2. Clarke transformation (3-phase → 2-phase)
     * 3. Park transformation (stationary → rotating frame)
     * 4. PI velocity controller
     * 5. PI current controllers (d-q)
     * 6. Inverse Park transformation
     * 7. Inverse Clarke transformation
     * 8. Write PWM outputs
     */
    
    // Step 1: Read currents (already done in main sensor read)
    foc.i_u = motor_state.actual_current_u;
    foc.i_v = motor_state.actual_current_v;
    
    // Step 2: Clarke transformation (α-β stationary frame)
    foc_clarke_transform();
    
    // Step 3: Update rotor position
    foc_update_rotor_position();
    
    // Step 4: Park transformation (d-q rotating frame)
    foc_park_transform();
    
    // Step 5: Current controllers and velocity loop
    foc_current_controllers();
    
    // Step 6: Inverse Park transformation (d-q → α-β)
    foc_inverse_park_transform();
    
    // Step 7: Inverse Clarke transformation (α-β → U,V,W)
    foc_inverse_clarke_transform();
    
    // Step 8: Write PWM outputs (done in main loop)
}

// ============ PUBLIC FUNCTIONS ============

// Export PWM values for main motor control loop
uint16_t foc_pwm_u = 512;
uint16_t foc_pwm_v = 512;
uint16_t foc_pwm_w = 512;

void foc_init(void) {
    Serial.println("[FOC] Initializing...");
    
    // Initialize state
    memset(&foc, 0, sizeof(FOCState));
    foc.theta_e = 0;
    foc.velocity_error_integral = 0;
    
    Serial.println("[FOC] Ready");
}

void foc_set_rpm(float rpm) {
    motor_state.target_rpm = rpm;
}

float foc_get_actual_rpm(void) {
    // Simplified: return target (should estimate from back-EMF or Hall)
    // TODO: Implement proper speed observer
    return motor_state.actual_rpm;
}

void foc_update_tuning(float kp, float ki, float kd) {
    xSemaphoreTake(state_mutex, portMAX_DELAY);
    tuning.kp = kp;
    tuning.ki = ki;
    tuning.kd = kd;
    xSemaphoreGive(state_mutex);
}

// Execute FOC and update PWM outputs
void foc_execute_with_pwm(void) {
    foc_execute();
    foc_pwm_u = foc.pwm_u;
    foc_pwm_v = foc.pwm_v;
    foc_pwm_w = foc.pwm_w;
}

// ============ END OF FILE ============
