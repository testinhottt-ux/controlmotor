#!/usr/bin/env python3
"""
Gerador de schematic KiCad válido com todos os 57 componentes
Baseado em arquivo original válido do projeto
"""

import csv

# Ler BOM
bom_components = []
with open('bom.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in enumerate(reader):
        if not row['Referencia'] or row['Referencia'] == 'NOTAS_IMPORTANTES' or not row['Componente']:
            continue
        bom_components.append(row)

print(f"✅ Lidos {len(bom_components)} componentes")

# Usar arquivo original como template e adicionar novos componentes
with open('schematic_incompleto.kicad_sch.bak', 'r', encoding='utf-8') as f:
    original = f.read()

# Extrair a seção de lib_symbols
lib_start = original.find('(lib_symbols')
lib_end = original.find(')', lib_start) + 1
lib_symbols = original[lib_start:lib_end]

# Novo conteúdo completo
header = original[:lib_start]

# Gerar instâncias com UUIDs únicos
instances = ""
import uuid

x_pos = 30
y_pos = 50
y_offset = 80

for idx, comp in enumerate(bom_components[:57]):
    ref = comp[1]['Referencia']
    name = comp[1]['Componente']
    value = comp[1]['Valor']
    comp_type = comp[1]['Tipo']
    
    # Escolher símbolo baseado no tipo
    symbol_map = {
        'MCU': 'MotorCtrl:ESP32',
        'IC Gate Driver': 'MotorCtrl:DRV8302',
        'IC Power Mgmt': 'MotorCtrl:R',
        'IC Sensor': 'MotorCtrl:R',
        'MOSFET': 'MotorCtrl:Q_NMOS',
        'Resistor': 'MotorCtrl:R',
        'Capacitor': 'MotorCtrl:C',
        'Inductor': 'MotorCtrl:R',
        'Ferrite Bead': 'MotorCtrl:R',
        'Diode': 'MotorCtrl:R',
        'TVS Diode': 'MotorCtrl:R',
        'Thermistor': 'MotorCtrl:R',
        'Fuse': 'MotorCtrl:R',
        'Connector': 'MotorCtrl:R',
    }
    
    symbol = symbol_map.get(comp_type, 'MotorCtrl:R')
    u_uuid = str(uuid.uuid4())
    
    # Layout em colunas
    if idx % 6 == 0:
        x_pos = 30
        y_pos += y_offset
    else:
        x_pos += 120
    
    instances += f'''  (symbol (lib_id "{symbol}") (at {x_pos} {y_pos} 0) (unit 1)
    (in_bom yes) (on_board yes)
    (uuid "{u_uuid}")
    (property "Reference" "{ref}" (id 0) (at {x_pos + 25} {y_pos - 7} 0)
      (effects (font (size 1.27 1.27))))
    (property "Value" "{value}" (id 1) (at {x_pos + 25} {y_pos + 8} 0)
      (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (id 2) (at {x_pos} {y_pos} 0)
      (effects (font (size 1.27 1.27)) hide))
    (property "Datasheet" "~" (id 3) (at {x_pos} {y_pos} 0)
      (effects (font (size 1.27 1.27)) hide))
    (pin "1" (uuid "{uuid.uuid4()}"))
    (pin "2" (uuid "{uuid.uuid4()}"))
  )
'''

footer = '''
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''

output = header + lib_symbols + '\n\n' + instances + footer

with open('schematic.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"✅ Arquivo regenerado: schematic.kicad_sch")
print(f"📏 Tamanho: {len(output) / 1024:.1f} KB")
