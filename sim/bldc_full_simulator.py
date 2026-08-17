#!/usr/bin/env python3
"""
Professional BLDC Motor Controller Simulator
Complete end-to-end simulation with:
- Throttle pedal (0-100%)
- FOC + PI controller
- Auto-learning (Astrom-Hagglund + Ziegler-Nichols)
- Temperature monitoring
- Safety protections
- 3-phase current balancing
"""

import json
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
from enum import Enum
from motor_models import BrakeModel, BatteryWithSpec, BatterySpec

class ControlMode(Enum):
    """Controller operation modes"""
    MANUAL = 0      # Manual Kp/Ki/Kd
    AUTOLEARN = 1   # Auto-learning active

class MotorState(Enum):
    """Motor operational states"""
    IDLE = 0
    RUNNING = 1
    FAULT = 2
    THERMAL_LIMIT = 3

@dataclass
class SimConfig:
    """Full simulation configuration"""
    # Motor targets
    throttle_percent: float = 50.0  # 0-100% accelerator pedal
    rpm_target: float = 3000.0
    duration_s: float = 3.0
    
    # Control parameters (injectable)
    kp: float = 0.3
    ki: float = 0.03
    kd: float = 0.01
    
    # Auto-learning
    autolearn_enabled: bool = False
    autolearn_duration_s: float = 2.0
    
    # Operating conditions
    load_torque: float = 0.0       # N.m (0 = no load)
    ambient_temp_c: float = 25.0   # °C
    motor_brake: bool = True       # Motor brake / regenerative braking (ON by default)
    
    # Safety parameters
    max_current_a: float = 50.0
    max_temp_c: float = 80.0
    thermal_time_constant_s: float = 2.0
    
    # Motor specification (for adaptive control)
    motor_inertia_kg_m2: float = 0.005  # Used to scale PID gains for any motor size

    # Battery model (for regenerative braking / SOC)
    battery_capacity_ah: float = 5.0
    battery_nominal_v: float = 48.0
    battery_internal_resistance: float = 0.05
    battery_efficiency: float = 95.0
    battery_soc_init: float = 0.85

    # Industrial Protections & Dead-Time
    brake_chopper_enabled: bool = True
    brake_chopper_v_on: float = 54.0       # Ativação do Chopper de Freio (V)
    brake_chopper_v_off: float = 51.0      # Desativação do Chopper de Freio (Histerese 3V)
    dead_time_ns: float = 500.0            # 500ns Dead-Time por hardware
    galvanic_isolation_active: bool = True # Optoisoladores Hall + CAN ISO1050

    # Optional throttle profile over time [(time_s, throttle_percent), ...].
    # When set, throttle_percent is interpolated across time (models user
    # releasing the pedal -> deceleration -> regenerative braking).
    throttle_profile: Optional[List[Tuple[float, float]]] = None

@dataclass
class SimState:
    """Complete simulation state at each timestep"""
    time_s: float
    mode: str  # 'manual' or 'autolearn'
    throttle: float
    rpm_target: float
    rpm_actual: float
    current_u: float
    current_v: float
    current_w: float
    current_rms: float
    voltage_u: float
    voltage_v: float
    voltage_w: float
    torque_cmd: float
    torque_actual: float
    temp_motor_c: float
    temp_driver_c: float
    motor_state: str  # 'idle', 'running', 'fault', 'thermal_limit'
    kp: float
    ki: float
    kd: float
    error_integral: float
    fault_code: int
    soc: float = 0.85
    battery_voltage: float = 48.0
    regen_power: float = 0.0
    motor_brake: bool = True
    brake_chopper_active: bool = False
    dead_time_loss_v: float = 0.0

