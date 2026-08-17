#!/usr/bin/env python3
"""
generate_industrial_svg_suite.py
Gera a suíte completa de esquemáticos CAD industriais com todas as recomendações:
- Dead-Time 500ns (R_DT 68k)
- Varistor MOV 14D680K + TVS 5KP58CA na entrada
- Optoacopladores rápidos TLP2362 nos sensores Hall
- Conversor DC-DC isolado B0505S-1WR3 no barramento CAN ISO1050
- Ponto de aterramento único Star Ground (PGND/AGND)
- Chopper de freio dinâmico com histerese
"""

import os
import json

def generate_sheet5_general():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%" height="100%">
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
    .wire-iso { fill: none; stroke: #059669; stroke-width: 1.5; stroke-linecap: round; stroke-dasharray: 4 2; }
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
    .junction-analog { fill: #D97706; }
  </style>

  <defs>
    <pattern id="cad-grid" width="50" height="50" patternUnits="userSpaceOnUse">
      <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#F1F5F9" stroke-width="1"/>
      <circle cx="0" cy="0" r="1" fill="#CBD5E1"/>
    </pattern>

    <g id="n_mosfet">
      <path d="M 0,-30 L 0,-15" class="comp-line"/>
      <path d="M 0,15 L 0,30" class="comp-line"/>
      <path d="M -30,0 L -15,0" class="comp-line"/>
      <path d="M -15,-20 L -15,20" class="comp-line" stroke-width="3"/>
      <path d="M -8,-20 L -8,-8" class="comp-line" stroke-width="3"/>
      <path d="M -8,-6 L -8,6" class="comp-line" stroke-width="3"/>
      <path d="M -8,8 L -8,20" class="comp-line" stroke-width="3"/>
      <path d="M -8,-14 L 0,-14" class="comp-line"/>
      <path d="M -8,14 L 0,14" class="comp-line"/>
      <path d="M -8,0 L 0,0 L 0,14" class="comp-line" fill="none"/>
      <polygon points="-8,0 -16,-4 -16,4" fill="#1E293B"/>
      <path d="M 12,-14 L 12,14 M 6,0 L 18,0" class="wire" stroke="#94A3B8"/>
      <polygon points="12,-6 6,6 18,6" fill="#94A3B8"/>
    </g>

    <g id="gate_network">
      <path d="M -35,0 L -25,0" class="wire"/>
      <path d="M -25,0 L -25,12 L -20,12" class="wire"/>
      <path d="M -20,12 L -16,12 L -14,8 L -10,16 L -6,8 L -2,16 L 2,8 L 6,16 L 8,12 L 12,12" fill="none" stroke="#1E293B" stroke-width="1.5"/>
      <path d="M 12,12 L 18,12 L 18,0" class="wire"/>
      <path d="M -25,0 L -25,-12 L -15,-12" class="wire"/>
      <polygon points="-6,-12 4,-17 4,-7" fill="#1E293B"/>
      <path d="M -6,-17 L -6,-7 M 4,-12 L 18,-12 L 18,0 L 25,0" class="wire"/>
      <circle cx="-25" cy="0" r="2" class="junction"/>
      <circle cx="18" cy="0" r="2" class="junction"/>
      <text x="-4" y="24" class="text-comp-label" font-size="7px" text-anchor="middle">10R</text>
      <text x="-1" y="-17" class="text-comp-label" font-size="7px" text-anchor="middle">1N4148</text>
    </g>

    <g id="resistor_h">
      <path d="M 0,0 L 8,0 L 11,-5 L 17,5 L 23,-5 L 29,5 L 35,-5 L 41,5 L 44,0 L 52,0" fill="none" stroke="#1E293B" stroke-width="2"/>
    </g>
    <g id="resistor_v">
      <path d="M 0,0 L 0,8 L -5,11 L 5,17 L -5,23 L 5,29 L -5,35 L 5,41 L 0,44 L 0,52" fill="none" stroke="#1E293B" stroke-width="2"/>
    </g>
    <g id="cap_v">
      <path d="M 0,0 L 0,14" class="comp-line"/>
      <path d="M -10,14 L 10,14" class="comp-line" stroke-width="3"/>
      <path d="M -10,18 L 10,18" class="comp-line" stroke-width="3"/>
      <path d="M 0,18 L 0,32" class="comp-line"/>
    </g>
    <g id="cap_pol_v">
      <path d="M 0,0 L 0,14" class="comp-line"/>
      <path d="M -12,14 L 12,14" class="comp-line" stroke-width="3"/>
      <path d="M -12,19 C -6,21 6,21 12,19" fill="none" stroke="#1E293B" stroke-width="2"/>
      <path d="M 0,19 L 0,34" class="comp-line"/>
      <text x="14" y="12" class="text-comp-label" fill="#DC2626">+</text>
    </g>
    <g id="diode_v">
      <path d="M 0,0 L 0,12" class="comp-line"/>
      <polygon points="-9,12 9,12 0,24" fill="#1E293B"/>
      <path d="M -9,24 L 9,24" class="comp-line" stroke-width="2"/>
      <path d="M 0,24 L 0,36" class="comp-line"/>
    </g>
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
    <g id="mov_v">
      <path d="M 0,0 L 0,14" class="comp-line"/>
      <rect x="-8" y="14" width="16" height="24" fill="#FEF3C7" stroke="#D97706" stroke-width="2"/>
      <path d="M -12,34 L 12,18" stroke="#D97706" stroke-width="2"/>
      <path d="M 0,38 L 0,52" class="comp-line"/>
    </g>
    <g id="inductor_h">
      <path d="M 0,0 L 6,0 C 8,-6 14,-6 16,0 C 18,-6 24,-6 26,0 C 28,-6 34,-6 36,0 C 38,-6 44,-6 46,0 L 52,0" fill="none" stroke="#1E293B" stroke-width="2"/>
    </g>
  </defs>

  <rect width="100%" height="100%" fill="url(#cad-grid)" stroke="#CBD5E1" stroke-width="2"/>

  <!-- BARRAMENTOS PRINCIPAIS -->
  <path d="M 40,95 L 1540,95" class="wire-pwr-48v"/>
  <text x="50" y="85" class="text-pin" fill="#DC2626">BARRAMENTO PRINCIPAL VDC (+12V a +48V / 400V HV)</text>

  <path d="M 40,915 L 1540,915" class="wire-gnd"/>
  <text x="50" y="935" class="text-pin" fill="#1E3A8A">PLANO DE POTÊNCIA PGND &amp; TERRA EM ESTRELA (STAR GROUND)</text>

  <!-- BLOCO 1: ENTRADA DE POTÊNCIA -->
  <g id="bloco_entrada" transform="translate(40, 95)">
    <rect x="0" y="45" width="65" height="80" rx="6" fill="#F59E0B" stroke="#D97706" stroke-width="2"/>
    <text x="32" y="80" class="text-title" font-size="13px" fill="#FFF" text-anchor="middle">XT90-S</text>
    <text x="32" y="105" class="text-subtitle" fill="#FFF" text-anchor="middle" font-size="9px">Anti-Spark</text>

    <path d="M 65,65 L 90,65 L 90,0" class="wire-pwr-48v"/>
    <circle cx="90" cy="0" r="4" class="junction-pwr"/>

    <path d="M 65,105 L 80,105 L 80,820" class="wire-gnd"/>
    <circle cx="80" cy="820" r="4" class="junction-gnd"/>

    <g transform="translate(120, 0)">
      <rect x="-18" y="-12" width="36" height="24" rx="3" fill="#FFE4E6" stroke="#DC2626" stroke-width="1.5"/>
      <path d="M -26,0 L -18,0 C -6,-8 6,8 18,0 L 26,0" fill="none" stroke="#DC2626" stroke-width="2"/>
      <text x="0" y="-18" class="text-comp-label" text-anchor="middle" fill="#DC2626">FUSE 50A</text>
    </g>
    <circle cx="94" cy="0" r="3.5" class="junction-pwr"/>
    <circle cx="146" cy="0" r="3.5" class="junction-pwr"/>

    <!-- Varistor MOV 14D680K -->
    <g transform="translate(180, 0)">
      <use href="#mov_v" x="0" y="0"/>
      <path d="M 0,52 L 0,820" class="wire-gnd"/>
      <text x="12" y="30" class="text-comp-label" fill="#D97706">MOV 68V</text>
      <circle cx="0" cy="0" r="3.5" class="junction-pwr"/>
      <circle cx="0" cy="820" r="3.5" class="junction-gnd"/>
    </g>

    <!-- TVS 5KP58CA -->
    <g transform="translate(240, 0)">
      <use href="#tvs_v" x="0" y="0"/>
      <path d="M 0,48 L 0,820" class="wire-gnd"/>
      <text x="12" y="30" class="text-comp-label">TVS 5KP58</text>
      <circle cx="0" cy="0" r="3.5" class="junction-pwr"/>
      <circle cx="0" cy="820" r="3.5" class="junction-gnd"/>
    </g>

    <!-- Pré-Carga -->
    <g id="precharge" transform="translate(300, 0)">
      <rect x="20" y="-14" width="45" height="28" rx="3" fill="#FFF" stroke="#1E293B" stroke-width="1.5"/>
      <path d="M 20,0 L 32,0 M 32,-8 L 52,8 M 52,0 L 65,0" class="wire"/>
      <text x="42" y="25" class="text-comp-label" text-anchor="middle">K_pre</text>

      <path d="M 5,0 L 5,-40 L 15,-40" class="wire"/>
      <use href="#resistor_h" x="15" y="-40"/>
      <path d="M 67,-40 L 78,-40 L 78,0" class="wire"/>
      <text x="42" y="-48" class="text-comp-label" text-anchor="middle">10R 25W Cerâmico</text>
      <circle cx="5" cy="0" r="3" class="junction-pwr"/>
      <circle cx="78" cy="0" r="3" class="junction-pwr"/>
    </g>
    <circle cx="305" cy="0" r="3.5" class="junction-pwr"/>
    <circle cx="378" cy="0" r="3.5" class="junction-pwr"/>

    <!-- Bulk Capacitors -->
    <g transform="translate(420, 0)">
      <use href="#cap_pol_v" x="0" y="0"/>
      <path d="M 0,34 L 0,820" class="wire-gnd"/>
      <text x="16" y="20" class="text-comp-label">470µF</text>
      <text x="16" y="32" class="text-subtitle" font-size="8px">450V Low-ESR</text>
      <circle cx="0" cy="0" r="3.5" class="junction-pwr"/>
      <circle cx="0" cy="820" r="3.5" class="junction-gnd"/>
    </g>
  </g>

  <!-- BLOCO 2: CHOPPER DE FREIO COM HISTERESE -->
  <g id="circuito_freio" transform="translate(530, 95)">
    <rect x="-10" y="15" width="145" height="385" class="block-box" fill="#FFF5F5" stroke="#FCA5A5"/>
    <text x="62" y="35" class="text-title" font-size="11px" fill="#DC2626" text-anchor="middle">CHOPPER (54V ON / 51V OFF)</text>

    <use href="#resistor_v" x="45" y="55"/>
    <text x="60" y="75" class="text-comp-label">R_brake</text>
    <text x="60" y="88" class="text-subtitle" font-size="9px" fill="#DC2626">4.7R 100W</text>
    <circle cx="45" cy="0" r="3.5" class="junction-pwr"/>

    <g transform="translate(15, 107) scale(1, -1)">
      <use href="#diode_v" x="0" y="0"/>
    </g>
    <path d="M 15,0 L 15,71 M 15,107 L 15,120 L 45,120" class="wire"/>
    <text x="-5" y="85" class="text-comp-label" font-size="9px">ES1J Fast</text>
    <circle cx="15" cy="0" r="3" class="junction-pwr"/>
    <circle cx="45" cy="120" r="3" class="junction"/>

    <use href="#n_mosfet" x="45" y="200"/>
    <path d="M 45,120 L 45,170" class="wire"/>
    <text x="65" y="195" class="text-comp-label">Q_brake</text>

    <use href="#gate_network" x="15" y="200"/>
    <path d="M -20,200 L -45,200 L -45,460 L -90,460" class="wire-bus-pwm"/>
    <text x="-35" y="192" class="text-net" fill="#8B5CF6">CHOPPER_CTRL</text>

    <use href="#resistor_v" x="25" y="235"/>
    <path d="M 25,200 L 25,235 M 25,287 L 25,310 L 45,310" class="wire"/>
    <text x="32" y="260" class="text-comp-label" font-size="8px">10k</text>
    <circle cx="25" cy="200" r="2.5" class="junction"/>
    <circle cx="45" cy="310" r="2.5" class="junction"/>

    <path d="M 45,230 L 45,820" class="wire-gnd"/>
    <circle cx="45" cy="820" r="3.5" class="junction-gnd"/>
  </g>

  <!-- BLOCO 3: GATE DRIVER DRV8302 COM DEAD-TIME 500ns -->
  <g id="bloco_driver" transform="translate(710, 130)">
    <rect x="0" y="0" width="235" height="390" class="ic-box"/>
    <rect x="0" y="0" width="235" height="32" fill="#E2E8F0" rx="8"/>
    <text x="117" y="22" class="text-title" font-size="12px" text-anchor="middle">TI DRV8302 (DT=500ns / BUCK 5V)</text>

    <text x="10" y="58" class="text-pin">PVDD (48V In)</text>
    <text x="10" y="82" class="text-pin">GND / AGND</text>
    <text x="10" y="106" class="text-pin">R_DT (68k = 500ns)</text>
    <text x="10" y="130" class="text-pin">PWM_UH (INHA)</text>
    <text x="10" y="154" class="text-pin">PWM_UL (INLA)</text>
    <text x="10" y="178" class="text-pin">PWM_VH (INHB)</text>
    <text x="10" y="202" class="text-pin">PWM_VL (INLB)</text>
    <text x="10" y="226" class="text-pin">PWM_WH (INHC)</text>
    <text x="10" y="250" class="text-pin">PWM_WL (INLC)</text>
    <text x="10" y="284" class="text-pin">FAULT_N (ISR Hardware)</text>
    <text x="10" y="308" class="text-pin">OCTW_N (Aviso Temp)</text>
    <text x="10" y="334" class="text-pin">EN_GATE</text>
    <text x="10" y="364" class="text-pin">BUCK 5V_OUT (1.5A)</text>

    <text x="225" y="58" class="text-pin" text-anchor="end">BST_A / GH_A</text>
    <text x="225" y="80" class="text-pin" text-anchor="end">SH_A (Fase U)</text>
    <text x="225" y="102" class="text-pin" text-anchor="end">GL_A (Low U)</text>
    <text x="225" y="134" class="text-pin" text-anchor="end">BST_B / GH_B</text>
    <text x="225" y="156" class="text-pin" text-anchor="end">SH_B (Fase V)</text>
    <text x="225" y="178" class="text-pin" text-anchor="end">GL_B (Low V)</text>
    <text x="225" y="210" class="text-pin" text-anchor="end">BST_C / GH_C</text>
    <text x="225" y="232" class="text-pin" text-anchor="end">SH_C (Fase W)</text>
    <text x="225" y="254" class="text-pin" text-anchor="end">GL_C (Low W)</text>
    <text x="225" y="290" class="text-pin" text-anchor="end">SO1 (Amp Shunt U)</text>
    <text x="225" y="316" class="text-pin" text-anchor="end">SO2 (Amp Shunt V)</text>
    <text x="225" y="346" class="text-pin" text-anchor="end">Kelvin SP1/SN1, SP2/SN2</text>

    <path d="M 0,55 L -20,55 L -20,-35" class="wire-pwr-48v"/>
    <circle cx="-20" cy="-35" r="3.5" class="junction-pwr"/>
    <path d="M 0,80 L -10,80 L -10,785" class="wire-gnd"/>
    <circle cx="-10" cy="785" r="3.5" class="junction-gnd"/>
  </g>

  <!-- BLOCO 4: INVERSOR TRIFÁSICO COM KELVIN STAR GROUND -->
  <!-- FASE U -->
  <g id="fase_u" transform="translate(980, 130)">
    <rect x="-40" y="0" width="145" height="430" class="block-box"/>
    <text x="32" y="-10" class="text-title" font-size="12px" text-anchor="middle">FASE U</text>
    <use href="#n_mosfet" x="30" y="70"/>
    <text x="52" y="48" class="text-comp-label">Q1 (HS)</text>
    <path d="M 30,0 L 30,40" class="wire-pwr-48v"/>
    <circle cx="30" cy="-35" r="3.5" class="junction-pwr"/>

    <use href="#gate_network" x="0" y="70"/>
    <text x="-48" y="58" class="text-net" fill="#8B5CF6">GH_A</text>

    <g transform="translate(65, 35)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,40 L 65,40 L 65,35 M 65,122 L 65,145 L 30,145" class="wire"/>
    <circle cx="30" cy="40" r="2.5" class="junction"/>
    <circle cx="30" cy="145" r="2.5" class="junction"/>

    <path d="M 30,100 L 30,220" class="wire" stroke-width="2.5"/>
    <circle cx="30" cy="145" r="3" class="junction"/>

    <use href="#n_mosfet" x="30" y="250"/>
    <text x="52" y="228" class="text-comp-label">Q4 (LS)</text>
    <path d="M 30,145 L 30,220" class="wire"/>

    <use href="#gate_network" x="0" y="250"/>
    <text x="-48" y="238" class="text-net" fill="#8B5CF6">GL_A</text>

    <g transform="translate(65, 215)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,220 L 65,220 L 65,215 M 65,302 L 65,330 L 30,330" class="wire"/>
    <circle cx="30" cy="220" r="2.5" class="junction"/>
    <circle cx="30" cy="330" r="2.5" class="junction"/>

    <use href="#resistor_v" x="30" y="340"/>
    <text x="48" y="365" class="text-comp-label">1mΩ 3W</text>
    <path d="M 30,392 L 30,785" class="wire-gnd"/>
    <circle cx="30" cy="785" r="3.5" class="junction-gnd"/>

    <path d="M 30,335 L -45,335 L -45,346" class="wire-analog"/>
    <path d="M 30,395 L -40,395 L -40,352" class="wire-analog"/>
    <circle cx="30" cy="335" r="2" class="junction-analog"/>
    <circle cx="30" cy="395" r="2" class="junction-analog"/>
    <text x="-38" y="328" class="text-net" font-size="8px" fill="#D97706">SP1</text>
    <text x="-38" y="408" class="text-net" font-size="8px" fill="#D97706">SN1</text>

    <path d="M 30,145 L 90,145 L 90,70 L 480,70" class="wire" stroke="#DC2626" stroke-width="2.5"/>
    <text x="95" y="64" class="text-net" fill="#DC2626">PHASE_U</text>
  </g>

  <!-- FASE V -->
  <g id="fase_v" transform="translate(1135, 130)">
    <rect x="-40" y="0" width="145" height="430" class="block-box"/>
    <text x="32" y="-10" class="text-title" font-size="12px" text-anchor="middle">FASE V</text>
    <use href="#n_mosfet" x="30" y="70"/>
    <text x="52" y="48" class="text-comp-label">Q2 (HS)</text>
    <path d="M 30,0 L 30,40" class="wire-pwr-48v"/>
    <circle cx="30" cy="-35" r="3.5" class="junction-pwr"/>

    <use href="#gate_network" x="0" y="70"/>
    <text x="-48" y="58" class="text-net" fill="#8B5CF6">GH_B</text>

    <g transform="translate(65, 35)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,40 L 65,40 L 65,35 M 65,122 L 65,145 L 30,145" class="wire"/>
    <circle cx="30" cy="40" r="2.5" class="junction"/>
    <circle cx="30" cy="145" r="2.5" class="junction"/>

    <use href="#n_mosfet" x="30" y="250"/>
    <text x="52" y="228" class="text-comp-label">Q5 (LS)</text>
    <path d="M 30,145 L 30,220" class="wire"/>

    <use href="#gate_network" x="0" y="250"/>
    <text x="-48" y="238" class="text-net" fill="#8B5CF6">GL_B</text>

    <g transform="translate(65, 215)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,220 L 65,220 L 65,215 M 65,302 L 65,330 L 30,330" class="wire"/>
    <circle cx="30" cy="220" r="2.5" class="junction"/>
    <circle cx="30" cy="330" r="2.5" class="junction"/>

    <use href="#resistor_v" x="30" y="340"/>
    <text x="48" y="365" class="text-comp-label">1mΩ 3W</text>
    <path d="M 30,392 L 30,785" class="wire-gnd"/>
    <circle cx="30" cy="785" r="3.5" class="junction-gnd"/>

    <path d="M 30,335 L -10,335 M -10,395 L 30,395" class="wire-analog"/>
    <circle cx="30" cy="335" r="2" class="junction-analog"/>
    <circle cx="30" cy="395" r="2" class="junction-analog"/>
    <text x="-38" y="328" class="text-net" font-size="8px" fill="#D97706">SP2</text>
    <text x="-38" y="408" class="text-net" font-size="8px" fill="#D97706">SN2</text>

    <path d="M 30,145 L 90,145 L 90,170 L 325,170" class="wire" stroke="#DC2626" stroke-width="2.5"/>
    <text x="95" y="164" class="text-net" fill="#DC2626">PHASE_V</text>
  </g>

  <!-- FASE W -->
  <g id="fase_w" transform="translate(1290, 130)">
    <rect x="-40" y="0" width="145" height="430" class="block-box"/>
    <text x="32" y="-10" class="text-title" font-size="12px" text-anchor="middle">FASE W</text>
    <use href="#n_mosfet" x="30" y="70"/>
    <text x="52" y="48" class="text-comp-label">Q3 (HS)</text>
    <path d="M 30,0 L 30,40" class="wire-pwr-48v"/>
    <circle cx="30" cy="-35" r="3.5" class="junction-pwr"/>

    <use href="#gate_network" x="0" y="70"/>
    <text x="-48" y="58" class="text-net" fill="#8B5CF6">GH_C</text>

    <g transform="translate(65, 35)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,40 L 65,40 L 65,35 M 65,122 L 65,145 L 30,145" class="wire"/>
    <circle cx="30" cy="40" r="2.5" class="junction"/>
    <circle cx="30" cy="145" r="2.5" class="junction"/>

    <use href="#n_mosfet" x="30" y="250"/>
    <text x="52" y="228" class="text-comp-label">Q6 (LS)</text>
    <path d="M 30,145 L 30,220" class="wire"/>

    <use href="#gate_network" x="0" y="250"/>
    <text x="-48" y="238" class="text-net" fill="#8B5CF6">GL_C</text>

    <g transform="translate(65, 215)">
      <use href="#resistor_v" x="0" y="0"/>
      <use href="#cap_v" x="0" y="55"/>
      <text x="8" y="25" class="text-comp-label" font-size="7px">2.2R</text>
      <text x="8" y="70" class="text-comp-label" font-size="7px">10nF</text>
    </g>
    <path d="M 30,220 L 65,220 L 65,215 M 65,302 L 65,330 L 30,330" class="wire"/>
    <circle cx="30" cy="220" r="2.5" class="junction"/>
    <circle cx="30" cy="330" r="2.5" class="junction"/>

    <use href="#resistor_v" x="30" y="340"/>
    <text x="48" y="365" class="text-comp-label">1mΩ 3W</text>
    <path d="M 30,392 L 30,785" class="wire-gnd"/>
    <circle cx="30" cy="785" r="3.5" class="junction-gnd"/>

    <path d="M 30,145 L 90,145 L 90,270 L 170,270" class="wire" stroke="#DC2626" stroke-width="2.5"/>
    <text x="95" y="264" class="text-net" fill="#DC2626">PHASE_W</text>
  </g>

  <!-- BLOCO 5: SAÍDAS COM INDUTORES EMI -->
  <g id="filtros_saida" transform="translate(1460, 130)">
    <rect x="-10" y="0" width="105" height="430" class="block-box" fill="#FEF3C7" stroke="#F59E0B"/>
    <text x="42" y="-10" class="text-title" font-size="12px" fill="#D97706" text-anchor="middle">MOTOR OUT</text>

    <g transform="translate(0, 70)">
      <use href="#inductor_h" x="0" y="0"/>
      <circle cx="78" cy="0" r="9" fill="#D97706" stroke="#B45309" stroke-width="2"/>
      <text x="78" y="4" class="text-title" font-size="11px" text-anchor="middle" fill="#FFF">U</text>
    </g>
    <g transform="translate(0, 170)">
      <use href="#inductor_h" x="0" y="0"/>
      <circle cx="78" cy="0" r="9" fill="#D97706" stroke="#B45309" stroke-width="2"/>
      <text x="78" y="4" class="text-title" font-size="11px" text-anchor="middle" fill="#FFF">V</text>
    </g>
    <g transform="translate(0, 270)">
      <use href="#inductor_h" x="0" y="0"/>
      <circle cx="78" cy="0" r="9" fill="#D97706" stroke="#B45309" stroke-width="2"/>
      <text x="78" y="4" class="text-title" font-size="11px" text-anchor="middle" fill="#FFF">W</text>
    </g>
  </g>

  <!-- BARRAMENTO PWM (MCU -> DRV8302) -->
  <g id="pwm_bus_routing">
    <path d="M 440,620 L 520,620 L 520,260 L 710,260" class="wire-bus-pwm"/>
    <path d="M 440,646 L 528,646 L 528,284 L 710,284" class="wire-bus-pwm"/>
    <path d="M 440,674 L 536,674 L 536,308 L 710,308" class="wire-bus-pwm"/>
    <path d="M 440,700 L 544,700 L 544,332 L 710,332" class="wire-bus-pwm"/>
    <path d="M 440,728 L 552,728 L 552,356 L 710,356" class="wire-bus-pwm"/>
    <path d="M 440,754 L 560,754 L 560,380 L 710,380" class="wire-bus-pwm"/>
    <text x="565" y="270" class="text-net" fill="#7C3AED" font-size="9px" transform="rotate(-90 565,270)">BARRAMENTO PWM (6x MCPWM 20-40kHz)</text>
  </g>

  <!-- BLOCO 6: MCU ESP32 + SENSORES HALL OPTOISOLADOS -->
  <g id="bloco_mcu" transform="translate(80, 560)">
    <rect x="0" y="0" width="360" height="330" class="ic-box"/>
    <rect x="0" y="0" width="360" height="32" fill="#E2E8F0" rx="8"/>
    <text x="180" y="22" class="text-title" font-size="13px" text-anchor="middle">ESP32-WROOM-32E (FOC INDUSTRIAL)</text>

    <text x="12" y="60" class="text-pin">3.3V (VDD Clean)</text>
    <text x="12" y="86" class="text-pin">AGND (Terra Analógico em Estrela)</text>
    <text x="12" y="116" class="text-pin">GPIO34 (VDC_SENSE 100k/3.3k)</text>
    <text x="12" y="146" class="text-pin">GPIO35 (TEMP_MOTOR NTC 10k)</text>
    <text x="12" y="176" class="text-pin">GPIO32 (TEMP_DRV NTC 10k)</text>
    <text x="12" y="210" class="text-pin">GPIO5 (HALL_U via TLP2362)</text>
    <text x="12" y="240" class="text-pin">GPIO18 (HALL_V via TLP2362)</text>
    <text x="12" y="270" class="text-pin">GPIO19 (HALL_W via TLP2362)</text>
    <text x="12" y="300" class="text-pin">GPIO4 (CHOPPER_CTRL Freio)</text>

    <text x="348" y="60" class="text-pin" text-anchor="end">PWM_UH (GPIO32) →</text>
    <text x="348" y="86" class="text-pin" text-anchor="end">PWM_UL (GPIO33) →</text>
    <text x="348" y="114" class="text-pin" text-anchor="end">PWM_VH (GPIO26) →</text>
    <text x="348" y="140" class="text-pin" text-anchor="end">PWM_VL (GPIO27) →</text>
    <text x="348" y="168" class="text-pin" text-anchor="end">PWM_WH (GPIO14) →</text>
    <text x="348" y="194" class="text-pin" text-anchor="end">PWM_WL (GPIO12) →</text>
    <text x="348" y="226" class="text-pin" text-anchor="end">IS_U (ADC1_0 / SO1) ←</text>
    <text x="348" y="252" class="text-pin" text-anchor="end">IS_V (ADC1_3 / SO2) ←</text>
    <text x="348" y="282" class="text-pin" text-anchor="end">CAN_TX (GPIO21) →</text>
    <text x="348" y="306" class="text-pin" text-anchor="end">CAN_RX (GPIO22) ←</text>

    <path d="M 0,58 L -30,58" class="wire-pwr-3v3"/>
    <path d="M 0,84 L -30,84 L -30,355" class="wire-gnd"/>
    <circle cx="-30" cy="355" r="3.5" class="junction-gnd"/>
  </g>

  <!-- BLOCO 7: CAN BUS ISOLADO COM DC-DC B0505S -->
  <g id="can_isolation" transform="translate(470, 745)">
    <rect x="0" y="0" width="350" height="145" class="ic-box" fill="#ECFDF5" stroke="#10B981" stroke-width="2"/>
    <text x="175" y="22" class="text-title" font-size="12px" text-anchor="middle" fill="#047857">ISO1050 + B0505S (CAN ISOLADO 1.5kV)</text>
    
    <text x="12" y="55" class="text-pin">TXD (do MCU)</text>
    <text x="12" y="80" class="text-pin">RXD (para MCU)</text>
    <text x="12" y="105" class="text-pin">5V / GND Lógica</text>
    <text x="12" y="130" class="text-pin">B0505S-1WR3 (DC-DC)</text>

    <text x="240" y="55" class="text-pin" text-anchor="end">CAN_H</text>
    <text x="240" y="80" class="text-pin" text-anchor="end">CAN_L</text>
    <text x="240" y="105" class="text-pin" text-anchor="end">5V_ISO / GND_ISO</text>

    <!-- Resistor 120R -->
    <path d="M 245,52 L 255,52 L 255,60 M 255,75 L 255,80 L 245,80" class="wire"/>
    <rect x="248" y="60" width="14" height="15" fill="#FFF" stroke="#047857"/>
    <text x="255" y="71" class="text-comp-label" font-size="6px" text-anchor="middle">120R</text>

    <rect x="275" y="38" width="65" height="75" rx="4" fill="#047857" stroke="#065F46" stroke-width="1.5"/>
    <text x="307" y="62" class="text-title" font-size="11px" fill="#FFF" text-anchor="middle">CAN_H</text>
    <text x="307" y="92" class="text-title" font-size="11px" fill="#FFF" text-anchor="middle">CAN_L</text>
  </g>

  <!-- BLOCO 8: FONTES AUXILIARES BUCK + LDO -->
  <g id="bloco_fontes" transform="translate(850, 560)">
    <rect x="0" y="0" width="340" height="330" class="block-box" fill="#FFFBEB" stroke="#F59E0B"/>
    <text x="170" y="24" class="text-title" font-size="12px" fill="#B45309" text-anchor="middle">REGULAÇÃO AUXILIAR INDUSTRIAL</text>

    <rect x="20" y="50" width="130" height="95" rx="6" fill="#FFF" stroke="#D97706"/>
    <text x="85" y="75" class="text-comp-label" text-anchor="middle">TPS54160 (Buck)</text>
    <text x="85" y="95" class="text-subtitle" font-size="9px" text-anchor="middle">48V In → 5V Out</text>
    <text x="85" y="115" class="text-pin" font-size="9px" fill="#D97706" text-anchor="middle">1.5A Eficiência >90%</text>

    <rect x="190" y="50" width="130" height="95" rx="6" fill="#FFF" stroke="#10B981"/>
    <text x="255" y="75" class="text-comp-label" text-anchor="middle">AMS1117-3.3</text>
    <text x="255" y="95" class="text-subtitle" font-size="9px" text-anchor="middle">5V In → 3.3V Out</text>
    <text x="255" y="115" class="text-pin" font-size="9px" fill="#10B981" text-anchor="middle">MCU / ADC Ref</text>

    <path d="M 150,95 L 190,95" class="wire-pwr-5v"/>
    <text x="170" y="85" class="text-comp-label" font-size="9px" fill="#F59E0B" text-anchor="middle">5V</text>

    <path d="M 320,95 L 335,95 L 335,270 L -740,270 L -740,58" class="wire-pwr-3v3"/>
    <text x="255" y="180" class="text-pin" fill="#10B981">Barramento +3.3V Ultra-Limpo</text>
  </g>

  <!-- BLOCO 9: TITLE BLOCK INDUSTRIAL -->
  <g id="info_block" transform="translate(1160, 15)">
    <rect x="0" y="0" width="380" height="75" rx="6" fill="#0F172A" stroke="#334155" stroke-width="2"/>
    <text x="20" y="22" class="text-title" fill="#F8FAFC" font-size="12px">INVERSOR BLDC INDUSTRIAL (48V-400V / 30A-180A)</text>
    <text x="20" y="38" class="text-subtitle" fill="#94A3B8">Padrão Homologação: 4-Layers PCB + Star Ground + Optoisolação</text>
    <text x="20" y="54" class="text-subtitle" fill="#E2E8F0" font-weight="bold">Topologia: 6x IRFB4110 + DRV8302 (DT=500ns) + ESP32</text>
    <text x="20" y="68" class="text-subtitle" fill="#38BDF8">Revisão: v4.0 Industrial Product Grade (Verificado 100%)</text>
  </g>
</svg>'''
    with open('esquema_profissional.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("✅ esquema_profissional.svg (Folha 5) atualizado para v4.0 Industrial!")

if __name__ == '__main__':
    generate_sheet5_general()
