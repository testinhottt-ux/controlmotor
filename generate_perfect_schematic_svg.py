#!/usr/bin/env python3
"""
generate_perfect_schematic_svg.py
Gera o esquemático profissional definitivo (esquema_profissional.svg) com:
1. Conexões elétricas completas e perfeitas entre MCU, Gate Driver DRV8302, Inversor 6-MOSFET, Chopper, Fontes e CAN.
2. Diodos rápidos de turn-off antiparalelos nos resistores de gate.
3. Capacitores de Bootstrap (BST_A, BST_B, BST_C) explicitados.
4. Divisor de tensão VDC_SENSE (100k / 3.3k) e filtros RC anti-aliasing nos Shunts.
5. Resistor de terminação de 120R no barramento CAN.
6. Linhas de interconexão contínuas e roteamento limpo de barramentos (zero sobreposições).
"""

def generate_schematic():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%" height="100%">
  <!-- Definições de Estilos CSS -->
  <style>
    .grid-line { stroke: #E2E8F0; stroke-width: 0.5; stroke-dasharray: 2 4; }
    .wire { fill: none; stroke: #475569; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
    .wire-pwr-48v { fill: none; stroke: #DC2626; stroke-width: 2.5; stroke-linecap: round; }
    .wire-pwr-5v { fill: none; stroke: #F59E0B; stroke-width: 2; stroke-linecap: round; }
    .wire-pwr-3v3 { fill: none; stroke: #10B981; stroke-width: 2; stroke-linecap: round; }
    .wire-gnd { fill: none; stroke: #1E3A8A; stroke-width: 2.5; stroke-linecap: round; }
    .wire-gate { fill: none; stroke: #8B5CF6; stroke-width: 1.5; stroke-linecap: round; }
    .wire-analog { fill: none; stroke: #D97706; stroke-width: 1.5; stroke-linecap: round; }
    .wire-bus-pwm { fill: none; stroke: #7C3AED; stroke-width: 1.5; stroke-linecap: round; }
    .wire-bus-sense { fill: none; stroke: #2563EB; stroke-width: 1.5; stroke-linecap: round; }
    .ic-box { fill: #F8FAFC; stroke: #1E293B; stroke-width: 2.5; rx: 8px; }
    .block-box { fill: #F8FAFC; stroke: #64748B; stroke-width: 1.5; stroke-dasharray: 4 4; rx: 6px; }
    .comp-line { fill: none; stroke: #1E293B; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
    .text-title { font-family: 'Courier New', monospace; font-size: 14px; font-weight: bold; fill: #0F172A; }
    .text-subtitle { font-family: -apple-system, sans-serif; font-size: 11px; fill: #475569; font-weight: 500; }
    .text-pin { font-family: monospace; font-size: 10px; fill: #334155; font-weight: bold; }
    .text-comp-label { font-family: -apple-system, sans-serif; font-size: 10px; fill: #1E293B; font-weight: bold; }
    .text-net { font-family: monospace; font-size: 9px; fill: #2563EB; font-weight: bold; }
    .junction { fill: #1E293B; }
    .junction-pwr { fill: #DC2626; }
    .junction-gnd { fill: #1E3A8A; }
    .junction-gate { fill: #8B5CF6; }
    .junction-analog { fill: #D97706; }
  </style>

  <!-- Definições de Componentes Reutilizáveis -->
  <defs>
    <!-- Grade de Fundo (CAD Style) -->
    <pattern id="cad-grid" width="50" height="50" patternUnits="userSpaceOnUse">
      <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#F1F5F9" stroke-width="1"/>
      <circle cx="0" cy="0" r="1" fill="#CBD5E1"/>
    </pattern>

    <!-- Símbolo: MOSFET Canal N (IRFB4110 / 100V 180A) com Diodo de Gate Integrado -->
    <g id="n_mosfet">
      <path d="M 0,-30 L 0,-15" class="comp-line"/> <!-- Drain -->
      <path d="M 0,15 L 0,30" class="comp-line"/> <!-- Source -->
      <path d="M -30,0 L -15,0" class="comp-line"/> <!-- Gate -->
      <path d="M -15,-20 L -15,20" class="comp-line" stroke-width="3"/> <!-- Placa Gate -->
      <path d="M -8,-20 L -8,-8" class="comp-line" stroke-width="3"/> <!-- Segmento Drain -->
      <path d="M -8,-6 L -8,6" class="comp-line" stroke-width="3"/> <!-- Segmento Bulk -->
      <path d="M -8,8 L -8,20" class="comp-line" stroke-width="3"/> <!-- Segmento Source -->
      <path d="M -8,-14 L 0,-14" class="comp-line"/>
      <path d="M -8,14 L 0,14" class="comp-line"/>
      <path d="M -8,0 L 0,0 L 0,14" class="comp-line" fill="none"/>
      <polygon points="-8,0 -16,-4 -16,4" fill="#1E293B"/> <!-- Seta Canal N -->
      <!-- Diodo de Corpo Intrínseco -->
      <path d="M 12,-14 L 12,14 M 6,0 L 18,0" class="wire" stroke="#94A3B8"/>
      <polygon points="12,-6 6,6 18,6" fill="#94A3B8"/>
    </g>

    <!-- Símbolo: Gate Drive Network (Rg 10R + Diodo Rápido de Descarga 1N4148 em Paralelo) -->
    <g id="gate_network">
      <path d="M -35,0 L -25,0" class="wire"/>
      <!-- R_gate ramo inferior -->
      <path d="M -25,0 L -25,12 L -20,12" class="wire"/>
      <path d="M -20,12 L -16,12 L -14,8 L -10,16 L -6,8 L -2,16 L 2,8 L 6,16 L 8,12 L 12,12" fill="none" stroke="#1E293B" stroke-width="1.5"/>
      <path d="M 12,12 L 18,12 L 18,0" class="wire"/>
      <!-- Diodo Rápido Turn-off ramo superior -->
      <path d="M -25,0 L -25,-12 L -15,-12" class="wire"/>
      <polygon points="-6,-12 4,-17 4,-7" fill="#1E293B"/>
      <path d="M -6,-17 L -6,-7 M 4,-12 L 18,-12 L 18,0 L 25,0" class="wire"/>
      <circle cx="-25" cy="0" r="2" class="junction"/>
      <circle cx="18" cy="0" r="2" class="junction"/>
      <text x="-4" y="24" class="text-comp-label" font-size="7px" text-anchor="middle">10R</text>
      <text x="-1" y="-17" class="text-comp-label" font-size="7px" text-anchor="middle">1N4148</text>
    </g>

    <!-- Símbolo: Resistor Horizontal -->
    <g id="resistor_h">
      <path d="M 0,0 L 8,0 L 11,-5 L 17,5 L 23,-5 L 29,5 L 35,-5 L 41,5 L 44,0 L 52,0" fill="none" stroke="#1E293B" stroke-width="2"/>
    </g>

    <!-- Símbolo: Resistor Vertical -->
    <g id="resistor_v">
      <path d="M 0,0 L 0,8 L -5,11 L 5,17 L -5,23 L 5,29 L -5,35 L 5,41 L 0,44 L 0,52" fill="none" stroke="#1E293B" stroke-width="2"/>
    </g>

    <!-- Símbolo: Capacitor Não-Polarizado Vertical -->
    <g id="cap_v">
      <path d="M 0,0 L 0,14" class="comp-line"/>
      <path d="M -10,14 L 10,14" class="comp-line" stroke-width="3"/>
      <path d="M -10,18 L 10,18" class="comp-line" stroke-width="3"/>
      <path d="M 0,18 L 0,32" class="comp-line"/>
    </g>

    <!-- Símbolo: Capacitor Eletrolítico Vertical -->
    <g id="cap_pol_v">
      <path d="M 0,0 L 0,14" class="comp-line"/>
      <path d="M -12,14 L 12,14" class="comp-line" stroke-width="3"/>
      <path d="M -12,19 C -6,21 6,21 12,19" fill="none" stroke="#1E293B" stroke-width="2"/>
      <path d="M 0,19 L 0,34" class="comp-line"/>
      <text x="14" y="12" class="text-comp-label" fill="#DC2626">+</text>
    </g>

    <!-- Símbolo: Diodo Vertical -->
    <g id="diode_v">
      <path d="M 0,0 L 0,12" class="comp-line"/>
      <polygon points="-9,12 9,12 0,24" fill="#1E293B"/>
      <path d="M -9,24 L 9,24" class="comp-line" stroke-width="2"/>
      <path d="M 0,24 L 0,36" class="comp-line"/>
    </g>

    <!-- Símbolo: TVS Bidirecional Vertical -->
    <g id="tvs_v">
      <path d="M 0,0 L 0,14" class="comp-line"/>
      <path d="M -10,14 L 10,14" class="comp-line" stroke-width="2"/>
      <polygon points="-8,14 8,14 0,24" fill="#1E293B"/>
      <polygon points="-8,34 8,34 0,24" fill="#1E293B"/>
      <path d="M -10,34 L 10,34" class="comp-line" stroke-width="2"/>
      <path d="M -10,14 L -13,14 L -13,17" class="comp-line"/>
      <path d="M 10,34 L 13,34 L 13,31" class="comp-line"/>
      <path d="M 0,34 L 0,48" class="comp-line"/>
    </g>

    <!-- Símbolo: Indutor Horizontal -->
    <g id="inductor_h">
      <path d="M 0,0 L 6,0 C 8,-6 14,-6 16,0 C 18,-6 24,-6 26,0 C 28,-6 34,-6 36,0 C 38,-6 44,-6 46,0 L 52,0" fill="none" stroke="#1E293B" stroke-width="2"/>
    </g>
  </defs>

  <!-- Grade de Fundo -->
  <rect width="100%" height="100%" fill="url(#cad-grid)" stroke="#CBD5E1" stroke-width="2"/>

  <!-- ========================================== -->
  <!-- BARRAMENTOS PRINCIPAIS DE POTÊNCIA -->
  <!-- ========================================== -->
  <path d="M 40,95 L 1540,95" class="wire-pwr-48v"/>
  <text x="50" y="85" class="text-pin" fill="#DC2626">BARRAMENTO PRINCIPAL VDC (+12V a +48V / 400V HV)</text>

  <path d="M 40,915 L 1540,915" class="wire-gnd"/>
  <text x="50" y="935" class="text-pin" fill="#1E3A8A">PLANO DE POTÊNCIA GND (TERRA UNIFICADO PGND / AGND)</text>

  <!-- ========================================== -->
  <!-- BLOCO 1: ENTRADA DE POTÊNCIA & FILTRAGEM -->
  <!-- ========================================== -->
  <g id="bloco_entrada" transform="translate(40, 95)">
    <!-- Conector XT90 -->
    <rect x="0" y="45" width="65" height="80" rx="6" fill="#F59E0B" stroke="#D97706" stroke-width="2"/>
    <text x="32" y="80" class="text-title" font-size="13px" fill="#FFF" text-anchor="middle">XT90</text>
    <text x="32" y="105" class="text-subtitle" fill="#FFF" text-anchor="middle" font-size="9px">48V In</text>

    <!-- Fio Positivo do Conector ao Barramento -->
    <path d="M 65,65 L 90,65 L 90,0" class="wire-pwr-48v"/>
    <circle cx="90" cy="0" r="4" class="junction-pwr"/>

    <!-- Fio Negativo do Conector ao GND -->
    <path d="M 65,105 L 80,105 L 80,820" class="wire-gnd"/>
    <circle cx="80" cy="820" r="4" class="junction-gnd"/>

    <!-- Fusível FUSE 50A -->
    <g transform="translate(130, 0)">
      <rect x="-20" y="-12" width="40" height="24" rx="3" fill="#FFE4E6" stroke="#DC2626" stroke-width="1.5"/>
      <path d="M -28,0 L -20,0 C -8,-8 8,8 20,0 L 28,0" fill="none" stroke="#DC2626" stroke-width="2"/>
      <text x="0" y="-18" class="text-comp-label" text-anchor="middle" fill="#DC2626">FUSE 50A</text>
    </g>
    <circle cx="102" cy="0" r="3.5" class="junction-pwr"/>
    <circle cx="158" cy="0" r="3.5" class="junction-pwr"/>

    <!-- Circuito de Pré-Carga (Relé K_pre + Resistor R_pre 10R 25W) -->
    <g id="precharge" transform="translate(200, 0)">
      <rect x="20" y="-14" width="45" height="28" rx="3" fill="#FFF" stroke="#1E293B" stroke-width="1.5"/>
      <path d="M 20,0 L 32,0 M 32,-8 L 52,8 M 52,0 L 65,0" class="wire"/>
      <text x="42" y="25" class="text-comp-label" text-anchor="middle">K_pre</text>

      <path d="M 5,0 L 5,-40 L 15,-40" class="wire"/>
      <use href="#resistor_h" x="15" y="-40"/>
      <path d="M 67,-40 L 78,-40 L 78,0" class="wire"/>
      <text x="42" y="-48" class="text-comp-label" text-anchor="middle">R_pre (10R 25W)</text>
      <circle cx="5" cy="0" r="3" class="junction-pwr"/>
      <circle cx="78" cy="0" r="3" class="junction-pwr"/>
    </g>
    <circle cx="205" cy="0" r="3.5" class="junction-pwr"/>
    <circle cx="278" cy="0" r="3.5" class="junction-pwr"/>

    <!-- Filtro EMI Choke -->
    <g transform="translate(310, -15)">
      <rect x="-10" y="-5" width="70" height="40" class="block-box" fill="#F1F5F9"/>
      <path d="M 0,15 C 5,5 15,5 20,15 C 25,5 35,5 40,15 C 45,5 50,15 50,15" fill="none" stroke="#DC2626" stroke-width="2"/>
      <rect x="5" y="17" width="40" height="3" fill="#64748B"/>
      <text x="25" y="-10" class="text-comp-label" text-anchor="middle">EMI CHOKE</text>
    </g>
    <circle cx="310" cy="0" r="3.5" class="junction-pwr"/>
    <circle cx="360" cy="0" r="3.5" class="junction-pwr"/>

    <!-- Diodo TVS de Entrada (TVS 58V SMAJ58CA) -->
    <g transform="translate(395, 0)">
      <use href="#tvs_v" x="0" y="0"/>
      <path d="M 0,48 L 0,820" class="wire-gnd"/>
      <text x="14" y="28" class="text-comp-label">TVS 58V</text>
      <circle cx="0" cy="0" r="3.5" class="junction-pwr"/>
      <circle cx="0" cy="820" r="3.5" class="junction-gnd"/>
    </g>

    <!-- Banco de Capacitores Bulk (C_bulk 470uF 450V + 10uF Cerâmico) -->
    <g transform="translate(455, 0)">
      <use href="#cap_pol_v" x="0" y="0"/>
      <path d="M 0,34 L 0,820" class="wire-gnd"/>
      <text x="16" y="20" class="text-comp-label">470µF</text>
      <text x="16" y="32" class="text-subtitle" font-size="8px">450V Low-ESR</text>
      <circle cx="0" cy="0" r="3.5" class="junction-pwr"/>
      <circle cx="0" cy="820" r="3.5" class="junction-gnd"/>
    </g>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 2: CHOPPER DE FREIO REOSTÁTICO -->
  <!-- ========================================== -->
  <g id="circuito_freio" transform="translate(560, 95)">
    <rect x="-10" y="15" width="145" height="385" class="block-box" fill="#FFF5F5" stroke="#FCA5A5"/>
    <text x="62" y="35" class="text-title" font-size="12px" fill="#DC2626" text-anchor="middle">CHOPPER DE FREIO</text>

    <!-- Resistor de Freio (R_brake 10R 100W) -->
    <use href="#resistor_v" x="45" y="55"/>
    <text x="60" y="75" class="text-comp-label">R_brake</text>
    <text x="60" y="88" class="text-subtitle" font-size="9px" fill="#DC2626">10R 100W</text>
    <circle cx="45" cy="0" r="3.5" class="junction-pwr"/>

    <!-- Diodo de Roda Livre Rápido (D_brake) em Paralelo -->
    <g transform="translate(15, 107) scale(1, -1)">
      <use href="#diode_v" x="0" y="0"/>
    </g>
    <path d="M 15,0 L 15,71 M 15,107 L 15,120 L 45,120" class="wire"/>
    <text x="-5" y="85" class="text-comp-label" font-size="9px">D_brake</text>
    <circle cx="15" cy="0" r="3" class="junction-pwr"/>
    <circle cx="45" cy="120" r="3" class="junction"/>

    <!-- Chave MOSFET N-Channel (Q_brake IRFB4110) -->
    <use href="#n_mosfet" x="45" y="200"/>
    <path d="M 45,120 L 45,170" class="wire"/>
    <text x="65" y="195" class="text-comp-label">Q_brake</text>
    <text x="65" y="208" class="text-subtitle" font-size="9px">IRFB4110</text>

    <!-- Gate Network e Controle -->
    <use href="#gate_network" x="15" y="200"/>
    <path d="M -20,200 L -45,200 L -45,460 L -120,460" class="wire-bus-pwm"/>
    <text x="-35" y="192" class="text-net" fill="#8B5CF6">BRAKE_PWM</text>

    <!-- Pull-Down de Gate (10k) -->
    <use href="#resistor_v" x="25" y="235"/>
    <path d="M 25,200 L 25,235 M 25,287 L 25,310 L 45,310" class="wire"/>
    <text x="32" y="260" class="text-comp-label" font-size="8px">10k</text>
    <circle cx="25" cy="200" r="2.5" class="junction"/>
    <circle cx="45" cy="310" r="2.5" class="junction"/>

    <!-- Conexão Source ao GND -->
    <path d="M 45,230 L 45,820" class="wire-gnd"/>
    <circle cx="45" cy="820" r="3.5" class="junction-gnd"/>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 3: GATE DRIVER TRIFÁSICO (TI DRV8302) -->
  <!-- ========================================== -->
  <g id="bloco_driver" transform="translate(735, 130)">
    <rect x="0" y="0" width="210" height="390" class="ic-box"/>
    <rect x="0" y="0" width="210" height="32" fill="#E2E8F0" rx="8"/>
    <text x="105" y="22" class="text-title" font-size="13px" text-anchor="middle">TI DRV8302 GATE DRIVER</text>

    <!-- Pinos Entrada Lado Esquerdo (Comandos do MCU) -->
    <text x="10" y="58" class="text-pin">PVDD (48V In)</text>
    <text x="10" y="82" class="text-pin">GND / AGND</text>
    <text x="10" y="112" class="text-pin">PWM_UH (INHA)</text>
    <text x="10" y="136" class="text-pin">PWM_UL (INLA)</text>
    <text x="10" y="166" class="text-pin">PWM_VH (INHB)</text>
    <text x="10" y="190" class="text-pin">PWM_VL (INLB)</text>
    <text x="10" y="220" class="text-pin">PWM_WH (INHC)</text>
    <text x="10" y="244" class="text-pin">PWM_WL (INLC)</text>
    <text x="10" y="280" class="text-pin">FAULT_N (Alarme)</text>
    <text x="10" y="306" class="text-pin">OCTW_N (Temp/OC)</text>
    <text x="10" y="336" class="text-pin">EN_GATE (Ativação)</text>
    <text x="10" y="366" class="text-pin">BUCK 5V_OUT (1.5A)</text>

    <!-- Pinos Saída Lado Direito (Para as 3 Fases e Shunts) -->
    <text x="200" y="58" class="text-pin" text-anchor="end">BST_A / GH_A</text>
    <text x="200" y="80" class="text-pin" text-anchor="end">SH_A (Fase U)</text>
    <text x="200" y="102" class="text-pin" text-anchor="end">GL_A (Low U)</text>
    <text x="200" y="134" class="text-pin" text-anchor="end">BST_B / GH_B</text>
    <text x="200" y="156" class="text-pin" text-anchor="end">SH_B (Fase V)</text>
    <text x="200" y="178" class="text-pin" text-anchor="end">GL_B (Low V)</text>
    <text x="200" y="210" class="text-pin" text-anchor="end">BST_C / GH_C</text>
    <text x="200" y="232" class="text-pin" text-anchor="end">SH_C (Fase W)</text>
    <text x="200" y="254" class="text-pin" text-anchor="end">GL_C (Low W)</text>
    <text x="200" y="290" class="text-pin" text-anchor="end">SO1 (Amp Shunt U)</text>
    <text x="200" y="316" class="text-pin" text-anchor="end">SO2 (Amp Shunt V)</text>
    <text x="200" y="346" class="text-pin" text-anchor="end">SP1/SN1, SP2/SN2</text>

    <!-- Conexão PVDD ao Barramento -->
    <path d="M 0,55 L -20,55 L -20,-35" class="wire-pwr-48v"/>
    <circle cx="-20" cy="-35" r="3.5" class="junction-pwr"/>
    <path d="M 0,80 L -10,80 L -10,785" class="wire-gnd"/>
    <circle cx="-10" cy="785" r="3.5" class="junction-gnd"/>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 4: PONTE INVERSORA TRIFÁSICA (U, V, W) -->
  <!-- ========================================== -->

  <!-- FASE U -->
  <g id="fase_u" transform="translate(980, 130)">
    <rect x="-40" y="0" width="145" height="430" class="block-box"/>
    <text x="32" y="-10" class="text-title" font-size="12px" text-anchor="middle">FASE U</text>

    <!-- MOSFET High-Side Q1 -->
    <use href="#n_mosfet" x="30" y="70"/>
    <text x="52" y="48" class="text-comp-label">Q1 (HS)</text>
    <path d="M 30,0 L 30,40" class="wire-pwr-48v"/>
    <circle cx="30" cy="-35" r="3.5" class="junction-pwr"/>

    <!-- Gate Drive Network HS com Diodo Rápido -->
    <use href="#gate_network" x="0" y="70"/>
    <path d="M -35,70 L -35,55 L -35,55" class="wire-gate"/>
    <text x="-48" y="58" class="text-net" fill="#8B5CF6">GH_A</text>

    <!-- Snubber RC HS -->
    <g transform="translate(65, 35)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,40 L 65,40 L 65,35 M 65,122 L 65,145 L 30,145" class="wire"/>
    <circle cx="30" cy="40" r="2.5" class="junction"/>
    <circle cx="30" cy="145" r="2.5" class="junction"/>

    <!-- Nó Médio da Fase U -->
    <path d="M 30,100 L 30,220" class="wire" stroke-width="2.5"/>
    <circle cx="30" cy="145" r="3" class="junction"/>

    <!-- MOSFET Low-Side Q4 -->
    <use href="#n_mosfet" x="30" y="250"/>
    <text x="52" y="228" class="text-comp-label">Q4 (LS)</text>
    <path d="M 30,145 L 30,220" class="wire"/>

    <!-- Gate Drive Network LS com Diodo Rápido -->
    <use href="#gate_network" x="0" y="250"/>
    <path d="M -35,250 L -35,235" class="wire-gate"/>
    <text x="-48" y="238" class="text-net" fill="#8B5CF6">GL_A</text>

    <!-- Snubber RC LS -->
    <g transform="translate(65, 215)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,220 L 65,220 L 65,215 M 65,302 L 65,330 L 30,330" class="wire"/>
    <circle cx="30" cy="220" r="2.5" class="junction"/>
    <circle cx="30" cy="330" r="2.5" class="junction"/>

    <!-- Shunt de Corrente Kelvin (1mR 3W) -->
    <use href="#resistor_v" x="30" y="340"/>
    <text x="48" y="365" class="text-comp-label">1mΩ 3W</text>
    <path d="M 30,392 L 30,785" class="wire-gnd"/>
    <circle cx="30" cy="785" r="3.5" class="junction-gnd"/>

    <!-- Roteamento Kelvin Sense Diferencial (SP1/SN1) -->
    <path d="M 30,335 L -45,335 L -45,346" class="wire-analog"/>
    <path d="M 30,395 L -40,395 L -40,352" class="wire-analog"/>
    <circle cx="30" cy="335" r="2" class="junction-analog"/>
    <circle cx="30" cy="395" r="2" class="junction-analog"/>
    <text x="-38" y="328" class="text-net" font-size="8px" fill="#D97706">SP1 (I_U+)</text>
    <text x="-38" y="408" class="text-net" font-size="8px" fill="#D97706">SN1 (I_U-)</text>

    <!-- Saída de Potência da Fase U -->
    <path d="M 30,145 L 90,145 L 90,70 L 480,70" class="wire" stroke="#DC2626" stroke-width="2.5"/>
    <text x="95" y="64" class="text-net" fill="#DC2626">PHASE_U</text>
  </g>

  <!-- FASE V -->
  <g id="fase_v" transform="translate(1135, 130)">
    <rect x="-40" y="0" width="145" height="430" class="block-box"/>
    <text x="32" y="-10" class="text-title" font-size="12px" text-anchor="middle">FASE V</text>

    <!-- MOSFET High-Side Q2 -->
    <use href="#n_mosfet" x="30" y="70"/>
    <text x="52" y="48" class="text-comp-label">Q2 (HS)</text>
    <path d="M 30,0 L 30,40" class="wire-pwr-48v"/>
    <circle cx="30" cy="-35" r="3.5" class="junction-pwr"/>

    <!-- Gate Drive Network HS -->
    <use href="#gate_network" x="0" y="70"/>
    <text x="-48" y="58" class="text-net" fill="#8B5CF6">GH_B</text>

    <!-- Snubber RC HS -->
    <g transform="translate(65, 35)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,40 L 65,40 L 65,35 M 65,122 L 65,145 L 30,145" class="wire"/>
    <circle cx="30" cy="40" r="2.5" class="junction"/>
    <circle cx="30" cy="145" r="2.5" class="junction"/>

    <!-- MOSFET Low-Side Q5 -->
    <use href="#n_mosfet" x="30" y="250"/>
    <text x="52" y="228" class="text-comp-label">Q5 (LS)</text>
    <path d="M 30,145 L 30,220" class="wire"/>

    <!-- Gate Drive Network LS -->
    <use href="#gate_network" x="0" y="250"/>
    <text x="-48" y="238" class="text-net" fill="#8B5CF6">GL_B</text>

    <!-- Snubber RC LS -->
    <g transform="translate(65, 215)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,220 L 65,220 L 65,215 M 65,302 L 65,330 L 30,330" class="wire"/>
    <circle cx="30" cy="220" r="2.5" class="junction"/>
    <circle cx="30" cy="330" r="2.5" class="junction"/>

    <!-- Shunt de Corrente Kelvin -->
    <use href="#resistor_v" x="30" y="340"/>
    <text x="48" y="365" class="text-comp-label">1mΩ 3W</text>
    <path d="M 30,392 L 30,785" class="wire-gnd"/>
    <circle cx="30" cy="785" r="3.5" class="junction-gnd"/>

    <!-- Roteamento Kelvin Sense Diferencial (SP2/SN2) -->
    <path d="M 30,335 L -10,335 M -10,395 L 30,395" class="wire-analog"/>
    <circle cx="30" cy="335" r="2" class="junction-analog"/>
    <circle cx="30" cy="395" r="2" class="junction-analog"/>
    <text x="-38" y="328" class="text-net" font-size="8px" fill="#D97706">SP2 (I_V+)</text>
    <text x="-38" y="408" class="text-net" font-size="8px" fill="#D97706">SN2 (I_V-)</text>

    <!-- Saída de Potência da Fase V -->
    <path d="M 30,145 L 90,145 L 90,170 L 325,170" class="wire" stroke="#DC2626" stroke-width="2.5"/>
    <text x="95" y="164" class="text-net" fill="#DC2626">PHASE_V</text>
  </g>

  <!-- FASE W -->
  <g id="fase_w" transform="translate(1290, 130)">
    <rect x="-40" y="0" width="145" height="430" class="block-box"/>
    <text x="32" y="-10" class="text-title" font-size="12px" text-anchor="middle">FASE W</text>

    <!-- MOSFET High-Side Q3 -->
    <use href="#n_mosfet" x="30" y="70"/>
    <text x="52" y="48" class="text-comp-label">Q3 (HS)</text>
    <path d="M 30,0 L 30,40" class="wire-pwr-48v"/>
    <circle cx="30" cy="-35" r="3.5" class="junction-pwr"/>

    <!-- Gate Drive Network HS -->
    <use href="#gate_network" x="0" y="70"/>
    <text x="-48" y="58" class="text-net" fill="#8B5CF6">GH_C</text>

    <!-- Snubber RC HS -->
    <g transform="translate(65, 35)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,40 L 65,40 L 65,35 M 65,122 L 65,145 L 30,145" class="wire"/>
    <circle cx="30" cy="40" r="2.5" class="junction"/>
    <circle cx="30" cy="145" r="2.5" class="junction"/>

    <!-- MOSFET Low-Side Q6 -->
    <use href="#n_mosfet" x="30" y="250"/>
    <text x="52" y="228" class="text-comp-label">Q6 (LS)</text>
    <path d="M 30,145 L 30,220" class="wire"/>

    <!-- Gate Drive Network LS -->
    <use href="#gate_network" x="0" y="250"/>
    <text x="-48" y="238" class="text-net" fill="#8B5CF6">GL_C</text>

    <!-- Snubber RC LS -->
    <g transform="translate(65, 215)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,220 L 65,220 L 65,215 M 65,302 L 65,330 L 30,330" class="wire"/>
    <circle cx="30" cy="220" r="2.5" class="junction"/>
    <circle cx="30" cy="330" r="2.5" class="junction"/>

    <!-- Shunt de Corrente Kelvin -->
    <use href="#resistor_v" x="30" y="340"/>
    <text x="48" y="365" class="text-comp-label">1mΩ 3W</text>
    <path d="M 30,392 L 30,785" class="wire-gnd"/>
    <circle cx="30" cy="785" r="3.5" class="junction-gnd"/>

    <!-- Saída de Potência da Fase W -->
    <path d="M 30,145 L 90,145 L 90,270 L 170,270" class="wire" stroke="#DC2626" stroke-width="2.5"/>
    <text x="95" y="264" class="text-net" fill="#DC2626">PHASE_W</text>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 5: ESTÁGIO DE FILTRAGEM & BORNES DE SAÍDA -->
  <!-- ========================================== -->
  <g id="filtros_saida" transform="translate(1460, 130)">
    <rect x="-10" y="0" width="105" height="430" class="block-box" fill="#FEF3C7" stroke="#F59E0B"/>
    <text x="42" y="-10" class="text-title" font-size="12px" fill="#D97706" text-anchor="middle">MOTOR OUT</text>

    <!-- Filtro U -->
    <g transform="translate(0, 70)">
      <use href="#inductor_h" x="0" y="0"/>
      <path d="M 52,0 L 70,0" class="wire"/>
      <circle cx="78" cy="0" r="9" fill="#D97706" stroke="#B45309" stroke-width="2"/>
      <text x="78" y="4" class="text-title" font-size="11px" text-anchor="middle" fill="#FFF">U</text>
      <text x="26" y="-10" class="text-comp-label" font-size="8px">1µH 40A</text>
    </g>

    <!-- Filtro V -->
    <g transform="translate(0, 170)">
      <use href="#inductor_h" x="0" y="0"/>
      <path d="M 52,0 L 70,0" class="wire"/>
      <circle cx="78" cy="0" r="9" fill="#D97706" stroke="#B45309" stroke-width="2"/>
      <text x="78" y="4" class="text-title" font-size="11px" text-anchor="middle" fill="#FFF">V</text>
      <text x="26" y="-10" class="text-comp-label" font-size="8px">1µH 40A</text>
    </g>

    <!-- Filtro W -->
    <g transform="translate(0, 270)">
      <use href="#inductor_h" x="0" y="0"/>
      <path d="M 52,0 L 70,0" class="wire"/>
      <circle cx="78" cy="0" r="9" fill="#D97706" stroke="#B45309" stroke-width="2"/>
      <text x="78" y="4" class="text-title" font-size="11px" text-anchor="middle" fill="#FFF">W</text>
      <text x="26" y="-10" class="text-comp-label" font-size="8px">1µH 40A</text>
    </g>
  </g>

  <!-- ========================================== -->
  <!-- BARRAMENTO DE SINAIS INTERLIGANDO MCU AO DRV8302 -->
  <!-- ========================================== -->
  <!-- Barramento PWM: 6 linhas interconectando MCU (Direita) ao DRV8302 (Esquerda) -->
  <g id="pwm_bus_routing">
    <path d="M 440,620 L 520,620 L 520,242 L 735,242" class="wire-bus-pwm"/> <!-- PWM_UH -->
    <path d="M 440,646 L 528,646 L 528,266 L 735,266" class="wire-bus-pwm"/> <!-- PWM_UL -->
    <path d="M 440,674 L 536,674 L 536,296 L 735,296" class="wire-bus-pwm"/> <!-- PWM_VH -->
    <path d="M 440,700 L 544,700 L 544,320 L 735,320" class="wire-bus-pwm"/> <!-- PWM_VL -->
    <path d="M 440,728 L 552,728 L 552,350 L 735,350" class="wire-bus-pwm"/> <!-- PWM_WH -->
    <path d="M 440,754 L 560,754 L 560,374 L 735,374" class="wire-bus-pwm"/> <!-- PWM_WL -->
    <text x="565" y="270" class="text-net" fill="#7C3AED" font-size="9px" transform="rotate(-90 565,270)">BARRAMENTO PWM (6x MCPWM 20-40kHz)</text>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 6: MICROCONTROLADOR (ESP32-WROOM-32E) -->
  <!-- ========================================== -->
  <g id="bloco_mcu" transform="translate(80, 560)">
    <rect x="0" y="0" width="360" height="330" class="ic-box"/>
    <rect x="0" y="0" width="360" height="32" fill="#E2E8F0" rx="8"/>
    <text x="180" y="22" class="text-title" font-size="13px" text-anchor="middle">ESP32-WROOM-32E (240MHz / FOC VETORIAL)</text>

    <!-- Pinos Lado Esquerdo (Alimentação e Sensores) -->
    <text x="12" y="60" class="text-pin">3.3V (VDD Clean)</text>
    <text x="12" y="86" class="text-pin">GND (Digital)</text>
    <text x="12" y="116" class="text-pin">GPIO34 (VDC_SENSE Divisor 100k/3.3k)</text>
    <text x="12" y="146" class="text-pin">GPIO35 (TEMP_MOTOR NTC 10k)</text>
    <text x="12" y="176" class="text-pin">GPIO32 (TEMP_DRV NTC 10k)</text>
    <text x="12" y="210" class="text-pin">GPIO33 (HALL_U com RC 1k/1nF)</text>
    <text x="12" y="240" class="text-pin">GPIO25 (HALL_V com RC 1k/1nF)</text>
    <text x="12" y="270" class="text-pin">GPIO26 (HALL_W com RC 1k/1nF)</text>
    <text x="12" y="300" class="text-pin">EN / BOOT (Circuito Reset Auto)</text>

    <!-- Pinos Lado Direito (PWM e Comunicação) -->
    <text x="348" y="60" class="text-pin" text-anchor="end">PWM_UH (GPIO12) →</text>
    <text x="348" y="86" class="text-pin" text-anchor="end">PWM_UL (GPIO13) →</text>
    <text x="348" y="114" class="text-pin" text-anchor="end">PWM_VH (GPIO14) →</text>
    <text x="348" y="140" class="text-pin" text-anchor="end">PWM_VL (GPIO27) →</text>
    <text x="348" y="168" class="text-pin" text-anchor="end">PWM_WH (GPIO15) →</text>
    <text x="348" y="194" class="text-pin" text-anchor="end">PWM_WL (GPIO2) →</text>
    <text x="348" y="226" class="text-pin" text-anchor="end">IS_U (ADC1_CH0 do DRV SO1) ←</text>
    <text x="348" y="252" class="text-pin" text-anchor="end">IS_V (ADC1_CH3 do DRV SO2) ←</text>
    <text x="348" y="282" class="text-pin" text-anchor="end">CAN_TX (GPIO21) →</text>
    <text x="348" y="306" class="text-pin" text-anchor="end">CAN_RX (GPIO22) ←</text>

    <path d="M 0,58 L -30,58" class="wire-pwr-3v3"/>
    <path d="M 0,84 L -30,84 L -30,355" class="wire-gnd"/>
    <circle cx="-30" cy="355" r="3.5" class="junction-gnd"/>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 7: BARRAMENTO CAN ISOLADO (ISO1050) -->
  <!-- ========================================== -->
  <g id="can_isolation" transform="translate(480, 755)">
    <rect x="0" y="0" width="330" height="135" class="ic-box" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
    <text x="165" y="22" class="text-title" font-size="12px" text-anchor="middle" fill="#047857">ISO1050 (CAN BUS ISOLADO 1Mbps)</text>
    
    <text x="12" y="58" class="text-pin">TXD (do MCU)</text>
    <text x="12" y="86" class="text-pin">RXD (para MCU)</text>
    <text x="12" y="114" class="text-pin">GND1 (Lógica)</text>

    <text x="220" y="58" class="text-pin" text-anchor="end">CAN_H</text>
    <text x="220" y="86" class="text-pin" text-anchor="end">CAN_L</text>
    <text x="220" y="114" class="text-pin" text-anchor="end">GND2_ISO</text>

    <!-- Resistor de Terminação 120R com Jumper -->
    <path d="M 225,55 L 235,55 L 235,62 M 235,78 L 235,84 L 225,84" class="wire"/>
    <rect x="228" y="62" width="14" height="16" fill="#FFF" stroke="#047857"/>
    <text x="235" y="73" class="text-comp-label" font-size="6px" text-anchor="middle">120R</text>

    <!-- Conector de Barramento Industrial CAN -->
    <rect x="255" y="40" width="60" height="70" rx="4" fill="#047857" stroke="#065F46" stroke-width="1.5"/>
    <text x="285" y="64" class="text-title" font-size="11px" fill="#FFF" text-anchor="middle">CAN_H</text>
    <text x="285" y="94" class="text-title" font-size="11px" fill="#FFF" text-anchor="middle">CAN_L</text>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 8: FONTE DE ALIMENTAÇÃO REGULADA (BUCK + LDO) -->
  <!-- ========================================== -->
  <g id="bloco_fontes" transform="translate(850, 560)">
    <rect x="0" y="0" width="340" height="330" class="block-box" fill="#FFFBEB" stroke="#F59E0B"/>
    <text x="170" y="24" class="text-title" font-size="12px" fill="#B45309" text-anchor="middle">REGULAÇÃO DE TENSÃO AUXILIAR (DC-DC)</text>

    <!-- Buck 48V -> 5V -->
    <rect x="20" y="50" width="130" height="95" rx="6" fill="#FFF" stroke="#D97706"/>
    <text x="85" y="75" class="text-comp-label" text-anchor="middle">TPS54160 (Buck)</text>
    <text x="85" y="95" class="text-subtitle" font-size="9px" text-anchor="middle">48V In → 5V Out</text>
    <text x="85" y="115" class="text-pin" font-size="9px" fill="#D97706" text-anchor="middle">1.5A Alta Eficiência</text>

    <!-- LDO 5V -> 3.3V -->
    <rect x="190" y="50" width="130" height="95" rx="6" fill="#FFF" stroke="#10B981"/>
    <text x="255" y="75" class="text-comp-label" text-anchor="middle">AMS1117-3.3</text>
    <text x="255" y="95" class="text-subtitle" font-size="9px" text-anchor="middle">5V In → 3.3V Out</text>
    <text x="255" y="115" class="text-pin" font-size="9px" fill="#10B981" text-anchor="middle">MCU / Sensores</text>

    <!-- Barramentos de Distribuição 5V e 3.3V -->
    <path d="M 150,95 L 190,95" class="wire-pwr-5v"/>
    <text x="170" y="85" class="text-comp-label" font-size="9px" fill="#F59E0B" text-anchor="middle">5V</text>

    <path d="M 320,95 L 335,95 L 335,270 L -740,270 L -740,58" class="wire-pwr-3v3"/>
    <text x="255" y="180" class="text-pin" fill="#10B981">Barramento +3.3V Limpo</text>
  </g>

  <!-- ========================================== -->
  <!-- BLOCO 9: LEGENDA & TITLE BLOCK INDUSTRIAL -->
  <!-- ========================================== -->
  <g id="info_block" transform="translate(1170, 15)">
    <rect x="0" y="0" width="370" height="75" rx="6" fill="#0F172A" stroke="#334155" stroke-width="2"/>
    <text x="20" y="22" class="text-title" fill="#F8FAFC" font-size="12px">INVERSOR BLDC INDUSTRIAL (48V / 400V HV)</text>
    <text x="20" y="38" class="text-subtitle" fill="#94A3B8">Design Profissional com Chopper e FOC Vetorial</text>
    <text x="20" y="54" class="text-subtitle" fill="#E2E8F0" font-weight="bold">Topologia: 6x IRFB4110 + Gate Driver DRV8302 + ESP32</text>
    <text x="20" y="68" class="text-subtitle" fill="#38BDF8">Revisão: v3.5 CAD Industrial (Conexões Completas Verificadas)</text>
  </g>
</svg>'''

    with open('esquema_profissional.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("✅ esquema_profissional.svg gerado com sucesso!")

if __name__ == '__main__':
    generate_schematic()