class BLDCMotor:
    """Full BLDC motor model with realistic braking/friction"""
    def __init__(self):
        # Motor parameters (BYD Seagull equivalent, 50A continuous, 115kW peak)
        self.J = 0.005          # moment of inertia (kg·m²)
        self.B = 0.01           # damping coefficient (N·m·s/rad)
        self.Kt = 0.28          # torque constant (N·m/A)
        self.Ke = 0.28          # back-EMF constant (V·s/rad)
        self.L = 1e-3           # phase inductance (H)
        self.R = 0.1            # phase resistance (Ω)
        self.tau_thermal = 2.0  # thermal time constant (s)
        
        # State
        self.omega = 0.0        # rad/s
        self.theta = 0.0        # rotor angle (rad)
        self.i_alpha = 0.0      # α-axis current (A)
        self.i_beta = 0.0       # β-axis current (A)
        self.temp = 25.0        # motor temperature (°C)
        
        # Brake model (realistic friction for vehicle)
        self.brake_model = BrakeModel(k_friction=0.002, k_aerodynamic=0.00001)
        self.tau_brake = 0.0    # Current braking torque
        
        self.dt = 1e-4
    
    def step(self, v_alpha: float, v_beta: float, tau_load: float, ambient_temp: float):
        """Simulate one control cycle"""
        # Current dynamics (α-β frame)
        di_alpha_dt = (v_alpha - self.R * self.i_alpha) / self.L
        di_beta_dt = (v_beta - self.R * self.i_beta) / self.L
        
        self.i_alpha = max(-60, min(60, self.i_alpha + di_alpha_dt * self.dt))
        self.i_beta = max(-60, min(60, self.i_beta + di_beta_dt * self.dt))
        
        # Motor torque (FOC simplified)
        i_mag = math.sqrt(self.i_alpha**2 + self.i_beta**2)
        tau_motor = self.Kt * i_mag
        
        # Braking torque from friction (realistic vehicle model)
        rpm_actual = self.omega * 60 / (2 * math.pi)
        self.tau_brake = self.brake_model.compute_braking_torque(rpm_actual)
        
        # Mechanical dynamics: J*dω/dt = τ_motor - B*ω - τ_brake - τ_load
        domega_dt = (tau_motor - self.B * self.omega - self.tau_brake - tau_load) / self.J
        self.omega = max(0, min(1257, self.omega + domega_dt * self.dt))  # 0-12000 RPM
        
        # Angle tracking
        self.theta += self.omega * self.dt
        self.theta = self.theta % (2 * math.pi)
        
        # Thermal dynamics (simplified)
        power_loss = i_mag**2 * self.R * 3 / 2  # I²R losses (3-phase)
        dtemp_dt = (power_loss * 0.1 - (self.temp - ambient_temp) * 0.5) / self.tau_thermal
        self.temp = max(ambient_temp, self.temp + dtemp_dt * self.dt)
    
    def get_rpm(self) -> float:
        return self.omega * 60 / (2 * math.pi)
    
    def get_3phase_currents(self) -> Tuple[float, float, float]:
        """Generate 3-phase currents (120° phase shift)"""
        i_mag = math.sqrt(self.i_alpha**2 + self.i_beta**2)
        i_u = i_mag * math.cos(self.theta)
        i_v = i_mag * math.cos(self.theta - 2*math.pi/3)
        i_w = i_mag * math.cos(self.theta - 4*math.pi/3)
        return i_u, i_v, i_w

class AdaptiveController:
    """Adaptive FOC with motor-dependent gain scaling"""
    def __init__(self, motor_inertia_j: float = 0.005, dt: float = 1e-4):
        """
        Adaptive controller that normalizes gains for ANY motor size.
        motor_inertia_j: Motor moment of inertia (kg·m²) - used to normalize bandwidth
        """
        # Motor-dependent scaling (τ = J/B, larger J needs smaller Kp to avoid oscillations)
        self.J = motor_inertia_j
        self.tau_motor = motor_inertia_j / 0.01  # Estimated time constant
        
        # Base gains (normalized for medium motor J=0.005)
        # These scale adaptively based on actual J
        self.kp_base = 0.3
        self.ki_base = 0.03
        self.kd_base = 0.01
        
        # Adaptive scaling factor: smaller motors (J<0.005) get higher gains
        # larger motors (J>0.005) get lower gains to prevent instability
        scale = 0.005 / max(self.J, 0.001)  # Ratio to medium motor
        self.kp = self.kp_base * scale
        self.ki = self.ki_base * scale  
        self.kd = self.kd_base * scale
        
        self.error_integral = 0.0
        self.error_last = 0.0
        self.dt = dt

