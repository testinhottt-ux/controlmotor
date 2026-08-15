#!/usr/bin/env python3
"""
API Client Test - Simulates HTTP requests to motor controller API
Tests parameter injection via REST-like calls
"""

import json
from integrated_simulator import SimConfig, run_simulation
import sys

class MockAPIClient:
    """Simulates REST API calls without needing Flask"""
    
    def simulate(self, params: dict) -> dict:
        """Simulate POST /api/simulate"""
        try:
            config = SimConfig(
                rpm_target=float(params.get('rpm_target', 3000)),
                duration_s=float(params.get('duration_s', 2.0)),
                kp=float(params.get('kp', 0.3)),
                ki=float(params.get('ki', 0.03)),
                kd=float(params.get('kd', 0.01)),
                load_torque=float(params.get('load_torque', 0.0))
            )
            
            states, summary = run_simulation(config)
            
            return {
                'status': 'success',
                'config': {
                    'rpm_target': config.rpm_target,
                    'duration_s': config.duration_s,
                    'kp': config.kp,
                    'ki': config.ki,
                    'kd': config.kd,
                    'load_torque': config.load_torque
                },
                'summary': summary,
                'num_samples': len(states)
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def simulate_batch(self, simulations: list) -> dict:
        """Simulate POST /api/simulate_batch"""
        results = []
        for sim in simulations:
            result = self.simulate(sim)
            if result['status'] == 'success':
                results.append({
                    'config': result['config'],
                    'summary': result['summary']
                })
        return {
            'status': 'success',
            'num_simulations': len(results),
            'results': results
        }

def test_api_single_call():
    """API Test 1: Single simulation call"""
    print("\n=== API TEST 1: Single Simulation ===")
    print("Simulating: POST /api/simulate")
    
    client = MockAPIClient()
    
    params = {
        'rpm_target': 4000,
        'duration_s': 2.0,
        'kp': 0.4,
        'ki': 0.04,
        'kd': 0.015
    }
    
    print(f"  Request: {json.dumps(params)}")
    response = client.simulate(params)
    
    print(f"  Response status: {response['status']}")
    if response['status'] == 'success':
        print(f"  Final RPM: {response['summary']['final_rpm']:.1f}")
        print(f"  Target RPM: {response['config']['rpm_target']:.0f}")
        print(f"  Error: {response['summary']['error_percent']:.2f}%")
        print(f"  Converged: {response['summary']['converged']}")
        passed = response['summary']['converged']
    else:
        print(f"  Error: {response.get('error')}")
        passed = False
    
    print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
    return passed

def test_api_batch_call():
    """API Test 2: Batch simulations"""
    print("\n=== API TEST 2: Batch Simulations ===")
    print("Simulating: POST /api/simulate_batch")
    
    client = MockAPIClient()
    
    batch = [
        {'rpm_target': 1000, 'kp': 0.2},
        {'rpm_target': 2000, 'kp': 0.3},
        {'rpm_target': 3000, 'kp': 0.4},
        {'rpm_target': 4000, 'kp': 0.5},
    ]
    
    print(f"  Request: {len(batch)} simulations")
    response = client.simulate_batch(batch)
    
    print(f"  Response status: {response['status']}")
    print(f"  Number of results: {response['num_simulations']}")
    
    all_converged = True
    for i, result in enumerate(response['results']):
        conv = result['summary']['converged']
        all_converged = all_converged and conv
        print(f"    Sim {i+1}: RPM {result['config']['rpm_target']:5.0f} " +
              f"→ {result['summary']['final_rpm']:6.1f} " +
              f"(Kp={result['config']['kp']:.1f}) {'✓' if conv else '✗'}")
    
    print(f"  Result: {'✓ PASS' if all_converged else '✗ FAIL'}")
    return all_converged

def test_api_parameter_sweep():
    """API Test 3: Parameter sweep (vary Kp, Ki, Kd)"""
    print("\n=== API TEST 3: Parameter Sweep ===")
    print("Varying Kp from 0.1 to 0.6 at RPM target 3000")
    
    client = MockAPIClient()
    
    kp_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    results = []
    
    for kp in kp_values:
        params = {
            'rpm_target': 3000,
            'kp': kp,
            'ki': 0.03,
            'kd': 0.01,
            'duration_s': 2.0
        }
        response = client.simulate(params)
        
        if response['status'] == 'success':
            conv = response['summary']['converged']
            error = response['summary']['error_percent']
            results.append((kp, conv, error))
            print(f"  Kp={kp:.1f}: Final={response['summary']['final_rpm']:6.1f} RPM, " +
                  f"Error={error:5.2f}%, " +
                  f"{'✓ Converged' if conv else '✗ Failed'}")
        else:
            results.append((kp, False, 999))
            print(f"  Kp={kp:.1f}: ERROR")
    
    all_conv = all(conv for _, conv, _ in results)
    print(f"  Result: {'✓ PASS (all converged)' if all_conv else '✗ FAIL'}")
    return all_conv

def test_api_with_load():
    """API Test 4: Load injection"""
    print("\n=== API TEST 4: Load Torque Injection ===")
    print("Testing motor with applied load")
    
    client = MockAPIClient()
    
    loads = [0.0, 0.2, 0.5, 1.0]
    results = []
    
    for load in loads:
        params = {
            'rpm_target': 3000,
            'kp': 0.3,
            'load_torque': load,
            'duration_s': 2.0
        }
        response = client.simulate(params)
        
        if response['status'] == 'success':
            conv = response['summary']['converged']
            peak_i = response['summary']['peak_current']
            results.append((load, conv, peak_i))
            print(f"  Load {load:.1f} N.m: Final={response['summary']['final_rpm']:6.1f} RPM, " +
                  f"Peak I={peak_i:6.1f} A, {'✓' if conv else '✗'}")
        else:
            results.append((load, False, 0))
            print(f"  Load {load:.1f} N.m: ERROR")
    
    all_conv = all(conv for _, conv, _ in results)
    print(f"  Result: {'✓ PASS (all loads handled)' if all_conv else '✗ FAIL'}")
    return all_conv

def test_api_rapid_commands():
    """API Test 5: Rapid successive commands"""
    print("\n=== API TEST 5: Rapid Successive Commands ===")
    print("Simulating fast repeated API calls")
    
    client = MockAPIClient()
    
    commands = [
        {'rpm_target': 2000, 'kp': 0.25},
        {'rpm_target': 3000, 'kp': 0.30},
        {'rpm_target': 4000, 'kp': 0.35},
        {'rpm_target': 3000, 'kp': 0.30},
        {'rpm_target': 1000, 'kp': 0.20},
    ]
    
    all_passed = True
    for i, cmd in enumerate(commands):
        response = client.simulate(cmd)
        if response['status'] == 'success' and response['summary']['converged']:
            print(f"  Command {i+1}: RPM {cmd['rpm_target']} ✓")
        else:
            print(f"  Command {i+1}: RPM {cmd['rpm_target']} ✗")
            all_passed = False
    
    print(f"  Result: {'✓ PASS (all commands)' if all_passed else '✗ FAIL'}")
    return all_passed

def main():
    print("=" * 70)
    print("API CLIENT TESTS - Parameter Injection via REST Calls")
    print("=" * 70)
    
    tests = [
        ('Single Call', test_api_single_call),
        ('Batch Call', test_api_batch_call),
        ('Parameter Sweep', test_api_parameter_sweep),
        ('Load Injection', test_api_with_load),
        ('Rapid Commands', test_api_rapid_commands),
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
        print(f"  {name:<30} {status}")
    
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"\n  Total: {passed_count}/{total} API tests passed")
    
    exit_code = 0 if passed_count == total else 1
    print(f"  Exit code: {exit_code}")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
