#!/usr/bin/env python3
"""Gerador de schematic KiCad REAL e válido — Controladora BLDC 400V/50A.

Causa-raiz corrigida: o schematic.kicad_sch antigo era um documento DESCRITIVO
(texto + (property ...) soltos no nível raiz, sem símbolos/pinos/fios/netlists),
o que o parser KiCad 9 rejeita ("Houve uma falha ao ler o esquemático").

Este script gera um arquivo .kicad_sch conforme o formato S-expression real,
espelhando a estrutura do ECL-OR.kicad_sch de referência (KiCad oficial):
  (kicad_sch ...) → (lib_symbols ...) → (symbol ...) instâncias → wires →
  junctions → (sheet_instances ...) → (symbol_instances ...)

Circuito: entrada 400V → fusível → banco de capacitores → 6 MOSFETs
(3 meias-pontes) → shunts → DRV8302 → ESP32 + GND.
"""

import uuid
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'schematic.kicad_sch')


def u():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Construção dos lib_symbols (definições de símbolo com gráficos e pinos)
# ---------------------------------------------------------------------------

def lib_symbol(name, pins, graphics, power=False, extra_props=None):
    """pins: lista de (numero, nome, (x, y), angle, etype, length, hide)
       graphics: string com os elementos gráficos (rectangle/polyline/pin)"""
    kw = ' (power)' if power else ''
    pn_off = ' (pin_names (offset 0) hide)' if not power else ' (pin_names (offset 0))'
    s = f'    (symbol "{name}"{kw}{pn_off} (in_bom yes) (on_board yes)\n'
    if power:
        s += '      (property "Reference" "#PWR" (id 0) (at 0 -6.35 0)\n        (effects (font (size 1.27 1.27)) hide)\n      )\n'
        s += '      (property "Value" "' + name.split(':')[-1] + '" (id 1) (at 0 -3.81 0)\n        (effects (font (size 1.27 1.27)))\n      )\n'
    else:
        s += '      (property "Reference" "?" (id 0) (at 0 5.08 0)\n        (effects (font (size 1.27 1.27)))\n      )\n'
        s += '      (property "Value" "' + name.split(':')[-1] + '" (id 1) (at 0 -5.08 0)\n        (effects (font (size 1.27 1.27)))\n      )\n'
    s += '      (property "Footprint" "" (id 2) (at 0 0 0)\n        (effects (font (size 1.27 1.27)) hide)\n      )\n'
    s += '      (property "Datasheet" "~" (id 3) (at 0 0 0)\n        (effects (font (size 1.27 1.27)) hide)\n      )\n'
    if extra_props:
        for k, v, idx in extra_props:
            s += f'      (property "{k}" "{v}" (id {idx}) (at 0 0 0)\n        (effects (font (size 1.27 1.27)) hide)\n      )\n'
    # sub-símbolo 0: gráficos
    s += f'      (symbol "{name.split(":")[-1]}_0_1"\n'
    s += graphics
    s += '      )\n'
    # sub-símbolo 1: pinos
    s += f'      (symbol "{name.split(":")[-1]}_1_1"\n'
    for num, pname, (x, y), ang, etype, length, hide in pins:
        s += (f'        (pin {etype} line (at {x} {y} {ang}) (length {length})' +
              (' hide' if hide else '') + '\n')
        s += f'          (name "{pname}" (effects (font (size 1.27 1.27))))\n'
        s += f'          (number "{num}" (effects (font (size 1.27 1.27))))\n'
        s += '        )\n'
    s += '      )\n'
    s += '    )\n'
    return s


def graphics_rect(name, x1, y1, x2, y2):
    return (f'        (rectangle (start {x1} {y1}) (end {x2} {y2})\n'
            f'          (stroke (width 0.254) (type default) (color 0 0 0 0))\n'
            f'          (fill (type none))\n'
            f'        )\n')


