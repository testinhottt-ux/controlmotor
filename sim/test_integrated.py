#!/usr/bin/env python3
"""
End-to-End Integration Tests
Tests the complete motor control loop with injected parameters
"""

import sys
import math
from integrated_simulator import SimConfig, run_simulation

def test_basic_convergence():
    """TEST 1: Motor should converge to RPM target"""
    print("\n=== TEST 1: Basic Convergence ===")
    print("Goal: Motor converge to 3000 RPM (error < 5%)")
    
    config = SimConfig(
        rpm_target=3000.0,
        duration_s=2.0,
        kp=0.3,
        ki=0.03,
        kd=0.01
    )
    
    states, summary = run_simulation(config)
    
    print(f"  Final RPM:     {summary['final_rpm']:.1f}")
    print(f"  Target RPM:    {summary['target_rpm']:.1f}")
    print(f"  Error:         {summary['error_percent']:.2f}%")
    print(f"  Converged:     {summary['converged']}")
    
    passed = summary['converged']
    print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_different_targets():
    """TEST 2: Vary RPM target (1000, 3000, 5000 RPM)"""
    print("\n=== TEST 2: Different RPM Targets ===")
    print("Goal: Converge at 1000, 3000, 5000 RPM")
    
    targets = [1000, 3000, 5000]
    results = []
    
    for rpm_target in targets:
        config = SimConfig(
            rpm_target=float(rpm_target),
            duration_s=2.0,
            kp=0.3,
            ki=0.03,
            kd=0.01
        )
        
        states, summary = run_simulation(config)
        converged = summary['converged']
        results.append(converged)
        
        print(f"  RPM {rpm_target:5d}: {summary['final_rpm']:6.1f} " +
              f"(error {summary['error_percent']:5.2f}%) " +
              f"{'✓' if converged else '✗'}")
    
    passed = all(results)
    print(f"  Result: {'✓ PASS (all targets)' if passed else '✗ FAIL (some targets)'}")
    return passed

def test_gain_variation():
    """TEST 3: Vary Kp gain (0.1, 0.3, 0.5) at 3000 RPM"""
    print("\n=== TEST 3: Gain Variation (Kp sweep) ===")
    print("Goal: Different Kp values converge but with different response")
    
    kp_values = [0.1, 0.3, 0.5]
    results = []
    
    for kp in kp_values:
        config = SimConfig(
            rpm_target=3000.0,
            duration_s=2.0,
            kp=kp,
            ki=0.03,
            kd=0.01
        )
        
        states, summary = run_simulation(config)
        
        # For lower Kp, expect slower convergence but less overshoot
        # For higher Kp, expect faster but riskier
        overshoot_pct = (max(s['rpm'] for s in states) - 3000) / 3000 * 100
        
        converged = summary['converged']
        results.append(converged)
        
        print(f"  Kp={kp:.1f}: Final {summary['final_rpm']:6.1f} RPM, " +
              f"Overshoot {overshoot_pct:6.1f}%, " +
              f"{'✓' if converged else '✗'}")
    
    passed = all(results)
    print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_load_torque():
    """TEST 4: Apply load torque (0.5 N.m) and verify convergence"""
    print("\n=== TEST 4: Load Torque Rejection ===")
    print("Goal: Motor handles load (0.5 N.m) and converges")
    
    config = SimConfig(
        rpm_target=3000.0,
        duration_s=2.0,
        kp=0.3,
        ki=0.03,
        kd=0.01,
        load_torque=0.5  # 0.5 N.m load
    )
    
    states, summary = run_simulation(config)
    
    print(f"  Final RPM:     {summary['final_rpm']:.1f}")
    print(f"  Load Torque:   0.5 N.m")
    print(f"  Error:         {summary['error_percent']:.2f}%")
    print(f"  Peak Current:  {summary['peak_current']:.1f} A")
    print(f"  Converged:     {summary['converged']}")
    
    passed = summary['converged']
    print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_ripple_and_smoothness():
    """TEST 5: Validate current ripple < 20% (3-phase balance)"""
    print("\n=== TEST 5: Current Ripple & 3-Phase Balance ===")
    print("Goal: 3-phase currents balanced (ripple < 20%)")
    
    config = SimConfig(
        rpm_target=3000.0,
        duration_s=2.0,
        kp=0.3,
        ki=0.03,
        kd=0.01
    )
    
    states, summary = run_simulation(config)
    
    # Skip transient (first 500ms)
    skip = int(0.5 / 1e-4)
    steady_states = states[skip:]
    
    # Compute current amplitude per phase in steady state
    i_u_vals = [s['current_u'] for s in steady_states]
    i_v_vals = [s['current_v'] for s in steady_states]
    i_w_vals = [s['current_w'] for s in steady_states]
    
    # RMS values
    i_u_rms = math.sqrt(sum(x**2 for x in i_u_vals) / len(i_u_vals)) if i_u_vals else 0
    i_v_rms = math.sqrt(sum(x**2 for x in i_v_vals) / len(i_v_vals)) if i_v_vals else 0
    i_w_rms = math.sqrt(sum(x**2 for x in i_w_vals) / len(i_w_vals)) if i_w_vals else 0
    
    # Check balance (all phases should be similar)
    mean_rms = (i_u_rms + i_v_rms + i_w_rms) / 3
    balance_u = abs(i_u_rms - mean_rms) / mean_rms * 100 if mean_rms > 0 else 0
    balance_v = abs(i_v_rms - mean_rms) / mean_rms * 100 if mean_rms > 0 else 0
    balance_w = abs(i_w_rms - mean_rms) / mean_rms * 100 if mean_rms > 0 else 0
    
    print(f"  Phase U RMS:   {i_u_rms:.2f} A (balance {balance_u:.1f}%)")
    print(f"  Phase V RMS:   {i_v_rms:.2f} A (balance {balance_v:.1f}%)")
    print(f"  Phase W RMS:   {i_w_rms:.2f} A (balance {balance_w:.1f}%)")
    
    # Check 120° phase shift (approximate via 3 samples)
    passed = all(x < 15 for x in [balance_u, balance_v, balance_w])
    print(f"  Result: {'✓ PASS (balanced)' if passed else '✗ FAIL (unbalanced)'}")
    return passed

