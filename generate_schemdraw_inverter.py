#!/usr/bin/env python3
"""
generate_schemdraw_inverter.py
Gera esquemáticos elétricos padrão IEEE/IEC profissionais do Inversor Trifásico e Chopper de Freio
usando a biblioteca Schemdraw. Exporta diretamente para SVG e PNG vetoriais perfeitos.
"""

import schemdraw
import schemdraw.elements as elm

def draw_3phase_inverter():
    """Desenha a Ponte Inversora Trifásica Completa (U, V, W) com Gate Drivers e Shunts"""
    with schemdraw.Drawing(file='schemdraw_3phase_inverter.svg', show=False) as d:
        d.config(fontsize=10, font='sans-serif', unit=2.2)
        
        # Barramento VDC Superior
        d += elm.Line().right().length(13.5).color('#DC2626').linewidth(2.5)
        d += elm.Label().label('VDC (+48V / 400V DC-LINK)', loc='top', color='#DC2626')
        
        phases = [
            ('U', 2.0, 'Q1', 'Q4', 'GH_A', 'GL_A', 'IS_U', '#DC2626'),
            ('V', 6.0, 'Q2', 'Q5', 'GH_B', 'GL_B', 'IS_V', '#2563EB'),
            ('W', 10.0, 'Q3', 'Q6', 'GH_C', 'GL_C', 'IS_W', '#16A34A')
        ]
        
        for phase_name, x_pos, q_hs_name, q_ls_name, gh_net, gl_net, is_net, color in phases:
            # Ponto de conexão no VDC
            top_pt = (x_pos, 0)
            d += elm.Dot().at(top_pt).color('#DC2626')
            
            # Linha até Drain High-Side
            d += elm.Line().down().at(top_pt).length(0.8)
            q_hs = d.add(elm.NFet(bulk=True).label(f'{q_hs_name} (HS)\nIRFB4110', loc='right'))
            
            # Resistor Gate HS
            d.push()
            d += elm.Line().left().at(q_hs.gate).length(0.5)
            d += elm.Resistor().left().label('10Ω', loc='bottom')
            d += elm.Label().label(gh_net, loc='left', color='#8B5CF6')
            d.pop()
            
            # Snubber RC High-Side (Lado Direito)
            d.push()
            d += elm.Line().right().at(q_hs.drain).length(1.2)
            d += elm.Resistor().down().label('2.2Ω', loc='right')
            d += elm.Capacitor().down().label('10nF', loc='right')
            d += elm.Line().left().to((x_pos, -2.8))
            d.pop()
            
            # Ponto Médio da Fase (Saída Motor)
            d += elm.Line().down().at(q_hs.source).length(0.8).dot()
            mid_pt = d.here
            
            # Linha de Saída da Fase para o Motor
            d.push()
            d += elm.Line().right().at(mid_pt).length(1.8)
            d += elm.Inductor2().right().label('1µH', loc='top')
            d += elm.Dot(radius=0.18).label(f'FASE {phase_name}', loc='right', color=color)
            d.pop()
            
            # Linha até Drain Low-Side
            d += elm.Line().down().at(mid_pt).length(0.8)
            q_ls = d.add(elm.NFet(bulk=True).label(f'{q_ls_name} (LS)\nIRFB4110', loc='right'))
            
            # Resistor Gate LS
            d.push()
            d += elm.Line().left().at(q_ls.gate).length(0.5)
            d += elm.Resistor().left().label('10Ω', loc='bottom')
            d += elm.Label().label(gl_net, loc='left', color='#8B5CF6')
            d.pop()
            
            # Shunt de Corrente (1mΩ)
            d += elm.Line().down().at(q_ls.source).length(0.6).dot()
            shunt_top = d.here
            d += elm.Resistor().down().label('1mΩ 3W\n(Shunt)', loc='right')
            shunt_bot = d.here
            
            # Conexão Kelvin Sense
            d.push()
            d += elm.Line().left().at(shunt_top).length(0.8)
            d += elm.Label().label(f'{is_net}+', loc='left', color='#D97706')
            d.pop()
            d.push()
            d += elm.Line().left().at(shunt_bot).length(0.8)
            d += elm.Label().label(f'{is_net}-', loc='left', color='#D97706')
            d.pop()
            
            # Conexão ao Plano GND
            d += elm.Ground().at(shunt_bot)
            
    print("✅ Gerado com sucesso: schemdraw_3phase_inverter.svg")

def draw_dc_link_and_chopper():
    """Desenha a Entrada de Potência, Pré-Carga e o Chopper de Freio Reostático"""
    with schemdraw.Drawing(file='schemdraw_chopper_power.svg', show=False) as d:
        d.config(fontsize=10, font='sans-serif', unit=2.2)
        
        # Conector de Entrada 48V / 400V
        d += elm.SourceV().up().label('XT90 / BATT\n48V - 400V', loc='left')
        d += elm.Line().right().length(0.8)
        
        # Fusível de Potência
        d += elm.Fuse().right().label('FUSE 50A', loc='top')
        d += elm.Line().right().length(0.5).dot()
        pre_in = d.here
        
        # Circuito de Pré-Carga (Relé K_pre // Resistor 10R 25W)
        d.push()
        d += elm.Line().up().length(0.8)
        d += elm.Resistor().right().label('R_pre 10Ω 25W', loc='top')
        d += elm.Line().down().length(0.8)
        d.pop()
        
        d += elm.Switch().right().label('K_pre (Bypass)', loc='bottom')
        d += elm.Line().right().length(0.5).dot()
        post_pre = d.here
        
        # Diodo TVS e Capacitor Bulk
        d.push()
        d += elm.Line().right().length(1.2)
        d += elm.Zener().down().label('TVS 58V / 450V', loc='right')
        d += elm.Ground()
        d.pop()
        
        d += elm.Line().right().length(2.5).dot()
        bulk_top = d.here
        d.push()
        d += elm.Capacitor(polar=True).down().label('470µF 450V\nBulk Cap', loc='right')
        d += elm.Ground()
        d.pop()
        
        # Chopper de Freio Motor
        d += elm.Line().right().length(2.5).dot()
        chopper_top = d.here
        
        # Ramo Resistor de Freio + Diodo Roda Livre
        d += elm.Line().down().at(chopper_top).length(0.5)
        d += elm.Resistor().down().label('R_brake\n10Ω 100W', loc='right')
        d.push()
        d += elm.Line().left().at(chopper_top).length(1.0)
        d += elm.Diode().down().label('D_brake\nMURS360', loc='left')
        d += elm.Line().right().length(1.0)
        d.pop()
        
        # MOSFET de Freio (Q_brake)
        d += elm.Line().down().length(0.5)
        q_brk = d.add(elm.NFet(bulk=True).label('Q_brake\nIRFB4110', loc='right'))
        
        d.push()
        d += elm.Line().left().at(q_brk.gate).length(0.8)
        d += elm.Resistor().left().label('47Ω', loc='bottom')
        d += elm.Label().label('BRAKE_PWM', loc='left', color='#8B5CF6')
        d.pop()
        
        d += elm.Ground().at(q_brk.source)
        
    print("✅ Gerado com sucesso: schemdraw_chopper_power.svg")

if __name__ == '__main__':
    draw_3phase_inverter()
    draw_dc_link_and_chopper()