class FOCController(AdaptiveController):
    """Field-Oriented Control with PI velocity loop (inherits adaptive scaling)"""
    def __init__(self, kp: float = 0.3, ki: float = 0.03, kd: float = 0.01, motor_inertia_j: float = 0.005):
        super().__init__(motor_inertia_j=motor_inertia_j, dt=1e-4)
        # Allow manual override
        if kp > 0:
            self.kp_base = kp
            self.kp = kp * (0.005 / max(self.J, 0.001))
        if ki > 0:
            self.ki_base = ki
            self.ki = ki * (0.005 / max(self.J, 0.001))
        if kd > 0:
            self.kd_base = kd
            self.kd = kd * (0.005 / max(self.J, 0.001))
    
    def compute(self, rpm_target: float, rpm_actual: float) -> Tuple[float, float]:
        """PI velocity controller → voltage commands"""
        error = rpm_target - rpm_actual
        
        # PI terms
        p_term = self.kp * error
        self.error_integral = max(-20, min(20, self.error_integral + error * self.dt))
        i_term = self.ki * self.error_integral
        d_term = self.kd * (error - self.error_last) / self.dt
        self.error_last = error
        
        # Voltage command (0-380V)
        v_cmd = p_term + i_term + d_term
        v_cmd = max(-380, min(380, v_cmd))
        
        # 3-phase generation
        v_alpha = v_cmd
        v_beta = v_cmd * 0.5
        
        return v_alpha, v_beta
    
    def update_gains(self, kp: float, ki: float, kd: float):
        """Dynamically update controller gains"""
        self.kp = max(0.01, min(5.0, kp))
        self.ki = max(0.001, min(1.0, ki))
        self.kd = max(0.001, min(0.5, kd))
        self.error_integral = 0.0  # Reset integrator on gain change

