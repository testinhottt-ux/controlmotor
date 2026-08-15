#!/usr/bin/env python3
"""
Motor Controller Web Server with Multi-Motor & Multi-Battery Support
Simple HTTP server (no dependencies) for parameter injection
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from bldc_full_simulator import SimConfig, run_simulation
from motor_models import MotorCatalog, BatteryCatalog
import threading
import time

class MotorControllerHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for motor simulation API"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """GET / — Show API documentation"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html = """<!DOCTYPE html>
<html>
<head>
    <title>Motor Controller API</title>
    <style>
        body { font-family: monospace; margin: 20px; }
        .endpoint { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
        pre { background: #222; color: #0f0; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🚗 Motor Controller Simulator API</h1>
    
    <h2>Available Endpoints</h2>
    
    <div class="endpoint">
        <h3>POST /api/simulate</h3>
        <p>Run single simulation with injected parameters</p>
        <pre>{
  "throttle_percent": 50,      # 0-100 (accelerator pedal)
  "duration_s": 3.0,           # simulation time
  "kp": 0.5,                   # P gain (0.01-5)
  "ki": 0.05,                  # I gain (0.001-1)
  "kd": 0.02,                  # D gain (0.001-0.5)
  "load_torque": 0.5,          # N·m (0-2)
  "autolearn_enabled": true,   # enable auto-tuning
  "autolearn_duration_s": 1.0, # tuning time
  "ambient_temp_c": 25         # °C (0-100)
}</pre>
        <p><strong>Example:</strong></p>
        <pre>curl -X POST http://localhost:8000/api/simulate \\
  -H "Content-Type: application/json" \\
  -d '{
    "throttle_percent": 75,
    "kp": 0.5,
    "load_torque": 0.5
  }'</pre>
    </div>
    
    <div class="endpoint">
        <h3>GET /api/status</h3>
        <p>Get server status and last simulation results</p>
        <pre>curl http://localhost:8000/api/status</pre>
    </div>
    
    <div class="endpoint">
        <h3>POST /api/simulate_batch</h3>
        <p>Run multiple simulations in sequence</p>
        <pre>{
  "simulations": [
    {"throttle_percent": 25, "kp": 0.3},
    {"throttle_percent": 50, "kp": 0.5},
    {"throttle_percent": 75, "kp": 0.7}
  ]
}</pre>
    </div>
    
    <h2>Response Format</h2>
    <pre>{
  "status": "success",
  "config": {
    "throttle_percent": 50,
    "kp": 0.5,
    "...": "..."
  },
  "summary": {
    "final_rpm": 3999.3,
    "target_rpm": 4000,
    "error_percent": 0.02,
    "converged": true,
    "peak_current": 45.2,
    "peak_temp": 42.1,
    "final_kp": 0.5,
    "final_ki": 0.05,
    "final_kd": 0.02
  }
}</pre>

    <h2>Test Examples</h2>
    <h3>1. Basic Throttle Test (50%)</h3>
    <pre>curl -X POST http://localhost:8000/api/simulate -H "Content-Type: application/json" -d '{
  "throttle_percent": 50,
  "duration_s": 2.0
}'</pre>

    <h3>2. With Auto-Learning</h3>
    <pre>curl -X POST http://localhost:8000/api/simulate -H "Content-Type: application/json" -d '{
  "throttle_percent": 50,
  "duration_s": 3.0,
  "autolearn_enabled": true,
  "autolearn_duration_s": 1.0
}'</pre>

    <h3>3. With Custom Gains + Load</h3>
    <pre>curl -X POST http://localhost:8000/api/simulate -H "Content-Type: application/json" -d '{
  "throttle_percent": 75,
  "kp": 0.6,
  "ki": 0.06,
  "kd": 0.03,
  "load_torque": 0.8,
  "duration_s": 2.5
}'</pre>

    <h3>4. Batch Test (Multiple RPMs)</h3>
    <pre>curl -X POST http://localhost:8000/api/simulate_batch -H "Content-Type: application/json" -d '{
  "simulations": [
    {"throttle_percent": 25, "kp": 0.3},
    {"throttle_percent": 50, "kp": 0.5},
    {"throttle_percent": 75, "kp": 0.7},
    {"throttle_percent": 100, "kp": 0.8}
  ]
}'</pre>

    <hr>
    <p><strong>Server Status:</strong> <span style="color: green;">✓ Running</span></p>
