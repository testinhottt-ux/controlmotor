#!/usr/bin/env python3
"""
Motor Controller Web Server with Multi-Motor & Multi-Battery Support
Simple HTTP server (no dependencies) for parameter injection
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Garantir que o diretório sim/ esteja no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bldc_full_simulator import SimConfig, run_simulation
    from motor_models import MotorCatalog, BatteryCatalog
except ImportError:
    from sim.bldc_full_simulator import SimConfig, run_simulation
    from sim.motor_models import MotorCatalog, BatteryCatalog

import threading
import time

class MotorControllerHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for motor simulation API"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_HEAD(self):
        """Handle HEAD requests like GET"""
        self.do_GET()
    
    def do_GET(self):
        """GET request handler — serve HTML dashboard, API endpoints, and static files"""
        clean_path = self.path.split('?')[0]
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if clean_path in ['/', '/index.html', '/controlmotor-dual.html']:
            html_path = os.path.join(project_root, 'controlmotor-dual.html')
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(html_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        if clean_path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'running',
                'server': 'Motor Controller Simulator & Dashboard Server',
                'version': '4.0',
                'endpoints': [
                    'GET  / (Dashboard Web UI)',
                    'GET  /controlmotor-dual.html',
                    'GET  /api/status',
                    'GET  /api/motors',
                    'GET  /api/batteries',
                    'GET  /api/profile',
                    'POST /api/simulate',
                    'POST /api/simulate_batch'
                ]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
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
            
        # Arquivos estáticos (SVG, PNG, JS, CSS, HTML, CSV)
        rel_path = clean_path.lstrip('/')
        safe_path = os.path.normpath(os.path.join(project_root, rel_path))
        if safe_path.startswith(project_root) and os.path.isfile(safe_path):
            ext = os.path.splitext(safe_path)[1].lower()
            mime_types = {
                '.html': 'text/html; charset=utf-8',
                '.svg': 'image/svg+xml',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.json': 'application/json',
                '.csv': 'text/csv'
            }
            content_type = mime_types.get(ext, 'application/octet-stream')
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(safe_path, 'rb') as f:
                self.wfile.write(f.read())
            return

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
    server_address = ('0.0.0.0', port)
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