class AutoLearner:
    """Astrom-Hagglund relay auto-tuning v3: Multi-phase progressive with rate-limit protection"""
    def __init__(self, rpm_setpoint: float = 3000.0, autolearn_duration_s: float = 2.0, dt: float = 1e-4):
        self.state = 'idle'  # idle, phase1, phase2, phase3, converged, timeout
        self.setpoint = rpm_setpoint
        self.dt = dt
        self.autolearn_duration_s = autolearn_duration_s
        
        # Phase timing
        self.phase1_end = 0.5   # Low relay: 0-0.5s
        self.phase2_end = 1.5   # Oscillation: 0.5-1.5s
        self.phase3_end = autolearn_duration_s  # Refinement: 1.5-2.0s
        
        # Relay configuration (adaptive by phase)
        self.relay_high_phase1 = 0.5   # Low voltage for soft start
        self.relay_high_phase2 = 2.0   # Normal oscillation
        self.relay_high_phase3 = 2.0   # Refinement
        self.relay_high = self.relay_high_phase1
        self.relay_low = -self.relay_high
        self.relay_cmd = 0.0
        
        # Hysteresis (adaptive by phase)
        self.hysteresis_base = rpm_setpoint * 0.15  # ±15% of setpoint
        self.hysteresis_threshold = self.hysteresis_base
        
        # Zero-crossing detection
        self.error_prev = 0.0
        self.zero_crossings = 0
        self.zero_crossing_times = []
        self.stable_oscillations = 0  # Count of stable periods
        
        # Peak tracking
        self.peak_rpm = 0
        self.min_rpm = float('inf')
        self.peaks = []
        
        # Rate-limit protection (max 3000 RPM/s = 314 rad/s acceleration)
        self.rpm_prev = 0.0
        self.max_rpm_rate = 3000.0 / 60.0  # Convert to RPM/s
        self.rate_limit_violated = False
        
        # Tuning results
        self.kp_result = 0.3
        self.ki_result = 0.03
        self.kd_result = 0.01
        
        # Convergence detection
        self.samples = 0
        self.total_samples = int(autolearn_duration_s / dt)
        self.tcr = 0.0
        self.acr = 0.0
        self.phase = 1
        self.progress_percent = 0.0
        
    def start(self):
        """Start relay tuning"""
        self.state = 'phase1'
        self.phase = 1
        self.error_prev = 0.0
        self.zero_crossings = 0
        self.zero_crossing_times = []
        self.peak_rpm = 0
        self.min_rpm = float('inf')
        self.peaks = []
        self.samples = 0
        self.stable_oscillations = 0
        self.progress_percent = 0.0
    
    def step(self, rpm_actual: float, time: float = 0.0) -> Tuple[float, str]:
        """
        Multi-phase relay auto-tuning with rate-limit protection.
        Phase 1 (0-0.5s): Soft start with low relay (detect inertia)
        Phase 2 (0.5-1.5s): Normal relay (create oscillations)
        Phase 3 (1.5-2.0s): Refinement (tuning convergence)
        
        Returns: (relay_command, state_string)
        """
        if self.state == 'idle':
            return 0.0, self.state
        
        error = self.setpoint - rpm_actual
        self.samples += 1
        self.progress_percent = (self.samples / self.total_samples) * 100.0
        
        # ===== PHASE PROGRESSION =====
        elapsed_time = self.samples * self.dt
        if elapsed_time < self.phase1_end:
            self.phase = 1
            self.relay_high = self.relay_high_phase1
            self.hysteresis_threshold = self.hysteresis_base * 1.5  # Wider band for soft start
        elif elapsed_time < self.phase2_end:
            self.phase = 2
            self.relay_high = self.relay_high_phase2
            self.hysteresis_threshold = self.hysteresis_base  # Normal band
        else:
            self.phase = 3
            self.relay_high = self.relay_high_phase3
            self.hysteresis_threshold = self.hysteresis_base * 0.75  # Tighter for refinement
        
        self.relay_low = -self.relay_high
        
        # ===== RATE-LIMIT PROTECTION =====
        # Prevent motor from accelerating too fast (protects mechanical system)
        rpm_rate = (rpm_actual - self.rpm_prev) / self.dt
        if abs(rpm_rate) > self.max_rpm_rate and self.relay_cmd > 0:
            # Motor accelerating too fast: force negative relay to brake
            self.relay_cmd = self.relay_low
            self.rate_limit_violated = True
        else:
            self.rate_limit_violated = False
        
        self.rpm_prev = rpm_actual
        
        # ===== HYSTERESIS RELAY CONTROL =====
        # If error > +threshold: command positive relay
        # If error < -threshold: command negative relay
        # Otherwise: maintain hysteresis (keep previous command)
        if error > self.hysteresis_threshold:
            self.relay_cmd = self.relay_high
        elif error < -self.hysteresis_threshold:
            self.relay_cmd = self.relay_low
        # else: keep relay_cmd unchanged (hysteresis)
        
        # ===== ZERO-CROSSING DETECTION =====
        # Detect oscillations around setpoint
        if self.error_prev * error < 0:  # Sign change in error
            self.zero_crossings += 1
            self.zero_crossing_times.append(time)
        
        # ===== PEAK TRACKING =====
        self.peaks.append(rpm_actual)
        self.peak_rpm = max(self.peak_rpm, rpm_actual)
        self.min_rpm = min(self.min_rpm, rpm_actual)
        
        # ===== TUNING CALCULATION (Phase 2 & 3 only) =====
        if self.phase >= 2 and self.zero_crossings >= 4:
            # Calculate critical period from zero-crossing intervals
            if len(self.zero_crossing_times) >= 4:
                intervals = []
                for i in range(len(self.zero_crossing_times) - 1):
                    dt_cross = self.zero_crossing_times[i+1] - self.zero_crossing_times[i]
                    if dt_cross > 0.001:  # Valid interval
                        intervals.append(dt_cross)
                
                if len(intervals) >= 2:
                    # Tcr = 2 * average half-period
                    self.tcr = 2.0 * (sum(intervals[-4:]) / len(intervals[-4:]))
            
            # Calculate critical amplitude from peak-to-peak
            amplitude_pp = self.peak_rpm - self.min_rpm
            self.acr = amplitude_pp / 2.0 if amplitude_pp > 1 else 1.0
            
            # ===== ZIEGLER-NICHOLS TUNING =====
            if self.tcr > 0.001 and self.acr > 1:
                # Ultimate gain from relay amplitude and oscillation amplitude
                ku = (4.0 * self.relay_high) / (math.pi * self.acr)
                
                # Z-N aggressive tuning (good for fast response, suitable for vehicles)
                self.kp_result = 0.6 * ku
                self.ki_result = 1.2 * ku / self.tcr
                self.kd_result = 0.075 * ku * self.tcr
                
                # Clamp to safe ranges
                self.kp_result = max(0.01, min(5.0, self.kp_result))
                self.ki_result = max(0.001, min(1.0, self.ki_result))
                self.kd_result = max(0.001, min(0.5, self.kd_result))
                
                # Count stable oscillation periods (phase 2)
                if self.phase == 2 and self.zero_crossings >= 4:
                    self.stable_oscillations += 1
        
        # ===== STATE MACHINE =====
        # Stay in phase until time expires, then move to next
        if elapsed_time >= self.phase3_end:
            # Auto-learning complete: stay in convergence
            self.state = 'converged' if self.zero_crossings >= 4 else 'timeout'
        elif self.phase == 1:
            self.state = 'phase1'
        elif self.phase == 2:
            self.state = 'phase2'
        else:
            self.state = 'phase3'
        
        self.error_prev = error
        return self.relay_cmd, self.state
    
    def get_results(self) -> Tuple[float, float, float]:
        """Get tuned parameters"""
        return (self.kp_result, self.ki_result, self.kd_result)
    
    def get_status(self) -> dict:
        """Get detailed tuning status for UI"""
        return {
            'state': self.state,
            'phase': self.phase,
            'progress_percent': self.progress_percent,
            'zero_crossings': self.zero_crossings,
            'relay_oscillating': abs(self.relay_cmd) > 0.1,
            'tcr': round(self.tcr, 4),
            'acr': round(self.acr, 1),
            'kp': round(self.kp_result, 4),
            'ki': round(self.ki_result, 4),
            'kd': round(self.kd_result, 4),
            'samples': self.samples,
            'stable_oscillations': self.stable_oscillations,
            'rate_limit_violated': self.rate_limit_violated
        }