def build_lib_symbols():
    L = []
    # --- Resistor (vertical) ---
    L.append(lib_symbol(
        'MotorCtrl:R',
        [('1', '~', (0, 1.27), 270, 'passive', 0.254, False),
         ('2', '~', (0, -1.27), 90, 'passive', 0.254, False)],
        graphics_rect('R', -0.762, 0.508, 0.762, -0.508)))
    # --- Capacitor ---
    L.append(lib_symbol(
        'MotorCtrl:C',
        [('1', '~', (0, 1.524), 270, 'passive', 0.254, False),
         ('2', '~', (0, -1.524), 90, 'passive', 0.254, False)],
        graphics_rect('C', -0.762, 1.016, 0.762, -1.016)))
    # --- MOSFET N (TO-247): G esquerda, D topo, S base ---
    L.append(lib_symbol(
        'MotorCtrl:Q_NMOS',
        [('1', 'G', (-3.81, 0), 0, 'input', 0.254, False),
         ('2', 'D', (0, 3.81), 270, 'passive', 0.254, False),
         ('3', 'S', (0, -3.81), 90, 'passive', 0.254, False)],
        graphics_rect('Q', -1.524, 3.556, 1.524, -3.556)))
    # --- DRV8302 (rectangular, pinos laterais) ---
    drv_pins = []
    # pinos da esquerda (entrada PWM/controle)
    for i, pn in enumerate(['IN_A', 'IN_B', 'IN_C', 'EN', 'nFAULT', 'GND']):
        drv_pins.append((str(i + 1), pn, (-7.62, 7.62 - i * 2.54), 0, 'input', 0.254, False))
    # pinos da direita (gate/saída)
    for i, pn in enumerate(['GHA', 'GLA', 'GHB', 'GLB', 'GHC', 'GLC', 'DVDD']):
        drv_pins.append((str(i + 7), pn, (7.62, 10.16 - i * 2.54), 180, 'output', 0.254, False))
    L.append(lib_symbol('MotorCtrl:DRV8302', drv_pins,
                        graphics_rect('DRV', -5.08, 15.24, 5.08, -15.24)))
    # --- ESP32-WROOM-32E (retangular, pinos laterais) ---
    esp_pins = []
    for i, pn in enumerate(['3V3', 'GPIO32', 'GPIO33', 'GPIO26', 'GPIO25', 'GPIO23',
                            'GPIO36', 'GPIO39', 'GPIO34', 'GPIO35']):
        esp_pins.append((str(i + 1), pn, (-7.62, 11.43 - i * 2.54), 0, 'bidirectional', 0.254, False))
    for i, pn in enumerate(['GND', 'GPIO5', 'GPIO18', 'GPIO19', 'GPIO16', 'GPIO17',
                            'VCC3V3', 'EN']):
        esp_pins.append((str(i + 11), pn, (7.62, 11.43 - i * 2.54), 180, 'bidirectional', 0.254, False))
    L.append(lib_symbol('MotorCtrl:ESP32', esp_pins,
                        graphics_rect('ESP', -5.08, 17.78, 5.08, -17.78)))
    # --- GND ---
    g = ('        (polyline\n          (pts\n            (xy 0 0) (xy 0 -1.27)\n            (xy 1.27 -1.27) (xy 0 -2.54)\n            (xy -1.27 -1.27) (xy 0 -1.27)\n          )\n'
         '          (stroke (width 0) (type default) (color 0 0 0 0))\n'
         '          (fill (type none))\n        )\n')
    L.append(lib_symbol('power:GND',
                        [('1', 'GND', (0, 0), 270, 'power_in', 0, True)],
                        g, power=True))
    # --- +400V ---
    v = ('        (polyline\n          (pts\n            (xy 0 0) (xy 0 2.54)\n          )\n'
         '          (stroke (width 0) (type default) (color 0 0 0 0))\n'
         '          (fill (type none))\n        )\n')
    L.append(lib_symbol('power:+400V',
                        [('1', '+400V', (0, 0), 90, 'power_in', 0, True)],
                        v, power=True))
    return L


# ---------------------------------------------------------------------------
# Instâncias
# ---------------------------------------------------------------------------

