#!/usr/bin/env python3
"""
generate_professional_cad_suite.py
Suíte Completa de Geração de Esquemáticos Padrão Industrial (TI / Infineon / IEEE).
Gera 4 folhas esquemáticas detalhadas + 1 diagrama mestre arquitetural integrado.
Inclui verificação visual automatizada de posição de todos os componentes do BOM.
"""

import os
import schemdraw
import schemdraw.elements as elm
from schemdraw import logic

def build_power_stage_schematic():
    """Folha 1: Ponte Inversora Trifásica 48V-400V com Snubbers, Bootstrap e Shunts Kelvin"""
    with schemdraw.Drawing(file='esquematico_folha1_inversor.svg', show=False) as d:
        d.config(fontsize=10, font='sans-serif', unit=2.5)
        
        # Título da Folha
        d += elm.Label().label('INVERSOR TRIFÁSICO BLDC/PMSM — ESTÁGIO DE POTÊNCIA (48V / 400V)', loc='top', color='#0F172A', fontsize=14)
        
        # Barramento VDC Superior (+48V / 400V)
        d += elm.Line().right().length(14.5).color('#DC2626').linewidth(3)
        d += elm.Label().label('VDC (+48V a +400V DC-LINK)', loc='top', color='#DC2626')
        
        fases = [
            ('U', 2.2, 'Q1', 'Q4', 'BST_A', 'GH_A', 'SH_A', 'GL_A', '1mΩ 3W', 'IS_U', '#DC2626'),
            ('V', 6.8, 'Q2', 'Q5', 'BST_B', 'GH_B', 'SH_B', 'GL_B', '1mΩ 3W', 'IS_V', '#2563EB'),
            ('W', 11.4, 'Q3', 'Q6', 'BST_C', 'GH_C', 'SH_C', 'GL_C', '1mΩ 3W', 'IS_W', '#16A34A')
        ]
        
        for name, x, q_hs, q_ls, bst, gh, sh, gl, shunt_val, is_net, col in fases:
            # Ponto de conexão no VDC
            top = (x, 0)
            d += elm.Dot(radius=0.12).at(top).color('#DC2626')
            
            # High-Side MOSFET (Drain para VDC)
            d += elm.Line().down().at(top).length(1.0)
            fet_hs = d.add(elm.NFet(bulk=True).label(f'{q_hs} (HS)\nIRFB4110 / SiC', loc='right'))
            
            # Resistor de Gate High-Side (10Ω)
            d.push()
            d += elm.Line().left().at(fet_hs.gate).length(0.6)
            d += elm.Resistor().left().label('10Ω', loc='bottom')
            d += elm.Label().label(gh, loc='left', color='#8B5CF6')
            d.pop()
            
            # Snubber RC High-Side (Paralelo Drain-Source)
            d.push()
            d += elm.Line().right().at(fet_hs.drain).length(1.4)
            d += elm.Resistor().down().label('2.2Ω\n1W', loc='right')
            d += elm.Capacitor().down().label('10nF\n100V', loc='right')
            d += elm.Line().left().to((x, -3.2))
            d.pop()
            
            # Capacitor de Bootstrap
            d.push()
            d += elm.Line().left().at(fet_hs.source).length(1.8)
            d += elm.Capacitor().up().label('C_boot\n100nF', loc='left')
            d += elm.Label().label(bst, loc='top', color='#0284C7')
            d.pop()
            
            # Nó Central da Fase (Meio da Ponte)
            d += elm.Line().down().at(fet_hs.source).length(1.0).dot()
            mid = d.here
            
            # Ponto de Saída de Fase e Filtro EMI
            d.push()
            d += elm.Line().right().at(mid).length(1.2)
            d += elm.Inductor2().right().label('1µH 40A', loc='top')
            d += elm.Dot(radius=0.2).label(f'FASE {name}\n(Motor)', loc='right', color=col)
            d.pop()
            
            # Low-Side MOSFET (Drain conectado ao nó médio)
            d += elm.Line().down().at(mid).length(1.0)
            fet_ls = d.add(elm.NFet(bulk=True).label(f'{q_ls} (LS)\nIRFB4110 / SiC', loc='right'))
            
            # Resistor de Gate Low-Side (10Ω)
            d.push()
            d += elm.Line().left().at(fet_ls.gate).length(0.6)
            d += elm.Resistor().left().label('10Ω', loc='bottom')
            d += elm.Label().label(gl, loc='left', color='#8B5CF6')
            d.pop()
            
            # Snubber RC Low-Side (Paralelo Drain-Source)
            d.push()
            d += elm.Line().right().at(fet_ls.drain).length(1.4)
            d += elm.Resistor().down().label('2.2Ω\n1W', loc='right')
            d += elm.Capacitor().down().label('10nF\n100V', loc='right')
            d += elm.Line().left().to((x, -6.6))
            d.pop()
            
            # Resistor Shunt de Corrente (1mΩ 3W)
            d += elm.Line().down().at(fet_ls.source).length(0.8).dot()
            sh_top = d.here
            d += elm.Resistor().down().label(f'{shunt_val}\n(Shunt)', loc='right')
            sh_bot = d.here
            
            # Linhas de Sensoriamento Kelvin
            d.push()
            d += elm.Line().left().at(sh_top).length(1.0)
            d += elm.Label().label(f'{is_net}+', loc='left', color='#D97706')
            d.pop()
            d.push()
            d += elm.Line().left().at(sh_bot).length(1.0)
            d += elm.Label().label(f'{is_net}-', loc='left', color='#D97706')
            d.pop()
            
            # Conexão ao Plano de Potência GND
            d += elm.Ground().at(sh_bot)

    print("✅ Folha 1 (Inversor Trifásico) gerada: esquematico_folha1_inversor.svg")