class BLDCSimulator:
    """Complete end-to-end BLDC simulator with adaptive control for any motor"""
    def __init__(self, config: SimConfig):
        self.config = config
        self.motor = BLDCMotor()
        # Adaptive controller: automatically scales PID gains for motor size
        self.controller = FOCController(config.kp, config.ki, config.kd, 
                                        motor_inertia_j=config.motor_inertia_kg_m2)
        self.dt = 1e-4
        # Use autolearn_duration_s from config (default 2.0s)
        self.autolearner = AutoLearner(config.rpm_target, 
                                       autolearn_duration_s=config.autolearn_duration_s,
                                       dt=self.dt)
        self.states: List[SimState] = []
        self.time = 0.0
        self.motor_state = MotorState.IDLE
        self.fault_code = 0
        self.autolearn_status = {}  # Track auto-learn progress for UI
        self.battery = BatteryWithSpec(BatterySpec(
            name='SimBattery', chemistry='LiPo',
            nominal_voltage_v=config.battery_nominal_v,
            capacity_ah=config.battery_capacity_ah,
            internal_resistance_ohm=config.battery_internal_resistance,
            max_discharge_current_a=150,
            efficiency_percent=config.battery_efficiency,
            temperature_coeff=-0.001), dt=self.dt)
        self.battery.soc = max(0.0, min(1.0, config.battery_soc_init))
        self.regen_energy_wh = 0.0  # Accumulated regen energy (Wh)
        self.prev_omega = 0.0        # Previous rotor speed for decel detection
        self.last_target_rpm = config.rpm_target  # Actual target chased this run
        self.brake_chopper_active = False # Estado do Chopper de Freio
    
    def _interpolate_profile(self, profile: List[Tuple[float, float]], t: float) -> float:
        """Linearly interpolate throttle percent at time t from a profile list"""
        if not profile:
            return self.config.throttle_percent
        if t <= profile[0][0]:
            return profile[0][1]
        if t >= profile[-1][0]:
            return profile[-1][1]
        for i in range(len(profile) - 1):
            t0, v0 = profile[i]
            t1, v1 = profile[i + 1]
            if t0 <= t <= t1:
                frac = (t - t0) / max(t1 - t0, 1e-9)
                return v0 + (v1 - v0) * frac
        return profile[-1][1]
    
    def run(self) -> List[dict]:
        """Execute complete simulation"""
        num_steps = int(self.config.duration_s / self.dt)
        autolearn_steps = int(self.config.autolearn_duration_s / self.dt)
        
        # Start auto-learning if enabled
        if self.config.autolearn_enabled:
            self.autolearner.start()
        
        for step in range(num_steps):
            # 1. Throttle pedal → RPM target
            if self.config.throttle_profile:
                throttle_percent = self._interpolate_profile(self.config.throttle_profile, self.time)
            else:
                throttle_percent = self.config.throttle_percent
            throttle_normalized = throttle_percent / 100.0
            rpm_target = throttle_normalized * 6000 + 1000  # 1000-7000 RPM range
            self.last_target_rpm = rpm_target
            
            # 2. Auto-learning phase (continuous until completion)
            relay_cmd = 0.0
            autolearn_active = self.config.autolearn_enabled and step < autolearn_steps
            if autolearn_active:
                relay_cmd, al_state = self.autolearner.step(self.motor.get_rpm(), self.time)
                self.autolearn_status = self.autolearner.get_status()
                
                # Converge only after full duration
                if al_state in ['converged', 'timeout']:
                    kp, ki, kd = self.autolearner.get_results()
                    self.controller.update_gains(kp, ki, kd)
                    # Disable auto-learn AFTER duration expires
                    if step >= autolearn_steps - 1:
                        self.config.autolearn_enabled = False
            
            # 3. FOC control law (or relay during auto-learn)
            if autolearn_active:
                v_alpha = relay_cmd * 20.0
                v_beta = 0.0
            else:
                v_alpha, v_beta = self.controller.compute(rpm_target, self.motor.get_rpm())
            
            # 3.5 Modelagem de Dead-Time (500ns em PWM de 20kHz)
            # Perda média de tensão devido ao tempo morto: V_loss = V_dc * (t_dead / T_pwm)
            t_pwm_s = 1.0 / 20000.0  # 50 µs
            dead_time_loss_v = self.battery.get_voltage() * ((self.config.dead_time_ns * 1e-9) / t_pwm_s)
            
            # 4. Motor simulation
            effective_load = self.config.load_torque if self.config.motor_brake else 0.0
            self.motor.step(v_alpha, v_beta, effective_load, self.config.ambient_temp_c)
            
            # 5. Safety checks
            self._check_faults()
            
            # 6. Generate 3-phase currents
            i_u, i_v, i_w = self.motor.get_3phase_currents()
            i_rms = math.sqrt((i_u**2 + i_v**2 + i_w**2) / 3)
            
            # 7. Voltages (simplified)
            v_u = 200 * math.cos(self.motor.theta)
            v_v = 200 * math.cos(self.motor.theta - 2*math.pi/3)
            v_w = 200 * math.cos(self.motor.theta - 4*math.pi/3)
            
            # 7.5 Regenerative braking + Chopper de Freio Dinâmico com Histerese
            rpm_actual = self.motor.get_rpm()
            omega_actual = rpm_actual * 2 * math.pi / 60.0
            regen_power = 0.0
            v_batt = self.battery.get_voltage()
            
            if self.config.motor_brake and rpm_actual > 50:
                decel = (self.prev_omega - omega_actual) / self.dt
                if decel > 1.0:
                    mech_power = self.motor.J * omega_actual * decel
                    regen_power = min(mech_power * 0.7, v_batt * 150)
                    i_regen = regen_power / max(v_batt, 1)
                    self.battery.charge(i_regen)
                    self.regen_energy_wh += regen_power * self.dt / 3600.0
            elif not self.config.motor_brake:
                self.battery.current_out = 0.0
            
            # Controle com Histerese do Chopper de Freio (54V liga, 51V desliga)
            if self.config.brake_chopper_enabled:
                if v_batt >= self.config.brake_chopper_v_on:
                    self.brake_chopper_active = True
                elif v_batt <= self.config.brake_chopper_v_off:
                    self.brake_chopper_active = False
                
                # Se o chopper está ativo, desvia corrente para R_brake (4.7Ω)
                if self.brake_chopper_active:
                    r_brake = 4.7
                    i_brake = v_batt / r_brake  # Corrente de queima no resistor de freio
                    self.battery.discharge(i_brake)
            
            self.prev_omega = omega_actual
            
            # 8. Record state
            state = SimState(
                time_s=self.time,
                mode='autolearn' if autolearn_active else 'manual',
                throttle=throttle_percent,
                rpm_target=rpm_target,
                rpm_actual=rpm_actual,
                current_u=i_u,
                current_v=i_v,
                current_w=i_w,
                current_rms=i_rms,
                voltage_u=v_u,
                voltage_v=v_v,
                voltage_w=v_w,
                torque_cmd=v_alpha,
                torque_actual=self.motor.Kt * i_rms,
                temp_motor_c=self.motor.temp,
                temp_driver_c=self.motor.temp + 5,
                motor_state=self.motor_state.name,
                kp=self.controller.kp,
                ki=self.controller.ki,
                kd=self.controller.kd,
                error_integral=self.controller.error_integral,
                fault_code=self.fault_code,
                soc=self.battery.get_soc(),
                battery_voltage=self.battery.get_voltage(),
                regen_power=regen_power,
                motor_brake=self.config.motor_brake,
                brake_chopper_active=self.brake_chopper_active,
                dead_time_loss_v=dead_time_loss_v
            )
            self.states.append(state)
            self.time += self.dt
        
        return [asdict(s) for s in self.states]
    
    def _check_faults(self):
        """Safety fault detection"""
        i_u, i_v, i_w = self.motor.get_3phase_currents()
        i_max = max(abs(i_u), abs(i_v), abs(i_w))
        
        self.fault_code = 0
        if i_max > self.config.max_current_a:
            self.fault_code |= 0x01  # Overcurrent
            self.motor_state = MotorState.FAULT
        
        if self.motor.temp > self.config.max_temp_c:
            self.fault_code |= 0x02  # Thermal limit
            self.motor_state = MotorState.THERMAL_LIMIT
        
        if self.motor.get_rpm() > 100 and self.fault_code == 0:
            self.motor_state = MotorState.RUNNING
        else:
            self.motor_state = MotorState.IDLE
    
    def get_summary(self) -> dict:
        """Compute simulation metrics"""
        if not self.states:
            return {}
        
        rpms = [s.rpm_actual for s in self.states]
        currents = [s.current_rms for s in self.states]
        temps = [s.temp_motor_c for s in self.states]
        
        skip_samples = int(0.5 / self.dt)
        steady_rpms = rpms[skip_samples:]
        steady_currents = currents[skip_samples:]
        
        return {
            'final_rpm': rpms[-1],
            'target_rpm': self.last_target_rpm,
            'error_percent': abs(rpms[-1] - self.last_target_rpm) / max(self.last_target_rpm, 1) * 100,
            'steady_rpm_avg': sum(steady_rpms) / len(steady_rpms) if steady_rpms else 0,
            'converged': abs(rpms[-1] - self.last_target_rpm) / max(self.last_target_rpm, 1) < 0.05,
            'peak_current': max(currents),
            'mean_current': sum(currents) / len(currents) if currents else 0,
            'peak_temp': max(temps),
            'motor_brake': self.config.motor_brake,
            'soc': self.battery.get_soc(),
            'battery_voltage': self.battery.get_voltage(),
            'regen_energy_wh': self.regen_energy_wh,
            'regen_power_max': max((s.regen_power for s in self.states), default=0.0),
            'final_kp': self.controller.kp,
            'final_ki': self.controller.ki,
            'final_kd': self.controller.kd,
            'faults': [s.fault_code for s in self.states if s.fault_code != 0],
        }

def run_simulation(config: SimConfig) -> Tuple[List[dict], dict, dict]:
    """Main simulation entry point
    
    Returns:
        states: List of simulation state snapshots
        summary: Performance summary metrics
        autolearn_status: Auto-learn tuning details (if was enabled)
    """
    sim = BLDCSimulator(config)
    states = sim.run()
    summary = sim.get_summary()
    # Always return autolearn status if it was enabled (config.autolearn_enabled gets modified in run())
    autolearn_status = sim.autolearn_status
    return states, summary, autolearn_status

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        config_dict = json.loads(sys.argv[1])
        config = SimConfig(**config_dict)
    else:
        config = SimConfig()
    
    print(f"Running BLDC simulator: Throttle={config.throttle_percent}%, AutoLearn={config.autolearn_enabled}")
    states, summary, autolearn_status = run_simulation(config)
    
    result = {
        'config': asdict(config),
        'summary': summary,
        'autolearn_status': autolearn_status,
        'num_states': len(states)
    }
    print(json.dumps(result, indent=2))
