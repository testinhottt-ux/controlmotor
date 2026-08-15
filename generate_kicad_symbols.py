#!/usr/bin/env python3
"""
generate_kicad_symbols.py - Adicionar 57 símbolos reais ao schematic KiCad

Estratégia: S-expression manual (Abordagem 2 de solucoes.md)
- Ler bom.csv
- Gerar s-expression para cada componente
- Inserir antes de sheet_instances
- Validar com kicad-cli
"""

import csv
import re
import time
import sys
from typing import Dict, List, Tuple

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BOM_FILE = "bom.csv"
SCHEMATIC_INPUT = "schematic.kicad_sch"
SCHEMATIC_OUTPUT = "schematic_completo.kicad_sch"

# Mapping de referência → símbolo KiCad (biblioteca)
SYMBOL_MAP = {
    'U1': ('Microcontroller_MCU_Espressif_ESP32', 'ESP32-WROOM-32'),
    'U2': ('Motor_Control_DRV8302', 'DRV8302'),
    # MOSFETs
    'Q1': ('Transistor_FET_IPP65R600P7', 'IPP65R600P7'),
    'Q2': ('Transistor_FET_IPP65R600P7', 'IPP65R600P7'),
    'Q3': ('Transistor_FET_IPP65R600P7', 'IPP65R600P7'),
    'Q4': ('Transistor_FET_IPP65R600P7', 'IPP65R600P7'),
    'Q5': ('Transistor_FET_IPP65R600P7', 'IPP65R600P7'),
    'Q6': ('Transistor_FET_IPP65R600P7', 'IPP65R600P7'),
    # Capacitores
    'C1': ('Capacitor_Bulk_470uF', '470µF 450V'),
    # Bootstrap capacitores
    'C_boot1': ('Capacitor_10uF_50V', '10µF 50V'),
    'C_boot2': ('Capacitor_10uF_50V', '10µF 50V'),
    'C_boot3': ('Capacitor_10uF_50V', '10µF 50V'),
    # Decoupling
    'Cfilter_1': ('Capacitor_100uF_10V', '100µF 10V'),
    'Cfilter_2': ('Capacitor_100nF', '100nF'),
    'Cfilter_adc': ('Capacitor_10nF', '10nF'),
    # Resistores (simplified)
    'Rgate_u': ('Resistor_10ohm_1_4w', '10Ω'),
    'Rgate_v': ('Resistor_10ohm_1_4w', '10Ω'),
    'Rgate_w': ('Resistor_10ohm_1_4w', '10Ω'),
    'Rgate_ls_u': ('Resistor_10k_1_4w', '10kΩ'),
    'Rgate_ls_v': ('Resistor_10k_1_4w', '10kΩ'),
    'Rgate_ls_w': ('Resistor_10k_1_4w', '10kΩ'),
    # Indutores
    'Lvcc': ('Inductor_10uH', '10µH'),
    'Lfilter_u': ('Ferrite_Bead_1uH', '1µH'),
    'Lfilter_v': ('Ferrite_Bead_1uH', '1µH'),
    'Lfilter_w': ('Ferrite_Bead_1uH', '1µH'),
    # Diodos
    'D_bootstrap_u': ('Diode_3A_200V', '3A 200V'),
    'D_bootstrap_v': ('Diode_3A_200V', '3A 200V'),
    'D_bootstrap_w': ('Diode_3A_200V', '3A 200V'),
    'D_tvs_1': ('TVS_Diode_50V', '50V'),
    'D_tvs_2': ('TVS_Diode_50V', '50V'),
    # Sensores Hall
    'Hall_A': ('IC_Sensor_Hall_A3144', 'A3144'),
    'Hall_B': ('IC_Sensor_Hall_A3144', 'A3144'),
    'Hall_C': ('IC_Sensor_Hall_A3144', 'A3144'),
    # Conectores
    'Connector_XT60': ('Connector_XT60', 'XT60'),
    'Connector_motor_u': ('Connector_Stud_M4', 'M4'),
    'Connector_motor_v': ('Connector_Stud_M4', 'M4'),
    'Connector_motor_w': ('Connector_Stud_M4', 'M4'),
    'Connector_aux': ('Connector_JST_PH', 'JST PH'),
    'Connector_debug': ('Connector_MicroUSB', 'µUSB'),
    'Fuse1': ('Fuse_50A_Automotive', '50A'),
}

# ============================================================================
# FUNÇÕES
# ============================================================================

def parse_bom(filepath: str) -> Dict[str, Dict]:
    """
    Parse bom.csv em dicionário estruturado.
    Filtra apenas linhas com referência válida e expande ranges (e.g., Q1-Q3 → Q1, Q2, Q3).
    
    CC: 6 (loop + regex + range expansion)
    """
    print(f"[1/4] Parsing {filepath}...", end=" ")
    start = time.time()
    
    bom_dict = {}
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ref = row['Referencia'].strip()
            # Filtrar apenas componentes reais
            if not ref or not re.match(r'^[A-Za-z_]+', ref):
                continue
            
            # Expandir ranges tipo "Q1-Q3" → ["Q1", "Q2", "Q3"]
            if '-' in ref and re.match(r'^([A-Z]+)(\d+)-\1(\d+)$', ref):
                # Match: Q1-Q3 → ('Q', '1', '3')
                match = re.match(r'^([A-Z]+)(\d+)-\1(\d+)$', ref)
                if match:
                    prefix, start_num, end_num = match.groups()
                    start_num, end_num = int(start_num), int(end_num)
                    # Expandir para Q1, Q2, Q3
                    for num in range(start_num, end_num + 1):
                        expanded_ref = f"{prefix}{num}"
                        bom_dict[expanded_ref] = {
                            'componente': row['Componente'],
                            'valor': row['Valor'],
                            'tipo': row['Tipo'],
                        }
                    continue
            
            # Referências simples (U1, C1, R_shunt_u, etc)
            if re.match(r'^[A-Za-z_]+\d+', ref):
                bom_dict[ref] = {
                    'componente': row['Componente'],
                    'valor': row['Valor'],
                    'tipo': row['Tipo'],
                }
    
    elapsed = time.time() - start
    print(f"✓ {len(bom_dict)} componentes ({elapsed:.2f}s)")
    return bom_dict


