#!/usr/bin/env python3
"""
Motor and Battery Model Library
Multiple motor types (Small, Medium, Large BLDC)
Multiple battery types (LiPo, LiFePO4, Lead-Acid)
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import math


@dataclass
class MotorSpec:
    """Motor specifications"""
    name: str
    power_rating_w: float      # Watts
    voltage_nominal_v: float   # Nominal voltage (V)
    speed_max_rpm: int         # Maximum RPM
    torque_rated_nm: float     # Rated torque (N·m)
    inertia_kg_m2: float       # Moment of inertia
    resistance_ohm: float      # Phase resistance (Ω)
    inductance_h: float        # Phase inductance (H)
    kt_nm_per_a: float         # Torque constant (N·m/A)
    back_emf_v_per_rpm: float  # Back-EMF constant (V/RPM)
    thermal_tau_s: float       # Thermal time constant (s)


@dataclass
class BatterySpec:
    """Battery specifications"""
    name: str
    chemistry: str              # LiPo, LiFePO4, Lead-Acid
    nominal_voltage_v: float   # Nominal voltage (V)
    capacity_ah: float         # Capacity (A·h)
    internal_resistance_ohm: float  # Internal resistance (Ω)
    max_discharge_current_a: float  # Max continuous discharge (A)
    efficiency_percent: float   # Round-trip efficiency (%)
    temperature_coeff: float    # Voltage drop per °C


class MotorCatalog:
    """Library of motor models"""
    
    SMALL_BLDC = MotorSpec(
        name="Small BLDC (100W)",
        power_rating_w=100,
        voltage_nominal_v=48,
        speed_max_rpm=3000,
        torque_rated_nm=0.3,
        inertia_kg_m2=0.0001,
        resistance_ohm=0.5,
        inductance_h=0.5e-3,
        kt_nm_per_a=0.1,
        back_emf_v_per_rpm=0.025,
        thermal_tau_s=5.0
    )
    
    MEDIUM_BLDC = MotorSpec(
        name="Medium BLDC (500W)",
        power_rating_w=500,
        voltage_nominal_v=48,
        speed_max_rpm=4000,
        torque_rated_nm=1.2,
        inertia_kg_m2=0.005,
        resistance_ohm=0.15,
        inductance_h=1.0e-3,
        kt_nm_per_a=0.28,
        back_emf_v_per_rpm=0.035,
        thermal_tau_s=10.0
    )
    
    LARGE_BLDC = MotorSpec(
        name="Large BLDC (1kW)",
        power_rating_w=1000,
        voltage_nominal_v=48,
        speed_max_rpm=5000,
        torque_rated_nm=2.0,
        inertia_kg_m2=0.010,
        resistance_ohm=0.08,
        inductance_h=1.5e-3,
        kt_nm_per_a=0.45,
        back_emf_v_per_rpm=0.045,
        thermal_tau_s=15.0
    )
    
    @staticmethod
    def get_by_name(name: str) -> MotorSpec:
        """Get motor by name"""
        motors = {
            'small': MotorCatalog.SMALL_BLDC,
            'medium': MotorCatalog.MEDIUM_BLDC,
            'large': MotorCatalog.LARGE_BLDC,
        }
        return motors.get(name.lower(), MotorCatalog.MEDIUM_BLDC)
    
    @staticmethod
    def list_all() -> Dict[str, str]:
        """List all available motors"""
        return {
            'small': MotorCatalog.SMALL_BLDC.name,
            'medium': MotorCatalog.MEDIUM_BLDC.name,
            'large': MotorCatalog.LARGE_BLDC.name,
        }


class BatteryCatalog:
    """Library of battery models"""
    
    LIPO_48V = BatterySpec(
        name="LiPo 48V (5Ah)",
        chemistry="LiPo",
        nominal_voltage_v=48.0,
        capacity_ah=5.0,
        internal_resistance_ohm=0.05,
        max_discharge_current_a=100,
        efficiency_percent=95,
        temperature_coeff=-0.001
    )
    
    LIFEPO4_48V = BatterySpec(
        name="LiFePO4 48V (10Ah)",
        chemistry="LiFePO4",
        nominal_voltage_v=48.0,
        capacity_ah=10.0,
        internal_resistance_ohm=0.03,
        max_discharge_current_a=150,
        efficiency_percent=98,
        temperature_coeff=-0.0005
    )
    
    LEAD_ACID_48V = BatterySpec(
        name="Lead-Acid 48V (20Ah)",
        chemistry="Lead-Acid",
        nominal_voltage_v=48.0,
        capacity_ah=20.0,
        internal_resistance_ohm=0.15,
        max_discharge_current_a=80,
        efficiency_percent=85,
        temperature_coeff=-0.003
    )
    
    @staticmethod
    def get_by_name(name: str) -> BatterySpec:
        """Get battery by name"""
        batteries = {
            'lipo': BatteryCatalog.LIPO_48V,
            'lifepo4': BatteryCatalog.LIFEPO4_48V,
            'lead-acid': BatteryCatalog.LEAD_ACID_48V,
        }
        return batteries.get(name.lower(), BatteryCatalog.LIPO_48V)
    
    @staticmethod
    def list_all() -> Dict[str, str]:
        """List all available batteries"""
        return {
            'lipo': BatteryCatalog.LIPO_48V.name,
            'lifepo4': BatteryCatalog.LIFEPO4_48V.name,
            'lead-acid': BatteryCatalog.LEAD_ACID_48V.name,
        }


class BrakeModel:
    """Realistic brake/friction model for vehicle dynamics"""
    def __init__(self, k_friction: float = 0.002, k_aerodynamic: float = 0.00001):
        self.k_friction = k_friction          # Coulomb friction (tires + drivetrain)
        self.k_aerodynamic = k_aerodynamic    # Aerodynamic drag (proportional to RPM²)
    
    def compute_braking_torque(self, rpm: float) -> float:
        """
        Compute braking torque (N·m) from friction and aerodynamic drag
        For car application: simulates rolling resistance + air drag
        """
        omega = rpm * 2 * math.pi / 60  # Convert to rad/s
        # Friction torque (proportional to speed)
        tau_friction = self.k_friction * omega
        # Aerodynamic drag (proportional to speed²)
        tau_aerodynamic = self.k_aerodynamic * omega * omega
        return tau_friction + tau_aerodynamic


class BLDCMotorWithSpec:
    """BLDC Motor with configurable specifications"""
    
    def __init__(self, spec: MotorSpec, dt: float = 1e-4, brake_model: Optional[BrakeModel] = None):
        self.spec = spec
        self.dt = dt
        self.brake_model = brake_model if brake_model else BrakeModel()
        
        # State variables
        self.rpm = 0.0
        self.theta = 0.0  # Electrical angle (rad)
        self.omega = 0.0  # Angular velocity (rad/s)
        self.torque_cmd = 0.0
        self.torque_load = 0.0
        self.torque_brake = 0.0  # Friction braking torque
        self.temp_motor = 25.0
        self.temp_ambient = 25.0
        
        # 3-phase current simulation
        self.ia = 0.0
        self.ib = 0.0
        self.ic = 0.0
    
    def set_ambient_temp(self, temp_c: float):
        """Set ambient temperature"""
        self.temp_ambient = temp_c
    
    def step(self, v_alpha: float, v_beta: float, load_torque: float = 0.0, ambient_temp: float = 25.0):
        """Simulate one time step"""
        self.set_ambient_temp(ambient_temp)
        self.torque_load = load_torque
        
        # Back-EMF voltage (simplified)
        back_emf = self.spec.back_emf_v_per_rpm * self.rpm
        
        # Voltage equation: V = I*R + L*dI/dt + back_emf
        # Simplified: assume fast current response
        current = (v_alpha - back_emf) / self.spec.resistance_ohm if self.spec.resistance_ohm > 0 else 0.0
        current = max(-self.spec.kt_nm_per_a * self.rpm / 10, min(self.spec.kt_nm_per_a * self.rpm / 10, current))
        
        # Torque generation
        self.torque_cmd = self.spec.kt_nm_per_a * current
        
        # Braking torque from friction (realistic car model)
        self.torque_brake = self.brake_model.compute_braking_torque(self.rpm)
        
        # Mechanical dynamics: J*dω/dt = τ_cmd - τ_load - τ_brake - B*ω
        damping = 0.01 * self.spec.inertia_kg_m2
        dtheta = self.omega * self.dt
        domega = (self.torque_cmd - self.torque_load - self.torque_brake - damping * self.omega) / self.spec.inertia_kg_m2
        
        self.omega += domega * self.dt
        self.theta += dtheta
        self.theta = self.theta % (2 * math.pi)
        
        # RPM conversion
        self.rpm = (self.omega / (2 * math.pi)) * 60
        self.rpm = max(0, self.rpm)
        
        # Thermal model
        power_dissipated = abs(current * current * self.spec.resistance_ohm)
        dtemp = (power_dissipated / 1000 - (self.temp_motor - self.temp_ambient) / 50) / self.spec.thermal_tau_s
        self.temp_motor += dtemp * self.dt
        self.temp_motor = max(self.temp_ambient, self.temp_motor)
        
        # 3-phase currents (simplified sinusoidal)
        self.ia = current * math.cos(self.theta)
        self.ib = current * math.cos(self.theta - 2*math.pi/3)
        self.ic = current * math.cos(self.theta - 4*math.pi/3)
    
    def get_rpm(self) -> float:
        """Get current RPM"""
        return self.rpm
    
    def get_torque(self) -> float:
        """Get current torque"""
        return self.torque_cmd
    
    def get_temp(self) -> float:
        """Get motor temperature"""
        return self.temp_motor
    
    def get_3phase_currents(self) -> Tuple[float, float, float]:
        """Get 3-phase currents"""
        return (self.ia, self.ib, self.ic)
    
    def get_current_rms(self) -> float:
        """Get RMS current"""
        return math.sqrt((self.ia**2 + self.ib**2 + self.ic**2) / 3)


class BatteryWithSpec:
    """Battery model with configurable specifications"""
    
    def __init__(self, spec: BatterySpec, dt: float = 1e-4):
        self.spec = spec
        self.dt = dt
        self.soc = 1.0  # State of charge (0-1)
        self.voltage = spec.nominal_voltage_v
        self.current_out = 0.0
    
    def discharge(self, current_a: float) -> float:
        """
        Realistic battery discharge with non-linear voltage curve
        current_a: discharge current (A)
        Returns: actual voltage (V)
        """
        # Clamp current to max discharge
        current_a = min(abs(current_a), self.spec.max_discharge_current_a)
        self.current_out = current_a
        
        # Voltage drop from internal resistance (Ohm's Law)
        voltage_drop_internal = current_a * self.spec.internal_resistance_ohm
        
        # Non-linear discharge curve (more realistic than linear)
        # Most battery chemistries have flat voltage until ~20% SOC, then steep drop
        if self.soc > 0.2:
            # Flat region: 0-80% (little voltage drop with SOC)
            soc_voltage = self.spec.nominal_voltage_v * (0.9 + 0.1 * self.soc)
        else:
            # Steep region: 0-20% (sharp voltage collapse)
            soc_voltage = self.spec.nominal_voltage_v * (0.6 + 1.5 * self.soc)
        
        # Temperature effect (cold reduces voltage)
        # 25°C is baseline, roughly -1mV per °C below 25°C
        temp_derate = max(0.9, 1.0 - (25 - 20) * self.spec.temperature_coeff)
        soc_voltage *= temp_derate
        
        # Final voltage: no negative allowed
        self.voltage = max(0, soc_voltage - voltage_drop_internal)
        
        # SOC depletion (Coulomb counting with efficiency)
        delta_soc = (current_a * self.dt) / (self.spec.capacity_ah * 3600)
        delta_soc *= (1.0 - (1.0 - self.spec.efficiency_percent / 100.0))  # Account for losses
        self.soc = max(0, self.soc - delta_soc)
        
        return self.voltage
    
    def get_soc(self) -> float:
        """Get state of charge (0-1)"""
        return self.soc
    
    def charge(self, regen_current_a: float) -> float:
        """
        Regenerative braking charge. Accepts the (positive) magnitude of
        current flowing BACK into the battery and increases SOC.
        Returns: updated battery voltage (V)
        """
        if regen_current_a <= 0:
            return self.voltage
        
        # Regeneration charge current (bounded by what the pack can absorb)
        charge_a = min(regen_current_a, self.spec.max_discharge_current_a * 0.5)
        self.current_out = -charge_a  # Negative = charging
        
        # Charging raises terminal voltage (internal resistance drop in reverse)
        voltage_rise = charge_a * self.spec.internal_resistance_ohm
        self.voltage = min(self.spec.nominal_voltage_v * 1.1, self.voltage + voltage_rise)
        
        # Coulomb counting: SOC increases (with round-trip efficiency)
        delta_soc = (charge_a * self.dt) / (self.spec.capacity_ah * 3600)
        delta_soc *= (self.spec.efficiency_percent / 100.0)  # Regen is not 100% efficient
        self.soc = min(1.0, self.soc + delta_soc)
        
        return self.voltage
    
    def get_voltage(self) -> float:
        """Get battery voltage"""
        return self.voltage
    
    def get_remaining_energy_wh(self) -> float:
        """Get remaining energy (Wh)"""
        return self.spec.nominal_voltage_v * self.spec.capacity_ah * self.soc
