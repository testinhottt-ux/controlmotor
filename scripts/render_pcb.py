#!/usr/bin/env python3
"""Render programático do PCB da controladora BLDC 400V/50A — layout REAL.

Redesenhado seguindo as melhores práticas do mercado (TI SLVA959B "Best
Practices for Board Layout of Motor Drivers" + topologia VESC 6.x):

  - Split físico: Zona de POTÊNCIA (3 half-bridges) | Zona de CONTROLE (MCU+driver)
  - Banco de capacitores perto do power stage (loop de alta frequência curto)
  - 6 MOSFETs DPAK em 3 half-bridges, com shunt Kelvin por fase
  - Gate driver central (DRV8302) equidistante dos gates
  - MCU (ESP32) na borda, isolado da zona de potência, antena para fora
  - Conectores: XT60 (entrada), bornes M6 (U/V/W), JST (hall/aux)

Cores e geometria inspiradas em controladoras comerciais (VESC 6, ODrive).
"""

import cairo
import math
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'imagens')
os.makedirs(OUT, exist_ok=True)

# ---- Paleta (estética PCB profissional) ----
FR4_GREEN = (0.11, 0.40, 0.21)
FR4_DARK = (0.07, 0.28, 0.15)
COPPER = (0.87, 0.63, 0.18)
GOLD = (0.92, 0.78, 0.30)
SILK = (0.95, 0.95, 0.94)
COMP_DARK = (0.13, 0.13, 0.16)
METAL = (0.62, 0.66, 0.72)
METAL_DARK = (0.42, 0.46, 0.52)
BLACK = (0.06, 0.06, 0.08)
RED = (0.75, 0.16, 0.13)
ALUM = (0.62, 0.64, 0.68)
ALUM_DARK = (0.46, 0.48, 0.53)
CERAMIC = (0.86, 0.84, 0.80)
CERAMIC_DARK = (0.30, 0.28, 0.26)
WHITE = (1.0, 1.0, 1.0)
BLUE = (0.15, 0.35, 0.55)
YELLOW = (0.95, 0.82, 0.15)


def rounded(ctx, x, y, w, h, r):
    ctx.new_path()
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
    ctx.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
    ctx.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
    ctx.close_path()


def fill(ctx, color):
    ctx.set_source_rgb(*color)
    ctx.fill()


def stroke(ctx, color, w=1.0):
    ctx.set_source_rgb(*color)
    ctx.set_line_width(w)
    ctx.stroke()


def text(ctx, x, y, s, size=10, color=SILK, anchor='c'):
    ctx.set_source_rgb(*color)
    ctx.set_font_size(size)
    fb = ctx.font_extents()
    w = ctx.text_extents(s)[2]
    if anchor == 'c':
        tx = x - w / 2
    elif anchor == 'w':
        tx = x
    elif anchor == 'e':
        tx = x - w
    else:
        tx = x
    ctx.move_to(tx, y + fb[3] / 2)
    ctx.show_text(s)


def dpak_mosfet(ctx, x, y, w=16, h=22, color=(0.10, 0.10, 0.13)):
    """MOSFET DPAK/TO-252 com tab metálico exposto"""
    rounded(ctx, x, y, w, h, 2)
    fill(ctx, color)
    stroke(ctx, BLACK, 0.7)
    # tab (drain) — metal
    ctx.set_source_rgb(*METAL)
    ctx.rectangle(x + 2, y + 4, w - 4, h - 8)
    ctx.fill()
    # pino gate/source à esquerda
    for i, px in enumerate([x - 3, x - 3, x + w + 1]):
        ctx.set_source_rgb(*METAL)
        ctx.rectangle(px, y + 4 + i * 7, 3, 2.5)
        ctx.fill()
    # label
    text(ctx, x + w / 2, y + h + 4, 'Q', 6, SILK)


def ceramic_cap(ctx, x, y, w=8, h=5, color=CERAMIC):
    """Capacitor cerâmico SMD 0805"""
    ctx.set_source_rgb(*color)
    ctx.rectangle(x, y, w, h)
    ctx.fill()
    ctx.set_source_rgb(*METAL_DARK)
    for px in (x, x + w - 2):
        ctx.rectangle(px, y, 2, h)
        ctx.fill()