</body>
</html>"""
            self.wfile.write(html.encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'running',
                'server': 'Motor Controller Simulator',
                'version': '2.0',
                'endpoints': [
                    'GET  /',
                    'GET  /api/status',
                    'GET  /api/motors',
                    'GET  /api/batteries',
                    'POST /api/simulate',
                    'POST /api/simulate_batch'
                ]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif self.path == '/api/motors':
            """List available motors"""
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            motors = MotorCatalog.list_all()
            response = {'status': 'success', 'motors': motors}
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif self.path == '/api/batteries':
            """List available batteries"""
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            batteries = BatteryCatalog.list_all()
            response = {'status': 'success', 'batteries': batteries}
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif self.path == '/api/profile':
            """GET saved tuning profile (persisted like EEPROM on firmware)"""
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            profile = _load_profile()
            self.wfile.write(json.dumps({'status': 'success', 'profile': profile}, indent=2).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """POST requests — run simulations"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
            return
        
        if self.path == '/api/simulate':
            self._handle_simulate(data)
        elif self.path == '/api/simulate_batch':
            self._handle_batch(data)
        elif self.path == '/api/profile':
            self._handle_save_profile(data)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_simulate(self, params):
        """Handle single simulation request"""
        try:
            # Get motor and battery types
            motor_type = params.get('motor_type', 'medium').lower()
            battery_type = params.get('battery_type', 'lipo').lower()
            
            # Validate and get specs
            try:
                motor_spec = MotorCatalog.get_by_name(motor_type)
                battery_spec = BatteryCatalog.get_by_name(battery_type)
            except:
                motor_spec = MotorCatalog.MEDIUM_BLDC
                battery_spec = BatteryCatalog.LIPO_48V
            
            # Get motor inertia for adaptive control scaling
            motor_inertia = motor_spec.inertia_kg_m2
            
            # Optional throttle profile [(t_s, %), ...] for regen / release-pedal tests
            throttle_profile = None
            if params.get('throttle_profile'):
                try:
                    throttle_profile = [(float(a), float(b)) for a, b in params['throttle_profile']]
                except Exception:
                    throttle_profile = None
            
            config = SimConfig(
                throttle_percent=float(params.get('throttle_percent', 50)),
                throttle_profile=throttle_profile,
                duration_s=float(params.get('duration_s', 0.5)),
                kp=float(params.get('kp', 0.3)),
                ki=float(params.get('ki', 0.03)),
                kd=float(params.get('kd', 0.01)),
                rpm_target=float(params.get('rpm_target', 3000)),
                load_torque=float(params.get('load_torque', 0.0)),
                motor_brake=bool(params.get('motor_brake', True)),
                autolearn_enabled=bool(params.get('autolearn_enabled', False)),
                autolearn_duration_s=float(params.get('autolearn_duration_s', 2.0)),
                ambient_temp_c=float(params.get('ambient_temp_c', 25)),
                motor_inertia_kg_m2=motor_inertia,  # Auto-adapt PID gains to motor size
                battery_capacity_ah=battery_spec.capacity_ah,
                battery_nominal_v=battery_spec.nominal_voltage_v,
                battery_internal_resistance=battery_spec.internal_resistance_ohm,
                battery_efficiency=battery_spec.efficiency_percent,
                battery_soc_init=float(params.get('battery_soc_init', 0.85))
            )
            
            # Validate
            if not (0 <= config.throttle_percent <= 100):
                raise ValueError('throttle_percent must be 0-100')
            if not (0.01 <= config.kp <= 5):
                raise ValueError('kp must be 0.01-5')
            if not (0.1 <= config.duration_s <= 10):
                raise ValueError('duration_s must be 0.1-10')
            
            print(f"[SIMULATE] Motor={motor_spec.name}, Battery={battery_spec.name}, Throttle={config.throttle_percent}%, AutoLearn={config.autolearn_enabled}")
            
            autolearn_requested = config.autolearn_enabled
            states, summary, autolearn_status = run_simulation(config)
            
            response = {
                'status': 'success',
                'config': {
                    'throttle_percent': config.throttle_percent,
                    'duration_s': config.duration_s,
                    'kp': config.kp,
                    'ki': config.ki,
                    'kd': config.kd,
                    'load_torque': config.load_torque,
                    'motor_brake': config.motor_brake,
                    'autolearn_enabled': config.autolearn_enabled,
                    'autolearn_duration_s': config.autolearn_duration_s,
                    'motor_type': motor_type,
                    'battery_type': battery_type
                },
                'motor': {
                    'name': motor_spec.name,
                    'power_w': motor_spec.power_rating_w,
                    'voltage_v': motor_spec.voltage_nominal_v,
                    'speed_max_rpm': motor_spec.speed_max_rpm,
                    'torque_nm': motor_spec.torque_rated_nm
                },
                'battery': {
                    'name': battery_spec.name,
                    'chemistry': battery_spec.chemistry,
                    'voltage_v': summary.get('battery_voltage', battery_spec.nominal_voltage_v),
                    'soc': round(summary.get('soc', 0.0) * 100, 1),
                    'capacity_ah': battery_spec.capacity_ah,
                    'max_current_a': battery_spec.max_discharge_current_a,
                    'regen_power_max': round(summary.get('regen_power_max', 0.0), 1),
                    'regen_energy_wh': round(summary.get('regen_energy_wh', 0.0), 3)
                },
                'summary': summary,
                'num_samples': len(states),
                'states': states  # Include historical data for charting
            }
            
            # Add auto-learn status if available
            if autolearn_requested and autolearn_status:
                response['autolearn_status'] = autolearn_status
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"[ERROR] {e}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode())
    
    def _handle_batch(self, params):
        """Handle batch simulation request"""
        try:
            sims = params.get('simulations', [])
            
            if not sims or len(sims) > 10:
                raise ValueError('Provide 1-10 simulations')
            
            results = []
            for i, sim in enumerate(sims):
                config = SimConfig(
                    throttle_percent=float(sim.get('throttle_percent', 50)),
                    duration_s=float(sim.get('duration_s', 2.0)),
                    kp=float(sim.get('kp', 0.3)),
                    ki=float(sim.get('ki', 0.03)),
                    kd=float(sim.get('kd', 0.01))
                )
                
                print(f"[BATCH {i+1}/{len(sims)}] Throttle={config.throttle_percent}%, Kp={config.kp}")
                
                _, summary, _ = run_simulation(config)
                results.append({
                    'config': {
                        'throttle_percent': config.throttle_percent,
                        'kp': config.kp
                    },
                    'summary': summary
                })
            
            response = {
                'status': 'success',
                'num_simulations': len(results),
                'results': results
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        except Exception as e:
            print(f"[ERROR] {e}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode())
    
    def _handle_save_profile(self, params):
        """Save tuning profile (mirrors firmware EEPROM save)"""
        try:
            profile = _save_profile(params)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'profile': profile}, indent=2).encode())
        except Exception as e:
            print(f"[ERROR] {e}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[HTTP] {self.address_string()} - {format % args}")

