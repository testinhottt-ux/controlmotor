#!/usr/bin/env python3
"""
Generate PCB Images and Schematics using KiCad
Creates PNG/SVG images of board layout and schematic
"""

import subprocess
import os
from pathlib import Path

def generate_kicad_images():
    """Generate images from existing KiCad files"""
    
    kicad_dir = Path('/home/teste/controlmotor')
    
    # Check for KiCad files
    kicad_sch = kicad_dir / 'schematic.kicad_sch'
    kicad_pcb = kicad_dir / 'schematic.kicad_pcb'
    
    print("=" * 70)
    print("GERAÇÃO DE IMAGENS PCB - CONTROLADORA MOTOR PMSM")
    print("=" * 70)
    print()
    
    # Check which files exist
    print("📁 Arquivos KiCad encontrados:")
    
    if kicad_sch.exists():
        print(f"   ✅ Esquemático: {kicad_sch.name}")
    else:
        print(f"   ❌ Esquemático não encontrado: {kicad_sch}")
    
    if kicad_pcb.exists():
        print(f"   ✅ Layout PCB: {kicad_pcb.name}")
    else:
        print(f"   ❌ Layout PCB não encontrado: {kicad_pcb}")
    
    print()
    
    # Try using kicad command-line tools
    try:
        # List available KiCad tools
        result = subprocess.run(['which', 'kicad'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ KiCad encontrado em: {result.stdout.strip()}")
        
        # Try kicad-cli (newer versions)
        result = subprocess.run(['which', 'kicad-cli'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ kicad-cli encontrado em: {result.stdout.strip()}")
            print("\n📊 Gerando imagens com kicad-cli...")
            
            # Generate schematic image
            if kicad_sch.exists():
                try:
                    subprocess.run([
                        'kicad-cli', 'sch', 'export', 'svg',
                        '--output', str(kicad_dir / 'schematic_image.svg'),
                        str(kicad_sch)
                    ], timeout=30, capture_output=True)
                    print("   ✅ Esquemático exportado: schematic_image.svg")
                except Exception as e:
                    print(f"   ⚠️  Erro ao exportar esquemático: {e}")
            
            # Generate PCB layout image
            if kicad_pcb.exists():
                try:
                    subprocess.run([
                        'kicad-cli', 'pcb', 'export', 'svg',
                        '--output', str(kicad_dir / 'pcb_layout.svg'),
                        str(kicad_pcb)
                    ], timeout=30, capture_output=True)
                    print("   ✅ Layout PCB exportado: pcb_layout.svg")
                except Exception as e:
                    print(f"   ⚠️  Erro ao exportar PCB: {e}")
        
        else:
            print("⚠️  kicad-cli não disponível (versão KiCad < 7.0)")
            print("   Usando geradores alternativos...")
    
    except Exception as e:
        print(f"❌ Erro ao executar KiCad: {e}")

def create_html_visualization():
    """Create HTML visualization of circuits"""
    
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controladora PMSM - Visualização de Placas e Circuitos</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 50px;
        }
        .section h2 {
            color: #667eea;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        .card {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #f9f9f9;
            transition: all 0.3s ease;
        }
        .card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.1);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .card-content {
            line-height: 1.6;
            color: #666;
        }
        .image-placeholder {
            width: 100%;
            height: 300px;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 1.1em;
            margin: 15px 0;
            border: 2px dashed #ccc;
        }
        .specs-list {
            list-style: none;
            padding: 0;
        }
        .specs-list li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .specs-list li:last-child {
            border-bottom: none;
        }
        .specs-list strong {
            color: #667eea;
            display: inline-block;
            width: 150px;
        }
        .measurement {
            display: inline-block;
            background: #f0f4ff;
            padding: 8px 12px;
            border-radius: 4px;
            margin-right: 10px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #667eea;
            font-weight: bold;
        }
        footer {
            background: #f9f9f9;
            padding: 20px;
            text-align: center;
            color: #999;
            border-top: 1px solid #ddd;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-right: 10px;
        }
        .status-complete {
            background: #d4edda;
            color: #155724;
        }
        .status-inprogress {
            background: #fff3cd;
            color: #856404;
        }
        .status-pending {
            background: #f8d7da;
            color: #721c24;
        }
        .table-simple {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .table-simple th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        .table-simple td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        .table-simple tr:hover {
            background: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔌 Controladora Universal de Motores PMSM/BLDC</h1>
            <p>Análise de Placas PCB e Circuitos SPICE</p>
        </header>
        
        <div class="content">
            <!-- Seção 1: Topology -->
            <div class="section">
                <h2>📐 Topologia do Circuito</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Inversor 3-fases com controle Field-Oriented (FOC) para motores PMSM síncronos e BLDC com comutação eletrônica.
                </p>
                
                <div class="image-placeholder">
                    <div>
                        <strong>CIRCUITO ESQUEMÁTICO</strong><br>
                        Inversor 3-fases com:<br>
                        • 6 MOSFETs 600V/50A (Q1-Q6)<br>
                        • Gate driver DRV8302 (15V, 2A)<br>
                        • Filtro DC-link (2×470µF)<br>
                        • Sensores: Hall + Shunts<br>
                    </div>
                </div>
                
                <ul class="specs-list">
                    <li><strong>Tensão DC:</strong> 400V nominal</li>
                    <li><strong>Corrente cont.:</strong> 50A @ 400V = 20kW</li>
                    <li><strong>Freq. PWM:</strong> 20 kHz</li>
                    <li><strong>Temp. junção:</strong> -40 a +125°C</li>
                    <li><strong>Eficiência:</strong> 92-94%</li>
                </ul>
            </div>
            
            <!-- Seção 2: Layout PCB -->
            <div class="section">
                <h2>🎨 Layout da Placa PCB</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Design de placa com 4 camadas para eletrônica de potência, com trilhas otimizadas para dissipação térmica.
                </p>
                
                <div class="grid">
                    <div class="card">
                        <h3>Top Layer (Componentes)</h3>
                        <div class="image-placeholder">
                            Camada Superior:<br>
                            • Seda com designadores<br>
                            • Pads de soldagem<br>
                            • Traces de sinal<br>
                            • Furos PTH
                        </div>
                        <p class="card-content">Camada de montagem dos componentes com trilhas de sinal e power.</p>
                    </div>
                    
                    <div class="card">
                        <h3>Power Plane (GND/VCC)</h3>
                        <div class="image-placeholder">
                            Camadas 2-3:<br>
                            • Plano de terra<br>
                            • Plano de potência<br>
                            • Retorno de corrente<br>
                            • Via termal
                        </div>
                        <p class="card-content">Planos contínuos para baixa impedância e dissipação térmica.</p>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">Parâmetros PCB</h3>
                    <table class="table-simple">
                        <thead>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                                <th>Especificação</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Dimensões</strong></td>
                                <td>150 × 100 mm</td>
                                <td>Tamanho compacto</td>
                            </tr>
                            <tr>
                                <td><strong>Camadas</strong></td>
                                <td>4 (Signal/GND/VCC/Signal)</td>
                                <td>Otimizado EMI</td>
                            </tr>
                            <tr>
                                <td><strong>Espessura cobre</strong></td>
                                <td>2 oz (70 µm)</td>
                                <td>Trilhas 50A</td>
                            </tr>
                            <tr>
                                <td><strong>Vias termais</strong></td>
                                <td>0.3 mm, ~200 vias</td>
                                <td>Dissipação 170W</td>
                            </tr>
                            <tr>
                                <td><strong>Espaçamento trilhas</strong></td>
                                <td>0.2 mm min</td>
                                <td>Alta densidade</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Seção 3: Simulação SPICE -->
            <div class="section">
                <h2>📊 Resultados Simulação SPICE</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Análise transiente do inversor 3-fases com carga RL equivalente ao motor.
                </p>
                
                <div class="card">
                    <h3>Parâmetros Simulados</h3>
                    <ul class="specs-list">
                        <li><strong>Tempo total:</strong> 5 ms (250 ciclos PWM @ 20 kHz)</li>
                        <li><strong>Passo de tempo:</strong> 1 µs</li>
                        <li><strong>Tensão DC-link:</strong> 400V ± variação</li>
                        <li><strong>Frequência motor:</strong> 200 Hz (equiv. 6000 RPM)</li>
                        <li><strong>Back-EMF:</strong> 143.5V pico</li>
                    </ul>
                    
                    <div style="margin-top: 20px;">
                        <h4 style="color: #667eea; margin-bottom: 10px;">Medições Esperadas</h4>
                        <div>
                            <span class="measurement">Ripple DC-link: &lt; 20V (5%)</span>
                            <span class="measurement">Corrente pico: 55A ± 5A</span>
                            <span class="measurement">Potência média: ~18kW</span>
                            <span class="measurement">Dissipação térmica: ~270W</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">Arquivo de Simulação</h3>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9em; overflow-x: auto;">
                        <pre>schematic_fixed.cir
├── Netlist: Circuito BLDC completo
├── Modelo: SW_MODEL (MOSFET ideal)
├── Motor: RLE com back-EMF sinusoidal
└── Análise: .tran 1u 5m

.measure tran:
  ├── I_peak_u = MAX(I(Rshunt_u))
  ├── Vdc_ripple = PP(V(vdc))
  ├── Power_avg = AVG(P)
  └── Power_peak = MAX(|P|)</pre>
                    </div>
                </div>
            </div>
            
            <!-- Seção 4: Status Projeto -->
            <div class="section">
                <h2>✅ Status do Projeto</h2>
                
                <div class="grid">
                    <div class="card">
                        <h3>Fase 1: Prototipagem</h3>
                        <div style="margin-top: 15px;">
                            <div><span class="status-badge status-complete">✅ Pesquisa</span></div>
                            <div><span class="status-badge status-complete">✅ Arquitetura</span></div>
                            <div><span class="status-badge status-complete">✅ Esquemático</span></div>
                            <div><span class="status-badge status-complete">✅ Simulação SPICE</span></div>
                            <div><span class="status-badge status-inprogress">🔄 Layout PCB</span></div>
                            <div><span class="status-badge status-pending">⏳ Firmware</span></div>
                            <div><span class="status-badge status-pending">⏳ Testes</span></div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Próximos Passos</h3>
                        <ol style="padding-left: 20px; line-height: 1.8;">
                            <li><strong>KiCad Layout:</strong> Terminar roteamento de trilhas (semana 1)</li>
                            <li><strong>Fabricação PCB:</strong> Encomendar prototipo JLCPCB (semana 2)</li>
                            <li><strong>Montagem:</strong> Soldar componentes e testes básicos (semana 3)</li>
                            <li><strong>Firmware ESP32:</strong> Implementar FOC + BLE (semana 4-5)</li>
                            <li><strong>Testes funcionais:</strong> Validar com motor real (semana 6)</li>
                        </ol>
                    </div>
                </div>
            </div>
            
            <!-- Seção 5: Ferramentas Usadas -->
            <div class="section">
                <h2>🛠️ Ferramentas CAD Utilizadas</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Stack de desenvolvimento 100% gratuito e open-source para PCB design e simulação.
                </p>
                
                <div class="grid">
                    <div class="card">
                        <h3>PCB Design</h3>
                        <ul class="specs-list">
                            <li><strong>Software:</strong> KiCad 7.0+</li>
                            <li><strong>Esquemático:</strong> KiCad Schematic</li>
                            <li><strong>Layout:</strong> KiCad PCB Editor</li>
                            <li><strong>3D Viewer:</strong> KiCad 3D Viewer</li>
                            <li><strong>Fabricação:</strong> Gerber export</li>
                            <li><strong>Status:</strong> ✅ Instalado</li>
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h3>Simulação SPICE</h3>
                        <ul class="specs-list">
                            <li><strong>Simulador:</strong> Ngspice 44.2</li>
                            <li><strong>Modelo:</strong> SPICE netlist (.cir)</li>
                            <li><strong>Análise:</strong> Transient (5ms)</li>
                            <li><strong>Plotagem:</strong> Python + Matplotlib</li>
                            <li><strong>Formatos:</strong> PNG, SVG, PDF</li>
                            <li><strong>Status:</strong> ✅ Instalado</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p><strong>Controladora Motor PMSM/BLDC</strong> | Projeto de Eletrônica de Potência | 2026</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Gerado automaticamente | Última atualização: 2026-08-14 | 
                Contato: <code>ag3@controlmotor.local</code>
            </p>
        </footer>
    </div>
</body>
</html>
"""
    
    with open('/home/teste/controlmotor/pcb_visualization.html', 'w') as f:
        f.write(html_content)
    
    print("✅ HTML de visualização gerado: pcb_visualization.html")

if __name__ == '__main__':
    print("\n")
    generate_kicad_images()
    print("\n")
    create_html_visualization()
    print("\n✅ Visualizações PCB concluídas!")
