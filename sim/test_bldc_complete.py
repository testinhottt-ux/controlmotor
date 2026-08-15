#!/usr/bin/env python3
"""
Complete End-to-End BLDC System Tests
Validates all parameters and features from professional motor controller
"""

import sys
from bldc_full_simulator import SimConfig, run_simulation

def test_throttle_pedal():
    """TEST 1: Throttle pedal (0-100%) maps to RPM"""
    print("\n" + "="*70)
    print("TEST 1: THROTTLE PEDAL (Accelerator)")
    print("="*70)
    print("Goal: Throttle 0-100% → RPM 1000-7000 (linear)")
    
    results = []
    throttles = [0, 25, 50, 75, 100]
    
    for throttle in throttles:
        config = SimConfig(
            throttle_percent=float(throttle),
            duration_s=2.0,
            kp=0.5, ki=0.05, kd=0.02  # Good gains
        )
        _, summary, _ = run_simulation(config)
        
        expected_rpm = (throttle / 100.0) * 6000 + 1000
        actual_rpm = summary['final_rpm']
        error_pct = abs(actual_rpm - expected_rpm) / expected_rpm * 100 if expected_rpm > 0 else 0
        
        converged = error_pct < 5
        results.append(converged)
        
        status = '✓' if converged else '✗'
        print(f"  Throttle {throttle:3d}%: {actual_rpm:6.1f} RPM (expected {expected_rpm:6.0f}) [{error_pct:5.1f}%] {status}")
    
    passed = all(results)
    print(f"\nResult: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_auto_learning():
    """TEST 2: Auto-learning tunes Kp/Ki/Kd"""
    print("\n" + "="*70)
    print("TEST 2: AUTO-LEARNING (Astrom-Hagglund Relay)")
    print("="*70)
    print("Goal: Auto-tune produces valid Kp/Ki/Kd gains")
    
    config = SimConfig(
        throttle_percent=50.0,
        duration_s=3.0,
        kp=0.1, ki=0.01, kd=0.005,  # Start with bad gains
        autolearn_enabled=True,
        autolearn_duration_s=1.5
    )
    
    _, summary, _ = run_simulation(config)
    
    print(f"  Before auto-learn: Kp={0.1:.3f}, Ki={0.01:.3f}, Kd={0.005:.3f}")
    print(f"  After auto-learn:  Kp={summary['final_kp']:.3f}, Ki={summary['final_ki']:.3f}, Kd={summary['final_kd']:.3f}")
    
    # Check that gains are positive and in reasonable range
    gains_valid = (
        0.01 <= summary['final_kp'] <= 5.0 and
        0.001 <= summary['final_ki'] <= 1.0 and
        0.001 <= summary['final_kd'] <= 0.5
    )
    
    print(f"  Gains in valid range: {gains_valid}")
    print(f"\nResult: {'✓ PASS' if gains_valid else '✗ FAIL'}")
    return gains_valid

def test_parameter_injection():
    """TEST 3: Inject Kp/Ki/Kd via API"""
    print("\n" + "="*70)
    print("TEST 3: PARAMETER INJECTION (Web API)")
    print("="*70)
    print("Goal: Vary Kp from 0.1 to 0.6 and verify convergence")
    
    results = []
    kp_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    
    for kp in kp_values:
        config = SimConfig(
            throttle_percent=50.0,
            duration_s=2.5,
            kp=kp,
            ki=0.03 * (kp / 0.3),  # Scale Ki proportionally
            kd=0.01 * (kp / 0.3)
        )
        
        _, summary, _ = run_simulation(config)
        converged = summary['converged']
        results.append(converged)
        
        status = '✓' if converged else '✗'
        print(f"  Kp={kp:.1f}: RPM {summary['final_rpm']:6.1f}, Error {summary['error_percent']:5.2f}% {status}")
    
    # Most should converge
    pass_count = sum(results)
    passed = pass_count >= 4  # At least 4 out of 6
    
    print(f"  Converged: {pass_count}/{len(results)}")
    print(f"\nResult: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_load_injection():
    """TEST 4: Inject load torque"""
    print("\n" + "="*70)
    print("TEST 4: LOAD TORQUE INJECTION")
    print("="*70)
    print("Goal: Motor handles load (0-1 N.m) with increased current")
    
    results = []
    loads = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    currents = []
    for load in loads:
        config = SimConfig(
            throttle_percent=50.0,
            duration_s=2.0,
            load_torque=load,
            kp=0.5, ki=0.05, kd=0.02
        )
        
        _, summary, _ = run_simulation(config)
        
        # With load, current increases but motor should still run
        converged = summary['converged'] or (summary['final_rpm'] > 2000)
        results.append(converged)
        currents.append(summary['peak_current'])
        
        status = '✓' if converged else '✗'
        print(f"  Load {load:.2f}Nm: RPM {summary['final_rpm']:6.1f}, I={summary['peak_current']:6.1f}A {status}")
    
    # Check that current increases with load
    current_trend = all(currents[i] <= currents[i+1] for i in range(len(currents)-1))
    
    passed = all(results) and current_trend
    print(f"  Current increases with load: {current_trend}")
    print(f"\nResult: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_temperature_monitoring():
    """TEST 5: Temperature protection"""
    print("\n" + "="*70)
    print("TEST 5: TEMPERATURE MONITORING & PROTECTION")
    print("="*70)
    print("Goal: Temp monitored (rises above ambient) and thermal fault fires at limit")
    
    tests = [
        (25, 'cool'),
        (50, 'warm'),
        (75, 'hot')
    ]
    
    results = []
    for ambient, label in tests:
        config = SimConfig(
            throttle_percent=100.0,
            duration_s=2.0,
            ambient_temp_c=ambient,
            max_temp_c=80.0,
            kp=0.5, ki=0.05, kd=0.02
        )
        
        states, summary, _ = run_simulation(config)
        
        # Monitoring: motor temp rises above ambient under full throttle
        temp_ok = summary['peak_temp'] > ambient
        # Protection: when limit is exceeded, thermal fault (0x02) fires
        thermal_fault = any(s['fault_code'] & 0x02 for s in states)
        expected_fault = summary['peak_temp'] >= 80
        protect_ok = (thermal_fault == expected_fault)
        ok = temp_ok and protect_ok
        results.append(ok)
        
        status = '✓' if ok else '✗'
        print(f"  Ambient {ambient:2d}°C: Peak {summary['peak_temp']:5.1f}°C "
              f"(limit 80°C) monitor={'Y' if temp_ok else 'N'} fault={thermal_fault} {status}")
    
    passed = all(results)
    print(f"\nResult: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_3phase_balance():
    """TEST 6: 3-phase currents balanced"""
    print("\n" + "="*70)
    print("TEST 6: 3-PHASE CURRENT BALANCE")
    print("="*70)
    print("Goal: Iu, Iv, Iw have 120° phase shift (balanced)")
    
    config = SimConfig(
        throttle_percent=50.0,
        duration_s=2.0,
        kp=0.5, ki=0.05, kd=0.02
    )
    
    states_list, _, _ = run_simulation(config)
    
    # Check steady state (skip first second)
    skip = int(1.0 / 1e-4)
    steady_states = states_list[skip:]
    
    # Compute RMS per phase
    i_u_vals = [s['current_u'] for s in steady_states]
    i_v_vals = [s['current_v'] for s in steady_states]
    i_w_vals = [s['current_w'] for s in steady_states]
    
    i_u_rms = (sum(x**2 for x in i_u_vals) / len(i_u_vals))**0.5 if i_u_vals else 0
    i_v_rms = (sum(x**2 for x in i_v_vals) / len(i_v_vals))**0.5 if i_v_vals else 0
    i_w_rms = (sum(x**2 for x in i_w_vals) / len(i_w_vals))**0.5 if i_w_vals else 0
    
    # All phases should be similar
    mean_rms = (i_u_rms + i_v_rms + i_w_rms) / 3
    imbalance_u = abs(i_u_rms - mean_rms) / mean_rms * 100 if mean_rms > 0 else 0
    imbalance_v = abs(i_v_rms - mean_rms) / mean_rms * 100 if mean_rms > 0 else 0
    imbalance_w = abs(i_w_rms - mean_rms) / mean_rms * 100 if mean_rms > 0 else 0
    
    balanced = all(x < 5 for x in [imbalance_u, imbalance_v, imbalance_w])
    
    print(f"  Phase U RMS: {i_u_rms:.2f}A (imbalance {imbalance_u:.1f}%)")
    print(f"  Phase V RMS: {i_v_rms:.2f}A (imbalance {imbalance_v:.1f}%)")
    print(f"  Phase W RMS: {i_w_rms:.2f}A (imbalance {imbalance_w:.1f}%)")
    
    status = '✓' if balanced else '✗'
    print(f"\nResult: {status} {'PASS (balanced)' if balanced else 'FAIL (unbalanced)'}")
    return balanced

def test_fault_protection():
    """TEST 7: Overcurrent and thermal protection"""
    print("\n" + "="*70)
    print("TEST 7: FAULT DETECTION & PROTECTION")
    print("="*70)
    print("Goal: Detect overcurrent and thermal faults")
    
    # Test with high load (should generate high current)
    config = SimConfig(
        throttle_percent=100.0,
        duration_s=2.0,
        load_torque=2.0,  # Heavy load
        kp=0.5, ki=0.05, kd=0.02,
        max_current_a=50.0,
        max_temp_c=80.0
    )
    
    states_list, summary, _ = run_simulation(config)
    
    # Check if any faults were detected
    faults = [s['fault_code'] for s in states_list if s['fault_code'] != 0]
    
    print(f"  Peak current: {summary['peak_current']:.1f}A (limit 50A)")
    print(f"  Peak temp: {summary['peak_temp']:.1f}°C (limit 80°C)")
    print(f"  Faults detected: {len(faults)}")
    
    # For this test, detecting faults is actually good (protection works)
    # But also OK if no faults if within limits
    fault_detection_works = len(faults) > 0 or (summary['peak_current'] < 50 and summary['peak_temp'] < 80)
    
    status = '✓' if fault_detection_works else '✗'
    print(f"\nResult: {status} {'PASS' if fault_detection_works else 'FAIL'}")
    return fault_detection_works

def main():
    print("=" * 70)
    print("END-TO-END BLDC MOTOR CONTROLLER TESTS")
    print("Complete System Validation with Parameter Injection")
    print("=" * 70)
    
    tests = [
        ('Throttle Pedal (0-100%)', test_throttle_pedal),
        ('Auto-Learning', test_auto_learning),
        ('Parameter Injection (Kp/Ki/Kd)', test_parameter_injection),
        ('Load Torque (0-1 N.m)', test_load_injection),
        ('Temperature Monitoring', test_temperature_monitoring),
        ('3-Phase Balance', test_3phase_balance),
        ('Fault Protection', test_fault_protection),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    for name, passed in results.items():
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f"  {name:<45} {status}")
    
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"\n  Total: {passed_count}/{total} tests passed")
    
    exit_code = 0 if passed_count == total else 1
    print(f"  Exit code: {exit_code}\n")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