def generate_symbol_sexpression(ref: str, valor: str, x: float = 50, y: float = 50) -> str:
    """
    Gera s-expression para um símbolo KiCad.
    
    Formato mínimo para KiCad 9.0:
    (symbol (name "REF") (at X Y)
      (property "Reference" "REF")
      (property "Value" "VALOR")
      (uuid "00000000-...")
    )
    
    CC: 2 (string formatting)
    """
    import uuid as uuid_module
    symbol_uuid = str(uuid_module.uuid4())
    
    # Incrementar Y para evitar overlap
    y_offset = y + (len(ref) * 10) % 200
    
    return f'''  (symbol (name "{ref}") (at {x} {y_offset})
    (property "Reference" "{ref}")
    (property "Value" "{valor}")
    (property "Footprint" "")
    (uuid "{symbol_uuid}")
    (pin "1" (uuid "{uuid_module.uuid4()}"))
  )
'''

def insert_symbols_into_schematic(
    bom_dict: Dict, 
    schematic_input: str,
    schematic_output: str
) -> Tuple[bool, str]:
    """
    Insere símbolos antes de 'sheet_instances'.
    
    CC: 6 (parsing + string operations + validation)
    """
    print(f"[2/4] Reading {schematic_input}...", end=" ")
    start = time.time()
    
    with open(schematic_input, 'r') as f:
        content = f.read()
    
    # Gerar símbolos para cada componente
    symbols = []
    for ref in sorted(bom_dict.keys()):
        valor = bom_dict[ref]['valor']
        symbol = generate_symbol_sexpression(ref, valor)
        symbols.append(symbol)
    
    symbols_text = '\n'.join(symbols)
    
    # Inserir antes de 'sheet_instances'
    insertion_point = content.find('  (sheet_instances')
    if insertion_point == -1:
        return False, "❌ Não encontrado 'sheet_instances' no schematic"
    
    # Inserir os símbolos
    new_content = (
        content[:insertion_point] +
        '\n' + symbols_text + '\n' +
        content[insertion_point:]
    )
    
    print(f"✓ ({time.time() - start:.2f}s)")
    
    print(f"[3/4] Writing {schematic_output}...", end=" ")
    start = time.time()
    
    with open(schematic_output, 'w') as f:
        f.write(new_content)
    
    elapsed = time.time() - start
    print(f"✓ ({elapsed:.2f}s)")
    
    return True, f"✅ {len(bom_dict)} símbolos inseridos"


def validate_schematic(schematic_path: str) -> Tuple[bool, str]:
    """
    Valida schematic com kicad-cli.
    
    CC: 3 (subprocess + error handling)
    """
    import subprocess
    
    print(f"[4/4] Validating with kicad-cli...", end=" ")
    start = time.time()
    
    try:
        result = subprocess.run(
            ['kicad-cli', 'sch', 'export', 'netlist', schematic_path, '-o', '/tmp/validate.net'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        elapsed = time.time() - start
        if result.returncode == 0:
            print(f"✓ ({elapsed:.2f}s)")
            return True, "✅ Validação passou"
        else:
            return False, f"❌ Validação falhou:\n{result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return False, "❌ Validação timeout"
    except FileNotFoundError:
        return False, "❌ kicad-cli não encontrado"


def main():
    """Main entry point (CC: 5)"""
    print("\n" + "="*70)
    print("  GERANDO SÍMBOLOS REAIS PARA SCHEMATIC KICAD 9.0")
    print("="*70 + "\n")
    
    try:
        # Etapa 1: Parse BOM
        bom_dict = parse_bom(BOM_FILE)
        
        if not bom_dict:
            print("❌ Nenhum componente encontrado no BOM")
            return False
        
        # Etapa 2-3: Inserir símbolos e validar
        success, msg = insert_symbols_into_schematic(
            bom_dict, 
            SCHEMATIC_INPUT, 
            SCHEMATIC_OUTPUT
        )
        
        if not success:
            print(msg)
            return False
        
        print(msg)
        
        # Etapa 4: Validação
        valid, msg = validate_schematic(SCHEMATIC_OUTPUT)
        print(msg)
        
        if valid:
            print(f"\n✅ SUCESSO! Arquivo gerado: {SCHEMATIC_OUTPUT}")
            print(f"   Próximo passo: cp {SCHEMATIC_OUTPUT} {SCHEMATIC_INPUT}")
            print(f"   Ou: kicad {SCHEMATIC_OUTPUT}")
        
        return valid
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        print("="*70 + "\n")


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
