#ifndef MOTOR_MODEL_H
#define MOTOR_MODEL_H

#include <cmath>
#include <iostream>

/**
 * Motor Model — Simulação de dinâmica PMSM
 * 
 * Parâmetros base (BYD Seagull equivalent):
 * - J = moment of inertia = 0.005 kg.m²
 * - B = damping coefficient = 0.01 N.m.s/rad
 * - Kt = torque constant = 0.28 N.m/A (motor típico 50A/400V)
 * - Load torque = 0 (sem carga) ou configurável
 */

class MotorModel {
public:
    // Estado
    double omega;        // rad/s (angular velocity)
    double torque_cmd;   // N.m (commanded motor torque from controller)
    
    // Parâmetros de motor (BYD Seagull equivalent)
    static constexpr double J  = 0.005;   // moment of inertia (kg.m²)
    static constexpr double B  = 0.01;    // damping coeff (N.m.s/rad)
    static constexpr double Kt = 0.28;    // torque constant (N.m/A)
    static constexpr double dt = 1e-4;    // timestep = 100 µs (10 kHz)
    
    double tau_load;  // load torque (N.m), default 0
    
    MotorModel() : omega(0.0), torque_cmd(0.0), tau_load(0.0) {}
    
    /**
     * Dinâmica mecânica Euler forward:
     * dω/dt = (τ_motor − B·ω − τ_load) / J
     * τ_motor = Kt · Iq (assumindo Iq = I_cmd para simplificar)
     */
    void step(double current_cmd) {
        torque_cmd = Kt * current_cmd;
        double domega_dt = (torque_cmd - B * omega - tau_load) / J;
        omega += domega_dt * dt;
        
        // Saturar omega a limites reais (~12000 RPM = 1257 rad/s)
        const double omega_max = 1257.0;  // 12000 RPM
        if (omega > omega_max) omega = omega_max;
        if (omega < 0) omega = 0;
    }
    
    double getRPM() const {
        return omega * 60.0 / (2.0 * M_PI);
    }
    
    void reset() {
        omega = 0.0;
        torque_cmd = 0.0;
    }
};

#endif