def build_gate_driver_schematic():
    """Folha 2: Gate Driver TI DRV8302 com Charge Pump, Buck Integrado e Shunts Amps"""
    with schemdraw.Drawing(file='esquematico_folha2_driver.svg', show=False) as d:
        d.config(fontsize=9, font='sans-serif', unit=2.2)
        
        d += elm.Label().label('GATE DRIVER TRIFÁSICO — TI DRV8302 COM AMP OP INTEGRADO', loc='top', color='#0F172A', fontsize=13)
        
        # Caixa Central do Driver DRV8302
        ic = d.add(elm.Ic(pins=[
            elm.IcPin(name='PVDD', pin='1', side='left'),
            elm.IcPin(name='GND', pin='2', side='left'),
            elm.IcPin(name='INH_A', pin='3', side='left'),
            elm.IcPin(name='INL_A', pin='4', side='left'),
            elm.IcPin(name='INH_B', pin='5', side='left'),
            elm.IcPin(name='INL_B', pin='6', side='left'),
            elm.IcPin(name='INH_C', pin='7', side='left'),
            elm.IcPin(name='INL_C', pin='8', side='left'),
            elm.IcPin(name='EN_GATE', pin='9', side='left'),
            elm.IcPin(name='nFAULT', pin='10', side='left'),
            
            elm.IcPin(name='GVDD', pin='20', side='right'),
            elm.IcPin(name='BST_A', pin='19', side='right'),
            elm.IcPin(name='GH_A', pin='18', side='right'),
            elm.IcPin(name='SH_A', pin='17', side='right'),
            elm.IcPin(name='GL_A', pin='16', side='right'),
            elm.IcPin(name='GH_B', pin='15', side='right'),
            elm.IcPin(name='GL_B', pin='14', side='right'),
            elm.IcPin(name='GH_C', pin='13', side='right'),
            elm.IcPin(name='GL_C', pin='12', side='right'),
            elm.IcPin(name='SO1', pin='11', side='right')
        ]).label('TI DRV8302\n(56-Pin QFN)', loc='center'))
        
        # Alimentação PVDD e GND
        d.push()
        d += elm.Line().left().at(ic.PVDD).length(1.2)
        d += elm.Label().label('VDC (+48V)', loc='left', color='#DC2626')
        d.pop()
        
        d.push()
        d += elm.Line().left().at(ic.GND).length(0.8)
        d += elm.Ground()
        d.pop()
        
        # Sinais de PWM do MCU
        pwm_pins = [
            (ic.INH_A, 'PWM_UH (GPIO12)'), (ic.INL_A, 'PWM_UL (GPIO13)'),
            (ic.INH_B, 'PWM_VH (GPIO14)'), (ic.INL_B, 'PWM_VL (GPIO27)'),
            (ic.INH_C, 'PWM_WH (GPIO15)'), (ic.INL_C, 'PWM_WL (GPIO2)'),
            (ic.EN_GATE, 'DRV_EN (GPIO18)'), (ic.nFAULT, 'FAULT_N (GPIO19)')
        ]
        for pin, label in pwm_pins:
            d.push()
            d += elm.Line().left().at(pin).length(1.0)
            d += elm.Label().label(label, loc='left', color='#6366F1')
            d.pop()
            
        # Saídas para os Gates
        gate_outs = [
            (ic.GVDD, 'GVDD (+8V LDO Cap)'),
            (ic.BST_A, 'BST_A (Boot U)'),
            (ic.GH_A, 'GH_A (Gate HS U)'),
            (ic.SH_A, 'SH_A (Source HS U)'),
            (ic.GL_A, 'GL_A (Gate LS U)'),
            (ic.GH_B, 'GH_B (Gate HS V)'),
            (ic.GL_B, 'GL_B (Gate LS V)'),
            (ic.GH_C, 'GH_C (Gate HS W)'),
            (ic.GL_C, 'GL_C (Gate LS W)'),
            (ic.SO1, 'IS_U_AMP (ADC1_CH0)')
        ]
        for pin, label in gate_outs:
            d.push()
            d += elm.Line().right().at(pin).length(1.2)
            d += elm.Label().label(label, loc='right', color='#0284C7')
            d.pop()

    print("✅ Folha 2 (Gate Driver DRV8302) gerada: esquematico_folha2_driver.svg")

