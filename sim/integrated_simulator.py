#!/usr/bin/env python3
"""
Integrated End-to-End Simulator: Sensors → FOC → Motor
Simulates complete motor control loop with injected parameters
"""

import json
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple

@dataclass
class SimConfig:
    """Configuration for integrated simulation"""
    rpm_target: float = 3000.0
    duration_s: float = 2.0
    kp: float = 0.3
    ki: float = 0.03
    kd: float = 0.01
    pwm_freq_hz: int = 20000
    control_freq_hz: int = 10000
    load_torque: float = 0.0  # N.m, 0 = no load

@dataclass
class SimState:
    """Simulation state at each timestep"""
    time_s: float
    rpm: float
    rpm_target: float
    current_u: float
    current_v: float
    current_w: float
    voltage_u: float
    voltage_v: float
    voltage_w: float
    pwm_u: float
    pwm_v: float
    pwm_w: float
    torque_cmd: float
    temp_motor: float
    error_integral: float
    
class MotorSimulator:
    """Simulates PMSM motor with realistic dynamics"""
    def __init__(self):
        # Motor parameters (BYD Seagull equivalent)
        self.J = 0.005      # moment of inertia (kg·m²)
        self.B = 0.01       # damping coefficient (N·m·s/rad)
        self.Kt = 0.28      # torque constant (N·m/A)
        self.L = 1e-3       # phase inductance (H)
        self.R = 0.1        # phase resistance (Ω)
        self.dt = 1e-4      # timestep = 100 µs (10 kHz)
        
        # State
        self.omega = 0.0    # rad/s
        self.i_alpha = 0.0  # α-axis current (A)
        self.i_beta = 0.0   # β-axis current (A)
        self.theta = 0.0    # rotor angle (rad)
    
    def step(self, v_alpha: float, v_beta: float, tau_load: float = 0.0):
        """Simulate motor dynamics one timestep (Euler method)"""
        # Current dynamics (α-β frame, simplified)
        di_alpha_dt = (v_alpha - self.R * self.i_alpha - 0) / self.L
        di_beta_dt = (v_beta - self.R * self.i_beta - 0) / self.L
        
        self.i_alpha += di_alpha_dt * self.dt
        self.i_beta += di_beta_dt * self.dt
        
        # Torque from current (q-component in FOC)
        i_q = math.sqrt(self.i_alpha**2 + self.i_beta**2)
        tau_motor = self.Kt * i_q
        
        # Mechanical dynamics
        domega_dt = (tau_motor - self.B * self.omega - tau_load) / self.J
        self.omega += domega_dt * self.dt
        
        # Clamp omega to realistic limits
        self.omega = max(0, min(1257, self.omega))  # 0-12000 RPM
        
        # Angle tracking (for commutation)
        self.theta += self.omega * self.dt
        self.theta = self.theta % (2 * math.pi)
    
    def get_rpm(self) -> float:
        """Current motor speed in RPM"""
        return self.omega * 60 / (2 * math.pi)

class FOCController:
    """Field-Oriented Control with PI velocity loop"""
    def __init__(self, kp: float = 0.3, ki: float = 0.03, kd: float = 0.01):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_integral = 0.0
        self.error_last = 0.0
        self.dt = 1e-4
    
    def compute(self, rpm_target: float, rpm_actual: float) -> Tuple[float, float]:
        """
        PI velocity controller: RPM error → voltage commands
        Returns (v_alpha, v_beta) for motor
        """
        error = rpm_target - rpm_actual
        
        # PI terms
        p_term = self.kp * error
        self.error_integral = max(-20, min(20, self.error_integral + error * self.dt))
        i_term = self.ki * self.error_integral
        d_term = self.kd * (error - self.error_last) / self.dt
        self.error_last = error
        
        # Voltage command (simplified: direct voltage from PI)
        v_cmd = p_term + i_term + d_term
        
        # Clamp to DC link (400V)
        v_cmd = max(-380, min(380, v_cmd))
        
        # Generate 3-phase voltages (simplified)
        v_alpha = v_cmd
        v_beta = v_cmd * 0.5  # Simplified for demo
        
        return v_alpha, v_beta

class PWMInverter:
    """Simulates 3-phase PWM inverter output"""
    def __init__(self, dc_link: float = 400.0, pwm_freq: int = 20000):
        self.dc_link = dc_link
        self.pwm_freq = pwm_freq
        self.period = 1 / pwm_freq
    
    def generate_3phase(self, v_alpha: float, v_beta: float, time: float) -> Tuple[float, float, float]:
        """Generate 3-phase voltages from α-β commands"""
        # Clarke inverse transform
        v_u = v_alpha
        v_v = -v_alpha/2 + math.sqrt(3)/2 * v_beta
        v_w = -v_alpha/2 - math.sqrt(3)/2 * v_beta
        
        # Clamp to DC link
        v_max = self.dc_link / 2
        v_u = max(-v_max, min(v_max, v_u))
        v_v = max(-v_max, min(v_max, v_v))
        v_w = max(-v_max, min(v_max, v_w))
        
        return v_u, v_v, v_w

