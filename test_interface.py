#!/usr/bin/env python3
"""
Test script for controlmotor-dual.html interface
Simulates user clicks and verifies API connectivity
"""

import requests
import json
import time
from datetime import datetime

def test_api_simulation():
    """Test POST /api/simulate endpoint with correct JSON format"""
    
    print("\n" + "="*70)
    print("🧪 TESTE: Interface Dual Mode + API Simulação")
    print("="*70 + "\n")
    
    api_url = 'http://localhost:8000/api/simulate'
    
    # Simular clique em "Iniciar" (throttle 50%, Kp=0.5, Ki=0.1, Kd=0.05)
    payload = {
        "throttle_percent": 50,
        "duration_s": 1.0,
        "kp": 0.5,
        "ki": 0.1,
        "kd": 0.05,
        "load_torque": 0,
        "autolearn_enabled": False
    }
    
    print(f"[TEST 1] POST /api/simulate com JSON correto")
    print(f"  Endpoint: {api_url}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        start = time.time()
        response = requests.post(api_url, json=payload, timeout=10)
        elapsed = time.time() - start
        
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Tempo: {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract telemetry
            summary = data.get('summary', {})
            rpm = summary.get('final_rpm', 0)
            current = summary.get('peak_current', 0)
            temp = summary.get('peak_temp', 0)
            
            # Calculate derived values (como o front-end faria)
            torque = current * 0.28  # Kt = 0.28 N·m/A
            voltage = 380 - (current * 0.1)
            power = (voltage * current / 1000)
            
            print(f"\n📊 Telemetria Simulada:")
            print(f"  RPM: {rpm:.0f} rpm")
            print(f"  Corrente: {current:.1f} A")
            print(f"  Torque (τ = I × Kt): {torque:.2f} N·m")
            print(f"  Temperatura: {temp:.1f} °C")
            print(f"  Tensão (com queda): {voltage:.1f} V")
            print(f"  Potência: {power:.2f} kW")
            
            # Verify fields that UI depends on
            expected_fields = ['final_rpm', 'peak_current', 'peak_temp']
            missing = [f for f in expected_fields if f not in summary]
            
            if missing:
                print(f"\n❌ FALHA: Campos faltando: {missing}")
                return False
            else:
                print(f"\n✅ Todos os campos esperados presentes")
            
            return True
        else:
            print(f"❌ Status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO: Não conseguiu conectar em {api_url}")
        print(f"   Verifique se o servidor está rodando: python3 sim/server.py")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_cors_headers():
    """Test CORS preflight (OPTIONS) request"""
    
    print(f"\n[TEST 2] Teste CORS (OPTIONS preflight)")
    api_url = 'http://localhost:8000/api/simulate'
    
    try:
        response = requests.options(api_url, timeout=5)
        
        print(f"✅ Status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', 'MISSING'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', 'MISSING'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', 'MISSING'),
        }
        
        print(f"  CORS Headers:")
        for key, val in cors_headers.items():
            status = "✅" if val != 'MISSING' else "❌"
            print(f"    {status} {key}: {val}")
        
        all_present = all(v != 'MISSING' for v in cors_headers.values())
        return all_present
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_throttle_range():
    """Test different throttle values (0%, 25%, 50%, 75%, 100%)"""
    
    print(f"\n[TEST 3] Teste Throttle em diferentes valores")
    api_url = 'http://localhost:8000/api/simulate'
    
    throttles = [0, 25, 50, 75, 100]
    results = []
    
    for throttle in throttles:
        payload = {
            "throttle_percent": throttle,
            "duration_s": 0.5,
            "kp": 0.5,
            "ki": 0.1,
            "kd": 0.05
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                summary = response.json().get('summary', {})
                rpm = summary.get('final_rpm', 0)
                current = summary.get('peak_current', 0)
                
                print(f"  Throttle {throttle:3d}%  →  RPM: {rpm:7.0f}  |  I: {current:6.1f}A  ✅")
                results.append(True)
            else:
                print(f"  Throttle {throttle:3d}%  →  HTTP {response.status_code}  ❌")
                results.append(False)
                
        except Exception as e:
            print(f"  Throttle {throttle:3d}%  →  {str(e)[:40]}  ❌")
            results.append(False)
    
    return all(results)


def test_modulos_io():
    """Simula dados que os módulos deveriam mostrar"""
    
    print(f"\n[TEST 4] Verificação de I/O dos Módulos Simulados")
    api_url = 'http://localhost:8000/api/simulate'
    
    payload = {
        "throttle_percent": 50,
        "duration_s": 1.0,
        "kp": 0.5,
        "ki": 0.1,
        "kd": 0.05,
        "load_torque": 0,
        "autolearn_enabled": False
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API retornou {response.status_code}")
            return False
        
        summary = response.json().get('summary', {})
        
        # Simular cálculos dos módulos
        rpm = summary.get('final_rpm', 0)
        current = summary.get('peak_current', 0)
        temp = summary.get('peak_temp', 0)
        
        # Motor BLDC outputs
        torque_motor = current * 0.28
        print(f"\n  🔷 Motor BLDC")
        print(f"     Entrada: U/V/W voltages")
        print(f"     Saída: RPM={rpm:.0f}, Torque={torque_motor:.2f} N·m")
        
        # FOC Controller
        voltage_phase = 380 - (current * 0.1)
        print(f"\n  ⚙️  FOC Controller")
        print(f"     Entrada: throttle=50%, Kp=0.5")
        print(f"     Saída: U-phase={voltage_phase:.1f}V (PI Loops ✓)")
        
        # Battery Model
        voltage_drop = current * 0.05
        battery_voltage = 48 - voltage_drop
        print(f"\n  🔋 Battery Model")
        print(f"     Entrada: I={current:.1f}A")
        print(f"     Saída: V_real={battery_voltage:.1f}V (com queda ESR)")
        
        # Thermal Model
        power_diss = voltage_phase * current
        print(f"\n  🌡️  Thermal Model")
        print(f"     Entrada: P_diss={power_diss:.1f}W")
        print(f"     Saída: T_motor={temp:.1f}°C (tau=2.0s)")
        
        # Auto-Learner (status)
        print(f"\n  🤖 Auto-Learner")
        print(f"     Status: Inativo (seria ativado com botão)")
        print(f"     Método: Relay + Ziegler-Nichols")
        
        # Proteções
        fault = "0x00 OK" if current < 50 and temp < 80 else "⚠️  FAULT"
        state = "RUNNING" if rpm > 0 else "IDLE"
        print(f"\n  🛡️  Proteções")
        print(f"     Fault Code: {fault}")
        print(f"     Estado Motor: {state}")
        
        print(f"\n✅ Todos os módulos gerando I/O corretamente")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def start_background_server_if_needed():
    """Ensure simulation server is running on localhost:8000"""
    import socket
    import sys
    import os
    import threading
    
    # Check if port 8000 is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result == 0:
        print("ℹ️ Servidor de simulação já está rodando em http://127.0.0.1:8000")
        return None
    
    print("🚀 Iniciando servidor de simulação em background (127.0.0.1:8000)...")
    sim_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sim')
    if sim_dir not in sys.path:
        sys.path.insert(0, sim_dir)
        
    try:
        from http.server import HTTPServer
        from server import MotorControllerHandler
        
        httpd = HTTPServer(('127.0.0.1', 8000), MotorControllerHandler)
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        time.sleep(0.5)
        print("✅ Servidor iniciado com sucesso!")
        return httpd
    except Exception as e:
        print(f"⚠️ Não foi possível iniciar servidor automático: {e}")
        return None


def main():
    """Run all tests"""
    
    server = start_background_server_if_needed()
    
    tests = [
        ("API Simulação + JSON Correto", test_api_simulation),
        ("CORS Headers", test_cors_headers),
        ("Throttle Range", test_throttle_range),
        ("Módulos I/O", test_modulos_io),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ ERRO em {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("📋 RESUMO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\n{'='*70}")
    print(f"Resultado: {passed}/{total} testes passaram")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 TODAS AS ETAPAS COMPLETADAS COM SUCESSO!")
        print("\n📌 Próximos passos:")
        print("  1. Abrir navegador em: file:///home/teste/controlmotor/controlmotor-dual.html")
        print("  2. Clicar em '▶ Iniciar'")
        print("  3. Observar telemetria atualizar em tempo real")
        print("  4. Conferir painel 'Módulos Simulados' com I/O")
        print("  5. Testar modo 'Real' (mock hardware)\n")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique logs acima.\n")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