def instance(lib_id, ref, value, at, pins, angle=0):
    """pins: lista de números já colocados; retorna (block, path, ref, value)"""
    pu = u()
    s = (f'  (symbol (lib_id "{lib_id}") (at {at[0]} {at[1]} {angle}) (unit 1)\n'
         f'    (in_bom yes) (on_board yes)\n'
         f'    (uuid {pu})\n')
    s += (f'    (property "Reference" "{ref}" (id 0) (at {at[0] + 2.54} {at[1] - 7.62} 0)\n'
          f'      (effects (font (size 1.27 1.27)))\n    )\n')
    s += (f'    (property "Value" "{value}" (id 1) (at {at[0] + 2.54} {at[1] + 7.62} 0)\n'
          f'      (effects (font (size 1.27 1.27)))\n    )\n')
    s += (f'    (property "Footprint" "" (id 2) (at {at[0]} {at[1]} 0)\n'
          f'      (effects (font (size 1.27 1.27)) hide)\n    )\n')
    s += (f'    (property "Datasheet" "~" (id 3) (at {at[0]} {at[1]} 0)\n'
          f'      (effects (font (size 1.27 1.27)) hide)\n    )\n')
    for pn in pins:
        s += f'    (pin "{pn}" (uuid {u()}))\n'
    s += '  )\n'
    return s, pu, ref, value


def wire(x1, y1, x2, y2):
    return (f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))'
            f' (stroke (width 0) (type default)) (uuid {u()}))\n')


def junction(x, y):
    return f'  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {u()}))\n'