def elyt_cap(ctx, x, y, w, h, label):
    """Capacitor eletrolítico (banco DC-link)"""
    rounded(ctx, x, y, w, h, 4)
    fill(ctx, COMP_DARK)
    stroke(ctx, BLACK, 1)
    ctx.set_source_rgb(*WHITE)
    ctx.rectangle(x + w - 7, y + h - 5, 5, 4)
    ctx.fill()
    text(ctx, x + w / 2, y + h / 2 + 1, label, 6, SILK)


def screw_terminal(ctx, x, y, w=26, h=30, label='U', color=GOLD):
    """Bornes de parafuso M6 para fase"""
    rounded(ctx, x, y, w, h, 4)
    fill(ctx, color)
    stroke(ctx, BLACK, 1)
    # furo do parafuso
    ctx.set_source_rgb(*BLACK)
    ctx.arc(x + w / 2, y + h / 2, 6, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(*METAL)
    ctx.arc(x + w / 2, y + h / 2, 3.5, 0, 2 * math.pi)
    ctx.fill()
    text(ctx, x + w / 2, y + h + 6, label, 10, SILK)


def xt60(ctx, x, y, w=44, h=30):
    """Conector XT60 (entrada bateria)"""
    rounded(ctx, x, y, w, h, 5)
    fill(ctx, (0.85, 0.35, 0.12))
    stroke(ctx, BLACK, 1)
    ctx.set_source_rgb(0.6, 0.2, 0.08)
    ctx.rectangle(x + 5, y + 5, w - 10, h - 10)
    ctx.fill()
    text(ctx, x + w / 2, y + h / 2 + 2, '+ -', 9, WHITE)


def ic(ctx, x, y, w, h, label, sub, color=COMP_DARK):
    """Circuito integrado (retângulo com pinos)"""
    ctx.set_source_rgb(*color)
    ctx.rectangle(x, y, w, h)
    ctx.fill()
    stroke(ctx, BLACK, 1)
    ctx.set_source_rgb(*GOLD)
    for i in range(6):
        ctx.rectangle(x - 3, y + 3 + i * (h - 6) / 5, 3, 2.5)
        ctx.rectangle(x + w, y + 3 + i * (h - 6) / 5, 3, 2.5)
        ctx.fill()
    text(ctx, x + w / 2, y + h / 2 - 2, label, 8, SILK)
    text(ctx, x + w / 2, y + h / 2 + 8, sub, 6, (0.8, 0.8, 0.85))


def vias_pattern(ctx, x, y, w, h, nx=4, ny=6, r=2.2):
    """Grade de vias térmicas (para dissipação sob MOSFET)"""
    ctx.set_source_rgb(*GOLD)
    for i in range(nx):
        for j in range(ny):
            ctx.arc(x + (i + 0.5) * w / nx, y + (j + 0.5) * h / ny, r, 0, 2 * math.pi)
            ctx.fill()


def draw_pcb_top():
    W, H = 1500, 1050
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(0.95, 0.96, 0.97)
    ctx.paint()

    # ---- Placa principal (margem e furos M4) ----
    px, py, pw, ph = 90, 80, 1320, 890
    rounded(ctx, px, py, pw, ph, 10)
    fill(ctx, FR4_GREEN)
    stroke(ctx, (0.04, 0.26, 0.13), 2.5)
    for (fx, fy) in [(px + 30, py + 30), (px + pw - 30, py + 30),
                     (px + 30, py + ph - 30), (px + pw - 30, py + ph - 30)]:
        ctx.set_source_rgb(*METAL)
        ctx.arc(fx, fy, 10, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgb(*BLACK)
        ctx.arc(fx, fy, 5, 0, 2 * math.pi)
        ctx.fill()

    # ============================================================
    # ZONA DE POTÊNCIA (esquerda ~65%): 3 half-bridges + DC-link
    # ============================================================
    pz_x, pz_y, pz_w, pz_h = px + 30, py + 30, 820, ph - 60
    ctx.set_source_rgba(0.95, 0.75, 0.25, 0.10)
    ctx.rectangle(pz_x, pz_y, pz_w, pz_h)
    ctx.fill()
    text(ctx, pz_x + pz_w / 2, pz_y + 14, 'ZONA DE POTÊNCIA 400V / 50A', 12, (0.55, 0.32, 0.05))

    # ---- Barramento DC (trilha de cobre grossa no topo) ----
    ctx.set_source_rgb(*COPPER)
    ctx.set_line_width(22)
    ctx.move_to(pz_x + 10, pz_y + 40)
    ctx.line_to(pz_x + pz_w - 10, pz_y + 40)
    ctx.stroke()
    text(ctx, pz_x + pz_w - 90, pz_y + 40, '+400V', 10, (0.4, 0.25, 0.05))

    # ---- Banco de capacitores DC-link (cerâmica, perto dos MOSFETs) ----
    # por fase, desacoplamento de alta frequência (regra TI)
    for i in range(3):
        cx = pz_x + 40 + i * 270
        for j in range(3):
            ceramic_cap(ctx, cx + j * 14, pz_y + 60 + (j % 2) * 8)
    text(ctx, pz_x + 160, pz_y + 72, 'Ccer 100n (HF loop)', 6, (0.5, 0.3, 0.1))

    # ---- 3 HALF-BRIDGES: cada fase = HS (topo) + LS (base) + shunt ----
    for i, phase in enumerate(['U', 'V', 'W']):
        bx = pz_x + 30 + i * 270
        # trilha de fase (switch node) — crítica, curta
        ctx.set_source_rgb(*COPPER)
        ctx.set_line_width(16)
        ctx.move_to(bx + 8, pz_y + 130)
        ctx.line_to(bx + 8, pz_y + 330)
        ctx.stroke()
        # high-side DPAK
        dpak_mosfet(ctx, bx + 40, pz_y + 100)
        text(ctx, bx + 48, pz_y + 90, f'Q{i*2+1} HS-{phase}', 7)
        # vias térmicas sob o HS
        vias_pattern(ctx, bx + 44, pz_y + 108, 10, 10, 2, 3, 1.5)
        # low-side DPAK
        dpak_mosfet(ctx, bx + 40, pz_y + 220)
        text(ctx, bx + 48, pz_y + 210, f'Q{i*2+2} LS-{phase}', 7)
        vias_pattern(ctx, bx + 44, pz_y + 228, 10, 10, 2, 3, 1.5)
        # shunt Kelvin (4-fios, regra TI) entre LS e GND
        ctx.set_source_rgb(0.94, 0.94, 0.96)
        rounded(ctx, bx + 20, pz_y + 330, 34, 14, 2)
        ctx.fill()
        stroke(ctx, METAL_DARK, 1)
        text(ctx, bx + 37, pz_y + 340, 'Rsh', 6, BLACK)
        # trilha de retorno ao GND
        ctx.set_source_rgb(*COPPER)
        ctx.set_line_width(14)
        ctx.move_to(bx + 37, pz_y + 344)
        ctx.line_to(bx + 37, pz_y + 400)
        ctx.stroke()

    # ---- Plano GND da zona de potência (pads de cobre) ----
    ctx.set_source_rgb(*GOLD)
    for gx in range(pz_x + 10, pz_x + pz_w - 20, 40):
        for gy in range(pz_y + 420, pz_y + pz_h - 20, 40):
            ctx.arc(gx, gy, 4, 0, 2 * math.pi)
            ctx.fill()

    # ---- Bornes de fase U/V/W (M6) na borda inferior da potência ----
    for i, phase in enumerate(['U', 'V', 'W']):
        screw_terminal(ctx, pz_x + 30 + i * 270, pz_y + pz_h - 90, 30, 34, phase, GOLD)
    # trilha das fases até os bornes
    ctx.set_source_rgb(*COPPER)
    ctx.set_line_width(18)
    for i in range(3):
        bx = pz_x + 30 + i * 270
        ctx.move_to(bx + 16, pz_y + 330)
        ctx.line_to(bx + 20, pz_y + pz_h - 88)
        ctx.stroke()

    # ---- XT60 entrada (borda esquerda da potência) ----
    xt60(ctx, pz_x + 30, pz_y + pz_h - 150, 46, 32)
    text(ctx, pz_x + 56, pz_y + pz_h - 170, 'BAT +400V', 7, (0.5, 0.3, 0.1))
    # fusível
    ctx.set_source_rgb(*YELLOW)
    rounded(ctx, pz_x + 120, pz_y + pz_h - 148, 40, 26, 4)
    ctx.fill()
    stroke(ctx, BLACK, 1)
    text(ctx, pz_x + 140, pz_y + pz_h - 138, 'F1 50A', 6, BLACK)

    # ============================================================
    # ZONA DE CONTROLE (direita ~35%): DRV8302 + ESP32 + reguladores
    # ============================================================
    cz_x = px + pz_w - 60
    cz_y = py + 30
    cz_w = px + pw - (pz_w - 60) - 30
    cz_h = ph - 60
    ctx.set_source_rgba(0.2, 0.55, 0.9, 0.09)
    ctx.rectangle(cz_x, cz_y, cz_w, cz_h)
    ctx.fill()
    text(ctx, cz_x + cz_w / 2, cz_y + 14, 'ZONA DE CONTROLE 3.3V/5V', 12, (0.1, 0.3, 0.5))

    # ---- DRV8302 (gate driver central, equidistante dos gates) ----
    ic(ctx, cz_x + 40, cz_y + 60, 110, 90, 'DRV8302', '3-phase gate driver')
    # trilhas de gate para cada fase (curtas)
    ctx.set_source_rgb(*COPPER)
    ctx.set_line_width(6)
    for i in range(3):
        bx = pz_x + 60 + i * 270
        ctx.move_to(cz_x + 40, cz_y + 85 + i * 20)
        ctx.curve_to(cz_x - 40, cz_y + 85 + i * 20, bx - 60, pz_y + 130, bx + 44, pz_y + 115)
        ctx.stroke()
    text(ctx, cz_x + 96, cz_y + 130, 'GHA/B/C ->', 6, SILK)

    # ---- Reguladores (buck 5V + LDO 3.3V) ----
    ic(ctx, cz_x + 200, cz_y + 60, 90, 40, 'BUCK', '12V->5V')
    ic(ctx, cz_x + 200, cz_y + 120, 90, 40, 'LDO', '5V->3.3V')
    # indutor
    ctx.set_source_rgb(0.75, 0.55, 0.25)
    rounded(ctx, cz_x + 315, cz_y + 70, 30, 60, 8)
    ctx.fill()
    text(ctx, cz_x + 330, cz_y + 102, 'L 10uH', 5, BLACK)

    # ---- ESP32-WROOM-32E (MCU, antena para fora) ----
    ex, ey = cz_x + 40, cz_y + 220
    ctx.set_source_rgb(*METAL)
    rounded(ctx, ex, ey, 120, 70, 6)
    ctx.fill()
    stroke(ctx, METAL_DARK, 1.2)
    text(ctx, ex + 60, ey + 22, 'ESP32-WROOM', 9, BLACK)
    text(ctx, ex + 60, ey + 38, '-32E', 11, BLACK)
    # antena
    ctx.set_source_rgb(*COPPER)
    ctx.rectangle(ex + 120, ey + 40, 14, 26)
    ctx.fill()
    text(ctx, ex + 127, ey + 40, '', 6, SILK)
    ctx.set_source_rgb(*GOLD)
    for i in range(2):
        ctx.rectangle(ex - 8 + i * 62, ey + 64, 56, 12)
        ctx.fill()

    # ---- Conectores de controle (JST) ----
    for i, lbl in enumerate(['Hall', 'CAN', 'USB']):
        ctx.set_source_rgb(*METAL)
        rounded(ctx, cz_x + 200 + i * 110, cz_y + 230, 70, 34, 4)
        ctx.fill()
        text(ctx, cz_x + 235 + i * 110, cz_y + 250, lbl, 7, BLACK)
    text(ctx, cz_x + 260, cz_y + 280, 'JST-PH 2.0mm', 6, SILK)

    # ---- silkscreen: marca + avisos ----
    text(ctx, px + pw / 2, py + ph - 40, 'BLDC CONTROLLER 400V - 50A - FOC', 15)
    text(ctx, px + pw / 2, py + ph - 20, 'DANGER HV 400V — descarregue antes de tocar  |  rev 2.0', 9,
         (1.0, 0.5, 0.4))

    surf.write_to_png(os.path.join(OUT, 'pcb_top.png'))
    print('pcb_top.png OK (layout real)')


def draw_pcb_bottom():
    W, H = 1500, 1050
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(0.95, 0.96, 0.97)
    ctx.paint()
    px, py, pw, ph = 90, 80, 1320, 890
    rounded(ctx, px, py, pw, ph, 10)
    fill(ctx, FR4_DARK)
    stroke(ctx, (0.04, 0.24, 0.11), 2.5)
    for (fx, fy) in [(px + 30, py + 30), (px + pw - 30, py + 30),
                     (px + 30, py + ph - 30), (px + pw - 30, py + ph - 30)]:
        ctx.set_source_rgb(*METAL)
        ctx.arc(fx, fy, 10, 0, 2 * math.pi)
        ctx.fill()

    # Plano de cobre inferior
    ctx.set_source_rgb(*COPPER)
    ctx.set_line_width(6)
    for i in range(8):
        y = py + 80 + i * 100
        ctx.move_to(px + 40, y)
        ctx.line_to(px + pw - 40, y)
        ctx.stroke()

    # Área de dissipação térmica (exposed pad sob a potência)
    ctx.set_source_rgb(*GOLD)
    for gx in range(px + 120, px + 900, 30):
        for gy in range(py + 120, py + ph - 120, 30):
            ctx.arc(gx, gy, 5, 0, 2 * math.pi)
            ctx.fill()
    text(ctx, px + 500, py + ph - 40, 'LADO B — PAD TÉRMICO / COBRE  |  via térmica 8x0.3mm p/ backplate',
         10)
    text(ctx, px + 500, py + ph - 22, 'Kelvin shunt: 4-fios (corrente e sensores separados)', 9)

    surf.write_to_png(os.path.join(OUT, 'pcb_bottom.png'))
    print('pcb_bottom.png OK')


def draw_prototipo():
    W, H = 1600, 1100
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(0.93, 0.94, 0.96)
    ctx.paint()

    def P(x, y, z):
        # isométrico: X -> +30°, Y -> -30° (profundidade), Z vertical
        return (x * math.cos(math.radians(30)) + y * math.cos(math.radians(150)) + W * 0.28,
                z + x * math.sin(math.radians(30)) + y * math.sin(math.radians(150)) + H * 0.25)

    def quad(p1, p2, p3, p4, color):
        ctx.set_source_rgb(*color)
        ctx.move_to(*P(*p1))
        ctx.line_to(*P(*p2))
        ctx.line_to(*P(*p3))
        ctx.line_to(*P(*p4))
        ctx.close_path()
        ctx.fill()
        ctx.set_source_rgb(*ALUM_DARK)
        ctx.set_line_width(1)
        ctx.stroke()

    # ---- Backplate de alumínio com aletas ----
    bx, by, bz = 420, 480, 380
    bw, bd = 520, 300
    quad((bx, by, bz), (bx + bw, by, bz), (bx + bw, by, bz + bd), (bx, by, bz + bd), ALUM)
    for i in range(12):
        ax = bx + 12 + i * (bw - 24) / 11
        quad((ax, by, bz + 8), (ax, by, bz + bd - 8),
             (ax, by - 46, bz + bd - 8), (ax, by - 46, bz + 8),
             (ALUM_DARK if i % 2 else (0.52, 0.55, 0.6)))
    quad((bx, by - 46, bz + bd), (bx + bw, by - 46, bz + bd),
         (bx + bw, by, bz + bd), (bx, by, bz + bd), (0.5, 0.53, 0.58))

    # ---- Placa (PCB) sobre o backplate ----
    pcx, pcz = bx - 30, bz - 30
    quad((pcx, by - 46, pcz), (pcx + 580, by - 46, pcz),
         (pcx + 580, by - 46, pcz + 360), (pcx, by - 46, pcz + 360), FR4_GREEN)
    # componentes em relevo
    comps = [
        (pcx + 60, pcz + 60, 70, 100, METAL, 'ESP32'),
        (pcx + 60, pcz + 210, 80, 80, COMP_DARK, 'DRV8302'),
        (pcx + 250, pcz + 70, 70, 230, (0.1, 0.1, 0.14), 'MOSFETs'),
        (pcx + 380, pcz + 60, 80, 100, (0.22, 0.24, 0.30), '470uF'),
        (pcx + 380, pcz + 190, 80, 90, (0.22, 0.24, 0.30), '470uF'),
    ]
    for (cx, cz, cw, cd, col, lbl) in comps:
        quad((cx, by - 46, cz), (cx + cw, by - 46, cz),
             (cx + cw, by - 46, cz + cd), (cx, by - 46, cz + cd), col)
        quad((cx, by - 46, cz + cd), (cx + cw, by - 46, cz + cd),
             (cx + cw, by - 76, cz + cd), (cx, by - 76, cz + cd),
             tuple(min(1, c * 1.3) for c in col))
        quad((cx + cw, by - 46, cz), (cx + cw, by - 46, cz + cd),
             (cx + cw, by - 76, cz + cd), (cx + cw, by - 76, cz),
             tuple(min(1, c * 0.8) for c in col))

    # ---- Conector XT60 ----
    quad((pcx + 480, by - 46, pcz + 280), (pcx + 520, by - 46, pcz + 280),
         (pcx + 520, by - 46, pcz + 330), (pcx + 480, by - 46, pcz + 330), (0.9, 0.4, 0.1))

    # ---- Cabos de fase para o motor ----
    for i, col in enumerate([(0.75, 0.2, 0.18), (0.2, 0.55, 0.8), (0.9, 0.7, 0.15)]):
        sx = pcx + 460 + i * 34
        tx = bx + 140 + i * 90
        ctx.set_source_rgb(*col)
        ctx.set_line_width(8)
        ctx.move_to(*P(sx, by - 46, pcz + 330))
        ctx.curve_to(*P(sx + 30, by - 170, pcz + 380),
                     *P(tx - 60, by - 210, pcz + 500),
                     *P(tx, by - 230, pcz + 560))
        ctx.stroke()

    # ---- Motor BLDC (cilindro) ----
    mx, my, mz = bx - 80, by - 230, bz + 250
    ctx.set_source_rgb(0.16, 0.16, 0.2)
    ctx.arc(*P(mx, my, mz), 140, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(*METAL)
    ctx.arc(*P(mx, my, mz), 32, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(0.5, 0.5, 0.55)
    ctx.arc(*P(mx, my, mz), 24, 0, 2 * math.pi)
    ctx.fill()
    for ang in range(0, 360, 24):
        a1 = math.radians(ang)
        a2 = math.radians(ang + 24)
        x1 = mx + 140 * math.cos(a1)
        y1 = my + 140 * math.sin(a1)
        x2 = mx + 140 * math.cos(a2)
        y2 = my + 140 * math.sin(a2)
        ctx.set_source_rgb(*RED if ang % 48 == 0 else (0.2, 0.2, 0.25))
        ctx.move_to(*P(x1, y1, mz))
        ctx.line_to(*P(x2, y2, mz))
        ctx.line_to(*P(x2, y2, mz + 170))
        ctx.line_to(*P(x1, y1, mz + 170))
        ctx.close_path()
        ctx.fill()

    # legenda
    ctx.set_source_rgb(0.1, 0.1, 0.15)
    ctx.set_font_size(20)
    ctx.move_to(50, H - 60)
    ctx.show_text('Prototipo: controlador BLDC 400V/50A — placa sobre backplate de aluminio + motor FOC')
    ctx.set_font_size(14)
    ctx.move_to(50, H - 34)
    ctx.show_text('Topologia: power stage (3 half-bridges) | gate driver central | MCU isolado  (inspirado VESC 6 / ODrive)')

    surf.write_to_png(os.path.join(OUT, 'prototipo.png'))
    print('prototipo.png OK')


if __name__ == '__main__':
    draw_pcb_top()
    draw_pcb_bottom()
    draw_prototipo()
    print('Done ->', OUT)