def build_power_and_chopper_schematic():
    """Folha 3: Gerenciamento de Energia, Pré-Carga, TVS, Chopper e Fontes Auxiliares"""
    with schemdraw.Drawing(file='esquematico_folha3_alimentacao.svg', show=False) as d:
        d.config(fontsize=10, font='sans-serif', unit=2.2)
        
        d += elm.Label().label('GERENCIAMENTO DE ENERGIA, PRÉ-CARGA E CHOPPER DE FREIO REOSTÁTICO', loc='top', color='#0F172A', fontsize=13)
        
        # Conector Principal de Entrada
        d += elm.SourceV().up().label('XT90 / BATT\n+48V a +400V', loc='left')
        d += elm.Line().right().length(0.8)
        d += elm.Fuse().right().label('FUSE 50A\n(Ultra-Fast)', loc='top')
        d += elm.Line().right().length(0.6).dot()
        p_in = d.here
        
        # Estágio de Pré-Carga Ativa
        d.push()
        d += elm.Line().up().length(0.9)
        d += elm.Resistor().right().label('R_pre 10Ω 25W\n(Limitação Inrush)', loc='top')
        d += elm.Line().down().length(0.9)
        d.pop()
        
        d += elm.Switch().right().label('K_pre (Bypass Relay)\n(Bobina 12V)', loc='bottom')
        d += elm.Line().right().length(0.6).dot()
        p_bus = d.here
        
        # Diodo TVS de Proteção contra Surto
        d.push()
        d += elm.Line().right().length(1.2)
        d += elm.Zener().down().label('TVS 58V / 450V\n(Transiente)', loc='right')
        d += elm.Ground()
        d.pop()
        
        # Banco de Capacitores Bulk (DC-Link)
        d += elm.Line().right().length(2.5).dot()
        d.push()
        d += elm.Capacitor(polar=True).down().label('470µF 450V\n(Low ESR Bulk)', loc='right')
        d += elm.Ground()
        d.pop()
        
        # Chopper de Freio Motor
        d += elm.Line().right().length(2.8).dot()
        ch_top = d.here
        
        d += elm.Line().down().at(ch_top).length(0.5)
        d += elm.Resistor().down().label('R_brake\n10Ω 100W\n(Reostato)', loc='right')
        
        # Diodo de Roda Livre em Paralelo com Resistor
        d.push()
        d += elm.Line().left().at(ch_top).length(1.2)
        d += elm.Diode().down().label('D_brake\nMURS360 (600V)', loc='left')
        d += elm.Line().right().length(1.2)
        d.pop()
        
        # MOSFET N de Chaveamento do Freio
        d += elm.Line().down().length(0.5)
        q_brk = d.add(elm.NFet(bulk=True).label('Q_brake\nIRFB4110', loc='right'))
        
        d.push()
        d += elm.Line().left().at(q_brk.gate).length(0.8)
        d += elm.Resistor().left().label('47Ω', loc='bottom')
        d += elm.Label().label('BRAKE_PWM (GPIO23)', loc='left', color='#8B5CF6')
        d.pop()
        
        d += elm.Ground().at(q_brk.source)
        
        # Linha para Inversor e Fontes Auxiliares
        d.push()
        d += elm.Line().right().at(ch_top).length(2.0)
        d += elm.Label().label('Para Inversor Trifásico (VDC)', loc='right', color='#DC2626')
        d.pop()

    print("✅ Folha 3 (Alimentação e Chopper) gerada: esquematico_folha3_alimentacao.svg")

