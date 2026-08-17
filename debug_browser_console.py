#!/usr/bin/env python3
"""
debug_browser_console.py
Executa o navegador real via Playwright para capturar todos os logs, erros JS e testar a reação do acelerador.
"""

import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8095

def start_server():
    server = HTTPServer(('127.0.0.1', PORT), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

def test_browser():
    server = start_server()
    time.sleep(0.5)
    url = f"http://127.0.0.1:{PORT}/controlmotor-dual.html"

    console_logs = []
    page_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium')
        page = browser.new_page()

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(f"{err}\n{getattr(err, 'stack', '')}"))

        print(f"🌐 Navegando para {url}...")
        page.goto(url)
        page.wait_for_timeout(1000)

        print("\n--- ERROS INICIAIS DA PÁGINA ---")
        print(f"Page errors: {page_errors}")
        print(f"Console logs: {console_logs[:10]}")

        # Inspecionar estado inicial dos elementos
        rpm_init = page.inner_text("#simRpm")
        cur_init = page.inner_text("#simCurrent")
        volt_init = page.inner_text("#simVoltage")
        print(f"\n[ESTADO INICIAL] RPM: '{rpm_init}', Corrente: '{cur_init}', Tensão: '{volt_init}'")

        for pct in [0, 25, 50, 75, 100, 0]:
            print(f"\n🏎️ Movendo acelerador #throttleSim para {pct}%...")
            page.fill("#throttleSim", str(pct))
            page.dispatch_event("#throttleSim", "input")
            page.wait_for_timeout(800)

            # Inspecionar estado após mover acelerador
            rpm = page.inner_text("#simRpm")
            target = page.inner_text("#simRpmTarget")
            cur = page.inner_text("#simCurrent")
            volt = page.inner_text("#simVoltage")
            torq = page.inner_text("#simTorque")
            temp = page.inner_text("#simTemp")
            pow_kw = page.inner_text("#simPower")
            err_pct = page.inner_text("#simErrorPct")

            print(f"  [Throttle {pct}%] RPM: {rpm} / {target} rpm | I: {cur} A | Torque: {torq} N·m | V: {volt} V | T: {temp} °C | P: {pow_kw} kW | Erro: {err_pct}%")

        print("\n🔌 Alternando para Modo Hardware Real...")
        page.click("#btnReal")
        page.wait_for_timeout(500)

        for pct in [0, 30, 80, 0]:
            print(f"🏎️ Movendo acelerador #throttleReal para {pct}%...")
            page.fill("#throttleReal", str(pct))
            page.dispatch_event("#throttleReal", "input")
            page.wait_for_timeout(600)

            rpm = page.inner_text("#realRpm")
            cur = page.inner_text("#realCurrent")
            torq = page.inner_text("#realTorque")
            volt = page.inner_text("#realVoltage")
            temp = page.inner_text("#realTemp")
            pow_kw = page.inner_text("#realPower")

            print(f"  [Real Throttle {pct}%] RPM: {rpm} rpm | I: {cur} A | Torque: {torq} N·m | V: {volt} V | T: {temp} °C | P: {pow_kw} kW")

        print("\n--- TODOS OS ERROS APÓS AÇÃO ---")
        print(f"Page errors ({len(page_errors)}): {page_errors}")

        browser.close()

if __name__ == '__main__':
    test_browser()
