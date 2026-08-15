#!/usr/bin/env python3
"""
Motor Controller Web API
Accepts simulation parameters via REST API
"""

from flask import Flask, request, jsonify
import json
from integrated_simulator import SimConfig, run_simulation, IntegratedSimulator
import time

app = Flask(__name__)

# Global simulation state
last_result = None
last_config = None

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    POST /api/simulate
    JSON body:
    {
        "rpm_target": 3000,
        "duration_s": 2.0,
        "kp": 0.3,
        "ki": 0.03,
        "kd": 0.01,
        "load_torque": 0.0
    }
    """
    global last_result, last_config
    
    try:
        data = request.json or {}
        
        # Build config with provided overrides
        config = SimConfig(
            rpm_target=float(data.get('rpm_target', 3000)),
            duration_s=float(data.get('duration_s', 2.0)),
            kp=float(data.get('kp', 0.3)),
            ki=float(data.get('ki', 0.03)),
            kd=float(data.get('kd', 0.01)),
            load_torque=float(data.get('load_torque', 0.0))
        )
        
        # Validate ranges
        if not (100 <= config.rpm_target <= 12000):
            return jsonify({'error': 'rpm_target must be 100-12000'}), 400
        if not (0.1 <= config.duration_s <= 10):
            return jsonify({'error': 'duration_s must be 0.1-10 seconds'}), 400
        if not (0.01 <= config.kp <= 5):
            return jsonify({'error': 'kp must be 0.01-5'}), 400
        
        # Run simulation
        start_time = time.time()
        states, summary = run_simulation(config)
        elapsed = time.time() - start_time
        
        last_result = {'states': states, 'summary': summary}
        last_config = config
        
        return jsonify({
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
            'elapsed_s': elapsed,
            'num_samples': len(states)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate_batch', methods=['POST'])
def simulate_batch():
    """
    POST /api/simulate_batch
    Run multiple simulations with different configs
    JSON body:
    {
        "simulations": [
            {"rpm_target": 2000, "kp": 0.3},
            {"rpm_target": 3000, "kp": 0.5},
            {"rpm_target": 5000, "kp": 0.2}
        ]
    }
    """
    try:
        data = request.json or {}
        sims = data.get('simulations', [])
        
        if not sims or len(sims) > 10:
            return jsonify({'error': 'provide 1-10 simulations'}), 400
        
        results = []
        for sim_config in sims:
            config = SimConfig(
                rpm_target=float(sim_config.get('rpm_target', 3000)),
                duration_s=float(sim_config.get('duration_s', 2.0)),
                kp=float(sim_config.get('kp', 0.3)),
                ki=float(sim_config.get('ki', 0.03)),
                kd=float(sim_config.get('kd', 0.01))
            )
            _, summary = run_simulation(config)
            results.append({
                'config': {
                    'rpm_target': config.rpm_target,
                    'kp': config.kp,
                    'ki': config.ki,
                    'kd': config.kd
                },
                'summary': summary
            })
        
        return jsonify({
            'status': 'success',
            'num_simulations': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get server status and last simulation"""
    return jsonify({
        'status': 'running',
        'last_config': {
            'rpm_target': last_config.rpm_target if last_config else None,
            'kp': last_config.kp if last_config else None
        } if last_config else None,
        'last_summary': last_result['summary'] if last_result else None
    }), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get detailed state history from last simulation"""
    if not last_result:
        return jsonify({'error': 'no simulation run yet'}), 404
    
    return jsonify({
        'status': 'success',
        'config': {
            'rpm_target': last_config.rpm_target if last_config else None
        },
        'states': last_result['states']
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'api': 'Motor Control Simulator',
        'version': '1.0',
        'endpoints': {
            'POST /api/simulate': 'Run single simulation with parameters',
            'POST /api/simulate_batch': 'Run batch of simulations',
            'GET /api/status': 'Get server status',
            'GET /api/data': 'Get detailed state history',
            'GET /': 'This help page'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