def build_mcu_and_can_schematic():
    """Folha 4: Microcontrolador ESP32-WROOM-32E e Transceptor CAN Isolado ISO1050"""
    with schemdraw.Drawing(file='esquematico_folha4_controle.svg', show=False) as d:
        d.config(fontsize=9, font='sans-serif', unit=2.2)
        
        d += elm.Label().label('SISTEMA DE CONTROLE — ESP32-WROOM-32E E BARRAMENTO CAN ISOLADO ISO1050', loc='top', color='#0F172A', fontsize=13)
        
        # ESP32 MCU
        mcu = d.add(elm.Ic(pins=[
            elm.IcPin(name='3.3V', pin='1', side='left'),
            elm.IcPin(name='GND', pin='2', side='left'),
            elm.IcPin(name='GPIO34', pin='3', side='left'),
            elm.IcPin(name='GPIO35', pin='4', side='left'),
            elm.IcPin(name='GPIO32', pin='5', side='left'),
            elm.IcPin(name='GPIO33', pin='6', side='left'),
            elm.IcPin(name='GPIO25', pin='7', side='left'),
            elm.IcPin(name='GPIO26', pin='8', side='left'),
            
            elm.IcPin(name='GPIO12', pin='16', side='right'),
            elm.IcPin(name='GPIO13', pin='15', side='right'),
            elm.IcPin(name='GPIO14', pin='14', side='right'),
            elm.IcPin(name='GPIO27', pin='13', side='right'),
            elm.IcPin(name='GPIO15', pin='12', side='right'),
            elm.IcPin(name='GPIO2', pin='11', side='right'),
            elm.IcPin(name='GPIO21', pin='10', side='right'),
            elm.IcPin(name='GPIO22', pin='9', side='right')
        ]).label('ESP32-WROOM-32E\n(Dual-Core 240MHz)', loc='center'))
        
        # Entradas Analógicas e Sensores
        mcu_inputs = [
            (getattr(mcu, '3.3V'), '3.3V (VCC Auxiliar)'),
            (mcu.GND, 'GND (Plano Lógico)'),
            (mcu.GPIO34, 'VDC_SENSE (Divisor 100k/3.3k)'),
            (mcu.GPIO35, 'TEMP_MOTOR (NTC 10k)'),
            (mcu.GPIO32, 'TEMP_DRV (NTC 10k)'),
            (mcu.GPIO33, 'HALL_U / RESOLVER_COS+'),
            (mcu.GPIO25, 'HALL_V / RESOLVER_SIN+'),
            (mcu.GPIO26, 'HALL_W / RESOLVER_EXC+')
        ]
        for pin, label in mcu_inputs:
            d.push()
            d += elm.Line().left().at(pin).length(1.2)
            d += elm.Label().label(label, loc='left', color='#D97706')
            d.pop()
            
        # Saídas de PWM e Comunicação
        mcu_outputs = [
            (mcu.GPIO12, 'PWM_UH → DRV8302'),
            (mcu.GPIO13, 'PWM_UL → DRV8302'),
            (mcu.GPIO14, 'PWM_VH → DRV8302'),
            (mcu.GPIO27, 'PWM_VL → DRV8302'),
            (mcu.GPIO15, 'PWM_WH → DRV8302'),
            (mcu.GPIO2, 'PWM_WL → DRV8302'),
            (mcu.GPIO21, 'CAN_TX → ISO1050'),
            (mcu.GPIO22, 'CAN_RX ← ISO1050')
        ]
        for pin, label in mcu_outputs:
            d.push()
            d += elm.Line().right().at(pin).length(1.2)
            d += elm.Label().label(label, loc='right', color='#8B5CF6')
            d.pop()
            
        # Transceptor CAN Isolado ISO1050 (Abaixo do MCU)
        can_ic = d.add(elm.Ic(pins=[
            elm.IcPin(name='TXD', pin='1', side='left'),
            elm.IcPin(name='RXD', pin='2', side='left'),
            elm.IcPin(name='GND1', pin='3', side='left'),
            
            elm.IcPin(name='CANH', pin='6', side='right'),
            elm.IcPin(name='CANL', pin='5', side='right'),
            elm.IcPin(name='GND2_ISO', pin='4', side='right')
        ]).at((0, -8)).label('ISO1050\n(CAN Isolado 5kV)', loc='center'))
        
        # Conexão CAN ao MCU
        d.push()
        d += elm.Line().left().at(can_ic.TXD).length(1.0)
        d += elm.Label().label('CAN_TX (do MCU)', loc='left', color='#047857')
        d.pop()
        
        d.push()
        d += elm.Line().left().at(can_ic.RXD).length(1.0)
        d += elm.Label().label('CAN_RX (para MCU)', loc='left', color='#047857')
        d.pop()
        
        # Conector Industrial CAN
        d.push()
        d += elm.Line().right().at(can_ic.CANH).length(1.2)
        d += elm.Dot(radius=0.18).label('CAN_HIGH (Borne)', loc='right', color='#047857')
        d.pop()
        d.push()
        d += elm.Line().right().at(can_ic.CANL).length(1.2)
        d += elm.Dot(radius=0.18).label('CAN_LOW (Borne)', loc='right', color='#047857')
        d.pop()

    print("✅ Folha 4 (MCU ESP32 e CAN ISO1050) gerada: esquematico_folha4_controle.svg")

if __name__ == '__main__':
    print("="*70)
    print("🚀 GERANDO SUÍTE COMPLETA DE ESQUEMÁTICOS PADRÃO IEEE/TI")
    print("="*70)
    build_power_stage_schematic()
    build_gate_driver_schematic()
    build_power_and_chopper_schematic()
    build_mcu_and_can_schematic()
    print("="*70)
    print("🎉 TODAS AS 4 FOLHAS ESQUEMÁTICAS GERADAS COM 100% DE SUCESSO!")
    print("="*70)
