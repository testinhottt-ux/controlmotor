#!/usr/bin/env python3
"""
Complete test for MotorControl Web Interface v2.0
Tests: Multiple Motors, Batteries, Auto-Learning (improved)
"""

import requests
import json
import time
import socket
import threading
from sim.server import MotorControllerHandler
from http.server import HTTPServer

def is_server_running(host='127.0.0.1', port=8000):
    try:
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        return True
    except OSError:
        return False

def start_background_server_if_needed():
    if not is_server_running():
        print("🚀 Iniciando servidor de simulação em background (127.0.0.1:8000)...")
        server = HTTPServer(('127.0.0.1', 8000), MotorControllerHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.5)
        print("✅ Servidor iniciado com sucesso!\n")

start_background_server_if_needed()

API_URL = 'http://127.0.0.1:8000/api/simulate'
MOTORS_URL = 'http://127.0.0.1:8000/api/motors'
BATTERIES_URL = 'http://127.0.0.1:8000/api/batteries'

print("\n" + "="*70)
print("🧪 TESTE COMPLETO: MotorControl v2.0 (Multi-Motor + Multi-Battery)")
print("="*70 + "\n")

# TEST 1: List Motors
print("[TEST 1] Listar Motores Disponíveis")
try:
    resp = requests.get(MOTORS_URL, timeout=5)
    motors = resp.json()['motors']
    print("✅ Motores disponíveis:")
    for key, name in motors.items():
        print(f"   - {key}: {name}")
except Exception as e:
    print(f"❌ Erro: {e}")

print()

# TEST 2: List Batteries
print("[TEST 2] Listar Baterias Disponíveis")
try:
    resp = requests.get(BATTERIES_URL, timeout=5)
    batteries = resp.json()['batteries']
    print("✅ Baterias disponíveis:")
    for key, name in batteries.items():
        print(f"   - {key}: {name}")
except Exception as e:
    print(f"❌ Erro: {e}")

print()

# TEST 3: Simulate with Different Motors
print("[TEST 3] Simulação com Diferentes Motores (mesma bateria)")
motor_types = ['small', 'medium', 'large']

for motor in motor_types:
    try:
        payload = {
            "throttle_percent": 50,
            "duration_s": 0.5,
            "kp": 0.5,
            "ki": 0.1,
            "kd": 0.05,
            "motor_type": motor,
            "battery_type": "lipo"
        }
        
        start = time.time()
        resp = requests.post(API_URL, json=payload, timeout=10)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            motor_info = data['motor']
            summary = data['summary']
            print(f"✅ {motor_info['name']:20s} | RPM: {summary['final_rpm']:7.0f} | I: {summary['peak_current']:6.1f}A | T: {elapsed:5.2f}s")
        else:
            print(f"❌ Motor {motor}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Motor {motor}: {str(e)[:50]}")

print()

# TEST 4: Simulate with Different Batteries
print("[TEST 4] Simulação com Diferentes Baterias (mesmo motor)")
battery_types = ['lipo', 'lifepo4', 'lead-acid']

for battery in battery_types:
    try:
        payload = {
            "throttle_percent": 75,
            "duration_s": 0.5,
            "kp": 0.5,
            "ki": 0.1,
            "kd": 0.05,
            "motor_type": "medium",
            "battery_type": battery
        }
        
        start = time.time()
        resp = requests.post(API_URL, json=payload, timeout=10)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            batt_info = data['battery']
            summary = data['summary']
            print(f"✅ {batt_info['name']:25s} | Max I: {batt_info['max_current_a']:3.0f}A | RPM: {summary['final_rpm']:7.0f} | T: {elapsed:5.2f}s")
        else:
            print(f"❌ Battery {battery}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Battery {battery}: {str(e)[:50]}")

print()

# TEST 5: Auto-Learning Improved
print("[TEST 5] Auto-Learning Melhorado (Relay com Histerese)")
try:
    payload = {
        "throttle_percent": 50,
        "duration_s": 1.5,  # Mais tempo para auto-learning
        "kp": 0.3,
        "ki": 0.03,
        "kd": 0.01,
        "autolearn_enabled": True,
        "autolearn_duration_s": 1.0,
        "motor_type": "medium",
        "battery_type": "lipo"
    }
    
    print("  Rodando auto-learning por 1.5s (relay ativa por 1.0s)...")
    start = time.time()
    resp = requests.post(API_URL, json=payload, timeout=15)
    elapsed = time.time() - start
    
    if resp.status_code == 200:
        data = resp.json()
        summary = data['summary']
        
        print(f"\n✅ Auto-Learning Completo!")
        print(f"  Final RPM: {summary['final_rpm']:.0f}")
        print(f"  Peak Current: {summary['peak_current']:.1f}A")
        print(f"  Converged: {summary['converged']}")
        print(f"  Tuned Kp: {summary['final_kp']:.4f}")
        print(f"  Tuned Ki: {summary['final_ki']:.4f}")
        print(f"  Tuned Kd: {summary['final_kd']:.4f}")
        print(f"  Tempo total: {elapsed:.2f}s")
    else:
        print(f"❌ HTTP {resp.status_code}")
except Exception as e:
    print(f"❌ Erro: {str(e)[:80]}")

print()

# TEST 6: Throttle Range with Best Motor+Battery
print("[TEST 6] Teste de Throttle (0%, 25%, 50%, 75%, 100%) - Large Motor + LiFePO4")
throttles = [0, 25, 50, 75, 100]

for throttle in throttles:
    try:
        payload = {
            "throttle_percent": throttle,
            "duration_s": 0.3,
            "kp": 0.5,
            "ki": 0.1,
            "kd": 0.05,
            "motor_type": "large",
            "battery_type": "lifepo4"
        }
        
        start = time.time()
        resp = requests.post(API_URL, json=payload, timeout=10)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            summary = resp.json()['summary']
            rpm = summary['final_rpm']
            current = summary['peak_current']
            print(f"  Throttle {throttle:3d}%  →  RPM: {rpm:7.0f}  |  I: {current:6.1f}A  ✅")
        else:
            print(f"  Throttle {throttle:3d}%  →  HTTP {resp.status_code}  ❌")
    except Exception as e:
        print(f"  Throttle {throttle:3d}%  →  {str(e)[:40]}  ❌")

print()
print("="*70)
print("✅ TODOS OS TESTES CONCLUÍDOS!")
print("="*70 + "\n")

print("📌 Próximos passos:")
print("  1. Abrir navegador: file:///home/teste/controlmotor/controlmotor-dual.html")
print("  2. Testar dropdowns: Motor (Small/Medium/Large)")
print("  3. Testar dropdowns: Battery (LiPo/LiFePO4/Lead-Acid)")
print("  4. Clicar '▶ Iniciar' e observar RPM não travar")
print("  5. Clicar '🤖 Auto-Learn' e observar oscilações\n")
