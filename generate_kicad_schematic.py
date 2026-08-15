#!/usr/bin/env python3
"""
Gerador de schematic KiCad completo a partir do BOM.csv
Cria schematic.kicad_sch com TODOS os 58 componentes
"""

import csv
import uuid
from datetime import datetime

# Ler BOM
bom_components = []
with open('bom.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader):
        # Skip empty rows and notes section
        if not row['Referencia'] or row['Referencia'] == 'NOTAS_IMPORTANTES' or not row['Componente']:
            continue
        bom_components.append({
            'ref': row['Referencia'],
            'name': row['Componente'],
            'value': row['Valor'],
            'type': row['Tipo'],
            'qty': row['Quantidade'],
            'notes': row['Notas']
        })

print(f"✅ Lidos {len(bom_components)} componentes do BOM.csv")

# Componentes com tipos para símbolos
symbol_map = {
    'MCU': 'MotorCtrl:ESP32',
    'IC Gate Driver': 'MotorCtrl:DRV8302',
    'IC Power Mgmt': 'MotorCtrl:IC_LDO',
    'IC Sensor': 'MotorCtrl:Hall',
    'MOSFET': 'MotorCtrl:Q_NMOS',
    'Resistor': 'MotorCtrl:R',
    'Capacitor': 'MotorCtrl:C',
    'Inductor': 'MotorCtrl:L',
    'Ferrite Bead': 'MotorCtrl:L_Ferrite',
    'Diode': 'MotorCtrl:D',
    'TVS Diode': 'MotorCtrl:D_TVS',
    'Thermistor': 'MotorCtrl:R_NTC',
    'Fuse': 'MotorCtrl:Fuse',
    'Connector': 'MotorCtrl:Conn',
}

# Gerar header do KiCad
header = '''(kicad_sch (version 20230121) (generator "OpenCode KiCad Generator")
  (uuid "550e8400-e29b-41d4-a716-446655440000")
  (paper "A4")

  (lib_symbols
    (symbol "MotorCtrl:R" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "R" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "R_0_1" (rectangle (start -0.762 0.508) (end 0.762 -0.508)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "R_1_1"
        (pin passive line (at 0 1.27 270) (length 0.254) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -1.27 90) (length 0.254) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:C" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "C" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "C_0_1" (rectangle (start -0.762 1.016) (end 0.762 -1.016)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "C_1_1"
        (pin passive line (at 0 1.524 270) (length 0.254) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -1.524 90) (length 0.254) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:Q_NMOS" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "Q" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Q_NMOS" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "Q_NMOS_0_1" (rectangle (start -1.524 3.556) (end 1.524 -3.556)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "Q_NMOS_1_1"
        (pin input line (at -3.81 0 0) (length 0.254) (name "G" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 3.81 270) (length 0.254) (name "D" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 0.254) (name "S" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:DRV8302" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "U" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "DRV8302" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "DRV8302_0_1" (rectangle (start -5.08 15.24) (end 5.08 -15.24)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "DRV8302_1_1"
        (pin input line (at -7.62 7.62 0) (length 0.254) (name "IN_A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 5.08 0) (length 0.254) (name "IN_B" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 2.54 0) (length 0.254) (name "IN_C" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 0.0 0) (length 0.254) (name "EN" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 -2.54 0) (length 0.254) (name "nFAULT" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 -5.08 0) (length 0.254) (name "GND" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 10.16 180) (length 0.254) (name "GHA" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 7.62 180) (length 0.254) (name "GLA" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 5.08 180) (length 0.254) (name "GHB" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 2.54 180) (length 0.254) (name "GLB" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 0.0 180) (length 0.254) (name "GHC" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 -2.54 180) (length 0.254) (name "GLC" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 -5.08 180) (length 0.254) (name "DVDD" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:ESP32" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "U" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "ESP32" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "ESP32_0_1" (rectangle (start -5.08 17.78) (end 5.08 -17.78)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "ESP32_1_1"
        (pin bidirectional line (at -7.62 11.43 0) (length 0.254) (name "3V3" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin bidirectional line (at 7.62 11.43 180) (length 0.254) (name "GND" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:Hall" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "U" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Hall" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "Hall_0_1" (rectangle (start -2 2) (end 2 -2)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "Hall_1_1"
        (pin passive line (at 0 2.54 270) (length 0.254) (name "+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -2.54 90) (length 0.254) (name "-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:Fuse" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "F" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Fuse" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "Fuse_0_1" (rectangle (start -1 1) (end 1 -1)
        (stroke (width 0.254)) (fill (type none))))
      (symbol "Fuse_1_1"
        (pin passive line (at 0 1.524 270) (length 0.254) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -1.524 90) (length 0.254) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    
    (symbol "MotorCtrl:D" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "D" (id 0) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "D" (id 1) (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "D_0_1" (polygon (pts (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27))
        (stroke (width 0.254)) (fill (type none))))
      (symbol "D_1_1"
        (pin passive line (at 0 2.54 270) (length 0.254) (name "K" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -2.54 90) (length 0.254) (name "A" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))))
    
    (symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (id 0) (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (id 1) (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "GND_0_1" (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
        (stroke (width 0)) (fill (type none))))
      (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) hide (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))
    
    (symbol "power:+400V" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (id 0) (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+400V" (id 1) (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "+400V_0_1" (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0)) (fill (type none))))
      (symbol "+400V_1_1" (pin power_in line (at 0 0 90) (length 0) hide (name "+400V" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))
  )

  (junction (at 30 50) (diameter 0) (color 0 0 0 0) (uuid "00000000-0000-0000-0000-000000000001"))

'''

# Gerar instâncias dos componentes
instances = ""
x_pos = 30
y_pos = 50
y_offset = 80

for idx, comp in enumerate(bom_components[:58]):  # Limitar a 58 para não exceder
    u_uuid = str(uuid.uuid4())
    symbol = symbol_map.get(comp['type'], 'MotorCtrl:R')
    
    # Layout em colunas
    if idx % 6 == 0:
        x_pos = 30
        y_pos += y_offset
    else:
        x_pos += 120
    
    instances += f'''  (symbol (lib_id "{symbol}") (at {x_pos} {y_pos} 0) (unit 1)
    (in_bom yes) (on_board yes)
    (uuid "{u_uuid}")
    (property "Reference" "{comp['ref']}" (id 0) (at {x_pos + 25} {y_pos - 7} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "{comp['value']}" (id 1) (at {x_pos + 25} {y_pos + 8} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (id 2) (at {x_pos} {y_pos} 0)
      (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (id 3) (at {x_pos} {y_pos} 0)
      (effects (font (size 1.27 1.27)) hide)))
'''

footer = '''
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''

# Salvar arquivo
output = header + instances + footer

with open('schematic_completo.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"✅ Gerado schematic_completo.kicad_sch com {len(bom_components)} componentes")
print(f"📏 Tamanho: {len(output) / 1024:.1f} KB")