class IntegratedSimulator:
    """End-to-end simulation: Motor + FOC + PWM + Inverter"""
    def __init__(self, config: SimConfig):
        self.config = config
        self.motor = MotorSimulator()
        self.controller = FOCController(config.kp, config.ki, config.kd)
        self.inverter = PWMInverter(400.0, config.pwm_freq_hz)
        
        self.dt = 1 / config.control_freq_hz
        self.states: List[SimState] = []
        self.time = 0.0
    
    def run(self) -> List[dict]:
        """Run simulation and return state history"""
        num_steps = int(self.config.duration_s / self.dt)
        
        for step in range(num_steps):
            # 1. Read feedback (motor RPM)
            rpm_actual = self.motor.get_rpm()
            
            # 2. FOC control law
            v_alpha, v_beta = self.controller.compute(self.config.rpm_target, rpm_actual)
            
            # 3. PWM inverter (3-phase generation)
            v_u, v_v, v_w = self.inverter.generate_3phase(v_alpha, v_beta, self.time)
            
            # 4. Motor dynamics (simplified: use α-β voltages)
            self.motor.step(v_alpha, v_beta, self.config.load_torque)
            
            # 5. Simulate 3-phase currents (120° phase shift)
            current_mag = math.sqrt(self.motor.i_alpha**2 + self.motor.i_beta**2)
            theta_elec = self.motor.theta % (2 * math.pi)
            current_u = current_mag * math.cos(theta_elec)
            current_v = current_mag * math.cos(theta_elec - 2*math.pi/3)
            current_w = current_mag * math.cos(theta_elec - 4*math.pi/3)
            
            # 6. Temperature estimation (simplified)
            i_sq_avg = (current_u**2 + current_v**2 + current_w**2) / 3
            power_loss = i_sq_avg * 0.1  # Resistance losses
            temp = 25 + power_loss * 0.1  # Very simplified
            
            # 7. Record state
            state = SimState(
                time_s=self.time,
                rpm=rpm_actual,
                rpm_target=self.config.rpm_target,
                current_u=current_u,
                current_v=current_v,
                current_w=current_w,
                voltage_u=v_u,
                voltage_v=v_v,
                voltage_w=v_w,
                pwm_u=v_u / 200,  # Normalized PWM (0-1)
                pwm_v=v_v / 200,
                pwm_w=v_w / 200,
                torque_cmd=v_alpha,
                temp_motor=temp,
                error_integral=self.controller.error_integral
            )
            self.states.append(state)
            self.time += self.dt
        
        return [asdict(s) for s in self.states]
    
    def get_summary(self) -> dict:
        """Compute simulation metrics"""
        if not self.states:
            return {}
        
        rpms = [s.rpm for s in self.states]
        currents = [math.sqrt(s.current_u**2 + s.current_v**2 + s.current_w**2) for s in self.states]
        
        # Skip first 500ms (transient)
        skip_samples = int(0.5 / self.dt)
        steady_rpms = rpms[skip_samples:]
        steady_currents = currents[skip_samples:]
        
        return {
            'final_rpm': rpms[-1],
            'target_rpm': self.config.rpm_target,
            'error_percent': abs(rpms[-1] - self.config.rpm_target) / self.config.rpm_target * 100,
            'steady_rpm_avg': sum(steady_rpms) / len(steady_rpms) if steady_rpms else 0,
            'steady_rpm_std': (sum((x - (sum(steady_rpms)/len(steady_rpms)))**2 for x in steady_rpms) / len(steady_rpms))**0.5 if steady_rpms else 0,
            'peak_current': max(currents),
            'mean_current': sum(currents) / len(currents) if currents else 0,
            'peak_temp': max(s.temp_motor for s in self.states),
            'converged': abs(rpms[-1] - self.config.rpm_target) / self.config.rpm_target < 0.05,
        }

def run_simulation(config: SimConfig) -> Tuple[List[dict], dict]:
    """Main entry point for simulation"""
    sim = IntegratedSimulator(config)
    states = sim.run()
    summary = sim.get_summary()
    return states, summary

if __name__ == '__main__':
    import sys
    
    # Example: run with default config
    if len(sys.argv) > 1:
        config_json = sys.argv[1]
        config_dict = json.loads(config_json)
        config = SimConfig(**config_dict)
    else:
        config = SimConfig()
    
    print(f"Running simulation: RPM target={config.rpm_target}, Kp={config.kp}, duration={config.duration_s}s")
    states, summary = run_simulation(config)
    
    # Output results
    result = {
        'config': asdict(config),
        'summary': summary,
        'states': states
    }
    print(json.dumps(result, indent=2))
