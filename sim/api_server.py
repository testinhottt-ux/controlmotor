#!/usr/bin/env python3
"""
Motor Controller Web API
Accepts simulation parameters via REST API
Supports Flask if available, with automatic zero-dependency fallback to standard http.server.
"""

import json
import time
import os
import sys

# Ensure sim directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from integrated_simulator import SimConfig, run_simulation, IntegratedSimulator

try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# Global simulation state
last_result = None
last_config = None

if HAS_FLASK:
    app = Flask(__name__)

    @app.route('/api/simulate', methods=['POST'])
    def simulate():
        global last_result, last_config
        try:
            data = request.json or {}
            config = SimConfig(
                rpm_target=float(data.get('rpm_target', 3000)),
                duration_s=float(data.get('duration_s', 2.0)),
                kp=float(data.get('kp', 0.3)),
                ki=float(data.get('ki', 0.03)),
                kd=float(data.get('kd', 0.01)),
                load_torque=float(data.get('load_torque', 0.0))
            )
            
            if not (100 <= config.rpm_target <= 12000):
                return jsonify({'error': 'rpm_target must be 100-12000'}), 400
            if not (0.1 <= config.duration_s <= 10):
                return jsonify({'error': 'duration_s must be 0.1-10 seconds'}), 400
            if not (0.01 <= config.kp <= 5):
                return jsonify({'error': 'kp must be 0.01-5'}), 400
            
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

    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({
            'status': 'running',
            'last_config': {
                'rpm_target': last_config.rpm_target if last_config else None,
                'kp': last_config.kp if last_config else None
            } if last_config else None,
            'last_summary': last_result['summary'] if last_result else None
        }), 200

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'api': 'Motor Control Simulator',
            'version': '1.0',
            'framework': 'Flask'
        }), 200

else:
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class StandaloneAPIHandler(BaseHTTPRequestHandler):
        def _send_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        def do_OPTIONS(self):
            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()

        def do_GET(self):
            global last_result, last_config
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            
            resp = {
                'api': 'Motor Control Simulator',
                'version': '1.0',
                'framework': 'standard http.server (zero-dependency)',
                'status': 'running'
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))

        def do_POST(self):
            global last_result, last_config
            if self.path.startswith('/api/simulate'):
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length) if content_length > 0 else b'{}'
                    data = json.loads(body.decode('utf-8')) if body else {}

                    config = SimConfig(
                        rpm_target=float(data.get('rpm_target', 3000)),
                        duration_s=float(data.get('duration_s', 2.0)),
                        kp=float(data.get('kp', 0.3)),
                        ki=float(data.get('ki', 0.03)),
                        kd=float(data.get('kd', 0.01)),
                        load_torque=float(data.get('load_torque', 0.0))
                    )

                    start_time = time.time()
                    states, summary = run_simulation(config)
                    elapsed = time.time() - start_time

                    last_result = {'states': states, 'summary': summary}
                    last_config = config

                    resp = {
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
                    }

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps(resp).encode('utf-8'))
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

def run_server(port=5000):
    if HAS_FLASK:
        app.run(host='127.0.0.1', port=port, debug=False)
    else:
        server = HTTPServer(('127.0.0.1', port), StandaloneAPIHandler)
        print(f"Server running on http://127.0.0.1:{port}")
        server.serve_forever()

if __name__ == '__main__':
    run_server(5000)

