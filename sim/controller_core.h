#ifndef CONTROLLER_CORE_H
#define CONTROLLER_CORE_H

#include <cmath>
#include <algorithm>
#include <iostream>

/**
 * Controller Core — Lógica de controle + auto-learning
 * Extraído de motor_foc.cpp + motor_autolearn.cpp + ble_interface.cpp
 */

class PIController {
public:
    double Kp, Ki, Kd;
    double integral_error;
    double last_error;
    
    // Limites de saída (corrente em amperes)
    static constexpr double I_MAX = 50.0;   // 50A max
    static constexpr double I_MIN = 0.0;
    
    PIController(double kp = 1.0, double ki = 0.1, double kd = 0.05)
        : Kp(kp), Ki(ki), Kd(kd), integral_error(0.0), last_error(0.0) {}
    
    /**
     * PI velocity controller: error_rpm → I_cmd (corrente d'eixo q)
     * Anti-windup: integral saturado
     */
    double compute(double rpm_target, double rpm_actual, double dt = 1e-4) {
        double error = rpm_target - rpm_actual;
        
        // Termo P
        double p_term = Kp * error;
        
        // Termo I com anti-windup
        integral_error += error * dt;
        const double INTEGRAL_MAX = 20.0;  // Limite de windup
        integral_error = std::max(-INTEGRAL_MAX, std::min(INTEGRAL_MAX, integral_error));
        double i_term = Ki * integral_error;
        
        // Termo D
        double d_term = Kd * (error - last_error) / dt;
        last_error = error;
        
        // Saída total
        double i_cmd = p_term + i_term + d_term;
        
        // Clamp a limites de corrente
        i_cmd = std::max(I_MIN, std::min(I_MAX, i_cmd));
        
        return i_cmd;
    }
    
    void reset() {
        integral_error = 0.0;
        last_error = 0.0;
    }
};

class ParamStore {
public:
    double Kp_stored, Ki_stored, Kd_stored;
    
    // Limites de parâmetros (baseado em Ziegler-Nichols)
    static constexpr double KP_MIN = 0.01, KP_MAX = 5.0;
    static constexpr double KI_MIN = 0.001, KI_MAX = 1.0;
    static constexpr double KD_MIN = 0.001, KD_MAX = 0.5;
    
    ParamStore(double kp = 1.0, double ki = 0.1, double kd = 0.05)
        : Kp_stored(kp), Ki_stored(ki), Kd_stored(kd) {}
    
    /**
     * Setter com clamp automático (software verificable)
     */
    bool setKp(double value) {
        Kp_stored = std::max(KP_MIN, std::min(KP_MAX, value));
        return true;
    }
    
    bool setKi(double value) {
        Ki_stored = std::max(KI_MIN, std::min(KI_MAX, value));
        return true;
    }
    
    bool setKd(double value) {
        Kd_stored = std::max(KD_MIN, std::min(KD_MAX, value));
        return true;
    }
    
    double getKp() const { return Kp_stored; }
    double getKi() const { return Ki_stored; }
    double getKd() const { return Kd_stored; }
};

class RelayAutoTuner {
public:
    enum State { IDLE, RUNNING, DONE };
    
    State state;
    double setpoint;
    double relay_high, relay_low;  // ±amplitude
    int zero_crossings;
    double osc_period;
    double osc_amplitude;
    int max_crossings;
    
    // Resultados Ziegler-Nichols
    double Kp_result, Ki_result, Kd_result;
    double Ku;  // Ultimate gain
    double Tu;  // Ultimate period
    
    RelayAutoTuner(double setpoint_rpm = 3000.0)
        : state(IDLE), setpoint(setpoint_rpm),
          relay_high(20.0), relay_low(-20.0),
          zero_crossings(0), osc_period(0.0), osc_amplitude(0.0),
          max_crossings(6), Kp_result(0), Ki_result(0), Kd_result(0),
          Ku(0), Tu(0) {}
    
    void start() {
        state = RUNNING;
        zero_crossings = 0;
        osc_period = 0.0;
        osc_amplitude = 0.0;
    }
    
    /**
     * Relay perturbation method (Astrom-Hagglund)
     * Retorna corrente de comando: ±relay para oscilar ao redor do setpoint
     */
    double relayStep(double rpm_actual) {
        if (state != RUNNING) return 0.0;
        
        double error = setpoint - rpm_actual;
        
        if (error > 0) {
            osc_amplitude = std::max(osc_amplitude, std::abs(rpm_actual - setpoint));
            return relay_high;
        } else {
            osc_amplitude = std::max(osc_amplitude, std::abs(rpm_actual - setpoint));
            return relay_low;
        }
    }
    
    /**
     * Detecta cruzamento zero (simples, sem real timestamping)
     * Em produção seria mais sofisticado (edge detection)
     */
    void updateOscillation(double rpm_actual) {
        static double last_error = 0;
        double error = setpoint - rpm_actual;
        
        if ((last_error > 0 && error < 0) || (last_error < 0 && error > 0)) {
            zero_crossings++;
            if (zero_crossings >= max_crossings) {
                state = DONE;
                // Período de oscilação (simplificado)
                Tu = 2.0;  // ~2 segundos por ciclo (típico em motor 3000 RPM)
                
                // Ziegler-Nichols: Kc = 0.6 * Ku
                Ku = 2.0 * relay_high / (M_PI * osc_amplitude);
                Kp_result = 0.6 * Ku;
                Ki_result = 1.2 * Ku / Tu;
                Kd_result = 0.075 * Ku * Tu;
                
                // Clamp aos limites
                Kp_result = std::max(ParamStore::KP_MIN, std::min(ParamStore::KP_MAX, Kp_result));
                Ki_result = std::max(ParamStore::KI_MIN, std::min(ParamStore::KI_MAX, Ki_result));
                Kd_result = std::max(ParamStore::KD_MIN, std::min(ParamStore::KD_MAX, Kd_result));
            }
        }
        
        last_error = error;
    }
    
    bool isDone() const { return state == DONE; }
    
    void getResults(double &kp, double &ki, double &kd) const {
        kp = Kp_result;
        ki = Ki_result;
        kd = Kd_result;
    }
};

#endif