def run_server(port=8000):
    """Start the HTTP server"""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, MotorControllerHandler)
    
    print("=" * 70)
    print("🚗 MOTOR CONTROLLER SIMULATOR - HTTP SERVER")
    print("=" * 70)
    print(f"Server running on http://127.0.0.1:{port}")
    print(f"Open browser or use curl to test API")
    print()
    print("Examples:")
    print(f"  - View API docs:  http://127.0.0.1:{port}/")
    print(f"  - Check status:   curl http://127.0.0.1:{port}/api/status")
    print(f"  - Run simulation: curl -X POST http://127.0.0.1:{port}/api/simulate \\")
    print(f"                      -H 'Content-Type: application/json' \\")
    print(f"                      -d '{{\"throttle_percent\": 75, \"kp\": 0.5}}'")
    print()
    print("Press Ctrl+C to stop server")
    print("=" * 70)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server stopped")
        sys.exit(0)

PROFILE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile.json')

def _load_profile():
    """Load saved tuning profile (like firmware EEPROM load)"""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[PROFILE] erro ao ler: {e}")
    return {}

def _save_profile(data):
    """Save tuning profile to disk (like firmware EEPROM save)"""
    allowed = ['kp', 'ki', 'kd', 'rpm_target', 'auto_learn_duration_s',
               'motor_type', 'battery_type', 'saved_at']
    profile = {k: v for k, v in data.items() if k in allowed}
    profile['saved_at'] = data.get('saved_at', '') or ''
    try:
        with open(PROFILE_FILE, 'w') as f:
            json.dump(profile, f, indent=2)
        print(f"[PROFILE] salvo: {profile}")
    except Exception as e:
        print(f"[PROFILE] erro ao salvar: {e}")
    return profile

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