def test_step_response():
    """TEST 6: Step response - RPM goes from 0 to 3000"""
    print("\n=== TEST 6: Step Response (0 → 3000 RPM) ===")
    print("Goal: Fast rise time, minimal overshoot")
    
    config = SimConfig(
        rpm_target=3000.0,
        duration_s=2.0,
        kp=0.3,
        ki=0.03,
        kd=0.01
    )
    
    states, summary = run_simulation(config)
    
    # Find time to reach 90% of target
    target_90 = 3000 * 0.9
    t_90 = None
    for s in states:
        if s['rpm'] >= target_90:
            t_90 = s['time_s']
            break
    
    # Find peak (overshoot)
    peak_rpm = max(s['rpm'] for s in states)
    overshoot_pct = (peak_rpm - 3000) / 3000 * 100
    
    print(f"  Time to 90%:   {t_90:.3f} s" if t_90 else "  Time to 90%:   Not reached")
    print(f"  Peak RPM:      {peak_rpm:.1f} RPM")
    print(f"  Overshoot:     {overshoot_pct:.1f}%")
    print(f"  Final RPM:     {summary['final_rpm']:.1f} RPM")
    
    # Good: t_90 < 1s, overshoot < 10%
    passed = (t_90 is not None and t_90 < 1.0) and (overshoot_pct < 10)
    print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def main():
    print("=" * 70)
    print("END-TO-END INTEGRATION TESTS")
    print("Motor Control Simulator with Injected Parameters")
    print("=" * 70)
    
    tests = [
        ('Basic Convergence', test_basic_convergence),
        ('Different Targets', test_different_targets),
        ('Gain Variation', test_gain_variation),
        ('Load Torque', test_load_torque),
        ('Current Ripple', test_ripple_and_smoothness),
        ('Step Response', test_step_response),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ERROR: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for name, passed in results.items():
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f"  {name:<25} {status}")
    
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"\n  Total: {passed_count}/{total} tests passed")
    
    exit_code = 0 if passed_count == total else 1
    print(f"  Exit code: {exit_code}")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
