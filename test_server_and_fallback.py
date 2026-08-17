#!/usr/bin/env python3
"""
test_server_and_fallback.py
Verifica:
1. sim/server.py respondendo na raiz '/' servindo controlmotor-dual.html
2. sim/server.py respondendo em '/controlmotor-dual.html'
3. sim/server.py servindo arquivos estáticos SVG
4. Fallback offline no browser quando o servidor está desligado
"""

import subprocess
import time
import requests
from playwright.sync_api import sync_playwright

def test_server_routes():
    print("\n[TEST 1] Verificando rotas e arquivos estáticos em sim/server.py...")
    proc = subprocess.Popen(["python3", "sim/server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.2)

    try:
        # 1. Rota raiz '/'
        r_root = requests.get("http://localhost:8000/")
        assert r_root.status_code == 200, f"Erro na raiz /: {r_root.status_code}"
        assert "<!DOCTYPE html>" in r_root.text, "Raiz não retornou o HTML do dashboard"
        assert "MotorControl Dual" in r_root.text, "Título MotorControl Dual ausente"
        print("  ✓ Rota raiz '/' servindo controlmotor-dual.html com sucesso!")

        # 2. Rota '/controlmotor-dual.html'
        r_html = requests.get("http://localhost:8000/controlmotor-dual.html")
        assert r_html.status_code == 200, f"Erro em /controlmotor-dual.html: {r_html.status_code}"
        print("  ✓ Rota '/controlmotor-dual.html' servindo o HTML com status 200!")

        # 3. Rota de arquivo estático SVG
        r_svg = requests.get("http://localhost:8000/esquema_profissional.svg")
        assert r_svg.status_code == 200, f"Erro no SVG: {r_svg.status_code}"
        assert "<svg" in r_svg.text, "Arquivo SVG não é válido"
        assert r_svg.headers.get("Content-Type") == "image/svg+xml", f"MIME type incorreto: {r_svg.headers.get('Content-Type')}"
        print("  ✓ Rota de arquivos estáticos SVG servindo esquema_profissional.svg com MIME image/svg+xml!")

        # 4. Rota '/api/status'
        r_status = requests.get("http://localhost:8000/api/status")
        assert r_status.status_code == 200
        json_data = r_status.json()
        assert json_data.get("status") == "running"
        print("  ✓ Rota '/api/status' operacional!")

    finally:
        proc.terminate()

def test_offline_fallback_in_browser():
    print("\n[TEST 2] Verificando fallback de demonstração local no navegador...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium')
        page = browser.new_page(viewport={'width': 1600, 'height': 1000})

        # Abrir o arquivo localmente sem servidor rodando (simulando offline total)
        file_url = "file:///home/teste/controlmotor/controlmotor-dual.html"
        page.goto(file_url, wait_until='domcontentloaded')
        page.wait_for_timeout(500)

        # Mover acelerador para 40%
        page.fill("#throttleSim", "40")
        page.dispatch_event("#throttleSim", "input")
        page.wait_for_timeout(1000)

        rpm = page.inner_text("#simRpm")
        current = page.inner_text("#simCurrent")
        voltage = page.inner_text("#simVoltage")
        power = page.inner_text("#simPower")

        print(f"  [Offline Demo Fallback] Acelerador 40% → RPM: {rpm} rpm | I: {current} A | V: {voltage} V | P: {power} kW")
        assert float(rpm) > 0, "Fallback local não calculou RPM"
        assert float(current) > 0, "Fallback local não calculou Corrente"
        print("  ✓ Fallback de demonstração offline 100% funcional!")

        browser.close()

def main():
    print("================================================================================")
    print("🚀 TESTANDO SERVIDOR HTTP sim/server.py E FALLBACK DE DEMONSTRAÇÃO OFFLINE")
    print("================================================================================")
    test_server_routes()
    test_offline_fallback_in_browser()
    print("\n================================================================================")
    print("🏆 RESULTADO: 100% DOS TESTES APROVADOS!")
    print("================================================================================")

if __name__ == '__main__':
    main()