def build_schematic():
    out = []
    out.append('(kicad_sch (version 20230121) (generator eeschema)\n')
    out.append(f'  (uuid {u()})\n')
    out.append('  (paper "A4")\n\n')
    out.append('  (lib_symbols\n')
    for ls in build_lib_symbols():
        out.append(ls)
    out.append('  )\n\n')

    insts = []
    # --- Fonte 400V + fusível + capacitores ---
    insts.append(instance('power:+400V', '#PWR01', '+400V', (30, 50), [1]))
    insts.append(instance('MotorCtrl:R', 'F1', '50A', (30, 120), [1, 2]))
    insts.append(instance('MotorCtrl:C', 'C1', '470uF', (30, 200), [1, 2]))
    insts.append(instance('MotorCtrl:C', 'C2', '470uF', (30, 290), [1, 2]))

    # --- 6 MOSFETs (3 meias-pontes) ---
    # Cada fase: HS em cima (D em +400V, S no nodo de fase), LS embaixo (D no
    # nodo de fase, S em shunt)
    mos = []
    m = 0
    for ph, x in [('U', 150), ('V', 250), ('W', 350)]:
        m += 1
        mos.append(instance('MotorCtrl:Q_NMOS', f'Q{m}', 'IPP65R600P7', (x, 110), [1, 2, 3]))
        m += 1
        mos.append(instance('MotorCtrl:Q_NMOS', f'Q{m}', 'IPP65R600P7', (x, 210), [1, 2, 3]))
    insts += mos

    # --- shunts (medida de corrente) + GND ---
    for ph, x in [('U', 150), ('V', 250), ('W', 350)]:
        insts.append(instance('MotorCtrl:R', f'Rsh_{ph}', '0.001R', (x, 320), [1, 2]))
        insts.append(instance('power:GND', f'#PWR02_{ph}', 'GND', (x, 360), [1]))

    # --- DRV8302 + ESP32 ---
    insts.append(instance('MotorCtrl:DRV8302', 'U2', 'DRV8302', (110, 480),
                          [str(i) for i in range(1, 14)]))
    insts.append(instance('MotorCtrl:ESP32', 'U1', 'ESP32-WROOM-32E', (110, 650),
                          [str(i) for i in range(1, 19)]))

    for blk, pu, ref, value in insts:
        out.append(blk)

    # --- Fios com coordenadas EXATAS nos pinos (nets reais no netlist) ---
    # Pinos calculados a partir dos offsets dos lib_symbols:
    #   R: pin1 (0,+1.27)[inf], pin2 (0,-1.27)[sup]
    #   C: pin1 (0,+1.524), pin2 (0,-1.524)
    #   Q_NMOS: G(-3.81,0) D(0,+3.81) S(0,-3.81)
    #   DRV8302: esq inputs x=-7.62, dir gates x=+7.62
    #   power:GND e +400V: pino em (0,0)

    # --- Barramento +400V (fonte → fusível → capacitores → drenos HS) ---
    out.append(wire(30, 50, 30, 118.73))          # #PWR01 → F1 pin2 (sup)
    out.append(junction(30, 50))
    out.append(wire(30, 121.27, 30, 198.476))     # F1 pin1 (inf) → C1 pin2 (sup)
    out.append(junction(30, 121.27))
    out.append(wire(30, 201.524, 30, 288.476))    # C1 pin1 (inf) → C2 pin2 (sup)
    out.append(junction(30, 201.524))
    out.append(wire(30, 291.524, 30, 113.81))     # C2 pin1 (inf) → linha dos drenos
    out.append(junction(30, 113.81))
    # barramento horizontal na altura do Dreno (y=113.81 = 110+3.81)
    out.append(wire(30, 113.81, 150, 113.81))
    out.append(junction(150, 113.81))
    out.append(wire(150, 113.81, 250, 113.81))
    out.append(junction(250, 113.81))
    out.append(wire(250, 113.81, 350, 113.81))
    out.append(junction(350, 113.81))

    # --- Nodo de fase por coluna: HS.S (106.19) → LS.D (213.81) ---
    # dividido para conectar também o S do LS (206.19) e o shunt
    for x in [150, 250, 350]:
        out.append(wire(x, 106.19, x, 206.19))    # HS.S → LS.S
        out.append(junction(x, 106.19))
        out.append(wire(x, 206.19, x, 213.81))    # LS.S → LS.D
        out.append(junction(x, 206.19))
        # LS.S → shunt (topo do shunt: pin2 em y=318.73)
        out.append(wire(x, 206.19, x, 318.73))
        out.append(junction(x, 318.73))
        # shunt (pino inf y=321.27) → GND
        out.append(wire(x, 321.27, x, 360))
        out.append(junction(x, 321.27))

    # --- Gates: DRV8302 (dir x=117.62) → G dos MOSFETs (x-3.81) ---
    # rota em "L" com vertical em xb = qg-4 (não cruza outros pinos)
    for qx, qy, gy, glabel in [
            (150, 110, 490.16, 'GHA'), (150, 210, 487.62, 'GLA'),
            (250, 110, 485.08, 'GHB'), (250, 210, 482.54, 'GLB'),
            (350, 110, 480.00, 'GHC'), (350, 210, 477.46, 'GLC')]:
        qgx = qx - 3.81
        xb = qgx - 4
        out.append(wire(117.62, gy, xb, gy))      # horizontal saindo do DRV
        out.append(wire(xb, gy, xb, qy))          # vertical até a altura do gate
        out.append(wire(xb, qy, qgx, qy))         # horizontal até o pino G
        out.append(junction(qgx, qy))

    # --- ESP32 (esq x=102.38) → entradas do DRV8302 (esq x=102.38) ---
    for esp_y, drv_y in [(658.89, 487.62), (656.35, 485.08), (653.81, 482.54)]:
        out.append(wire(102.38, esp_y, 102.38, drv_y))
        out.append(junction(102.38, drv_y))

    # sheet_instances
    out.append('  (sheet_instances\n    (path "/" (page "1"))\n  )\n')
    # symbol_instances
    out.append('  (symbol_instances\n')
    for _, pu, ref, value in insts:
        out.append(f'    (path "/{pu}"\n      (reference "{ref}") (unit 1) (value "{value}") (footprint "")\n    )\n')
    out.append('  )\n')
    out.append(')\n')
    return ''.join(out)


if __name__ == '__main__':
    content = build_schematic()
    with open(OUT, 'w') as f:
        f.write(content)
    print(f'Escrevi {OUT} ({len(content)} bytes)')