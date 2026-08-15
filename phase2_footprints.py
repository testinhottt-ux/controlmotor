#!/usr/bin/env python3
"""
phase2_footprints.py - Mapping de componentes → Footprints KiCad (JLCPCB compatible)

Fase 2: Curto Prazo (1-2 dias)
Objetivo: Criar mapa de footprints para cada componente do BOM
"""

import csv
import json
import time
from typing import Dict

# ============================================================================
# MAPA REAL DE FOOTPRINTS (JLCPCB + KiCad padrão)
# ============================================================================

FOOTPRINT_MAP = {
    # MCU + Driver
    'U1': {'footprint': 'Package_BGA:BGA-48_7x7mm_P0.5mm', 'type': 'BGA', 'size': '48-pin'},
    'U2': {'footprint': 'Package_LQFP:LQFP-48_7x7mm_P0.5mm', 'type': 'QFP', 'size': '48-pin'},
    
    # MOSFETs (TO-247 = 3 pinos)
    'Q1': {'footprint': 'Package_TO_SOT_Transistor:TO-247-2', 'type': 'TO-247', 'pins': 3},
    'Q2': {'footprint': 'Package_TO_SOT_Transistor:TO-247-2', 'type': 'TO-247', 'pins': 3},
    'Q3': {'footprint': 'Package_TO_SOT_Transistor:TO-247-2', 'type': 'TO-247', 'pins': 3},
    'Q4': {'footprint': 'Package_TO_SOT_Transistor:TO-247-2', 'type': 'TO-247', 'pins': 3},
    'Q5': {'footprint': 'Package_TO_SOT_Transistor:TO-247-2', 'type': 'TO-247', 'pins': 3},
    'Q6': {'footprint': 'Package_TO_SOT_Transistor:TO-247-2', 'type': 'TO-247', 'pins': 3},
    
    # Capacitores bulk (1210 para 470µF)
    'C1': {'footprint': 'Capacitor_SMD:C_1210_3225Metric', 'type': 'SMD', 'size': '1210'},
    'C2': {'footprint': 'Capacitor_SMD:C_1210_3225Metric', 'type': 'SMD', 'size': '1210'},
    
    # Bootstrap capacitores (0603 para 10µF)
    'C_boot1': {'footprint': 'Capacitor_SMD:C_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'C_boot2': {'footprint': 'Capacitor_SMD:C_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'C_boot3': {'footprint': 'Capacitor_SMD:C_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    
    # Decoupling (0603)
    'Cfilter_1': {'footprint': 'Capacitor_SMD:C_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Cfilter_2': {'footprint': 'Capacitor_SMD:C_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Cfilter_adc': {'footprint': 'Capacitor_SMD:C_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    
    # Resistores (0603)
    'Rgate_u': {'footprint': 'Resistor_SMD:R_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Rgate_v': {'footprint': 'Resistor_SMD:R_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Rgate_w': {'footprint': 'Resistor_SMD:R_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Rgate_ls_u': {'footprint': 'Resistor_SMD:R_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Rgate_ls_v': {'footprint': 'Resistor_SMD:R_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Rgate_ls_w': {'footprint': 'Resistor_SMD:R_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    
    # Indutores (1210)
    'Lvcc': {'footprint': 'Inductor_SMD:L_1210_3225Metric', 'type': 'SMD', 'size': '1210'},
    'Lfilter_u': {'footprint': 'Inductor_SMD:L_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Lfilter_v': {'footprint': 'Inductor_SMD:L_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    'Lfilter_w': {'footprint': 'Inductor_SMD:L_0603_1608Metric', 'type': 'SMD', 'size': '0603'},
    
    # Diodos (SOD-123 para bootstrap)
    'D_bootstrap_u': {'footprint': 'Diode_SMD:D_SOD-123', 'type': 'SOD-123', 'pins': 2},
    'D_bootstrap_v': {'footprint': 'Diode_SMD:D_SOD-123', 'type': 'SOD-123', 'pins': 2},
    'D_bootstrap_w': {'footprint': 'Diode_SMD:D_SOD-123', 'type': 'SOD-123', 'pins': 2},
    
    # TVS diodos (SOD-123)
    'D_tvs_1': {'footprint': 'Diode_SMD:D_SOD-123', 'type': 'SOD-123', 'pins': 2},
    'D_tvs_2': {'footprint': 'Diode_SMD:D_SOD-123', 'type': 'SOD-123', 'pins': 2},
    
    # Hall sensors (DIP-3)
    'Hall_A': {'footprint': 'Package_DIP:DIP-3_W8.89mm', 'type': 'DIP', 'pins': 3},
    'Hall_B': {'footprint': 'Package_DIP:DIP-3_W8.89mm', 'type': 'DIP', 'pins': 3},
    'Hall_C': {'footprint': 'Package_DIP:DIP-3_W8.89mm', 'type': 'DIP', 'pins': 3},
    
    # Conectores
    'Connector_XT60': {'footprint': 'Connector:XT60-M', 'type': 'Connector', 'pins': 2},
    'Connector_motor_u': {'footprint': 'Connector_Samtec:SAMTEC-M-M_L25.02mm_W3.08mm_P2.54mm', 'type': 'Stud M4', 'pins': 1},
    'Connector_motor_v': {'footprint': 'Connector_Samtec:SAMTEC-M-M_L25.02mm_W3.08mm_P2.54mm', 'type': 'Stud M4', 'pins': 1},
    'Connector_motor_w': {'footprint': 'Connector_Samtec:SAMTEC-M-M_L25.02mm_W3.08mm_P2.54mm', 'type': 'Stud M4', 'pins': 1},
    'Connector_aux': {'footprint': 'Connector_JST:JST-PH-2.0mm-4pin', 'type': 'JST-PH', 'pins': 4},
    'Connector_debug': {'footprint': 'Connector_USB:USB_Micro-B_Wuerth-614-105-41-341631', 'type': 'µUSB', 'pins': 5},
    
    # Fuse
    'Fuse1': {'footprint': 'Fuse:Fuse_1206_3216Metric', 'type': 'SMD Fuse', 'size': '1206'},
}

# ============================================================================
# FUNÇÕES
# ============================================================================

def create_footprint_map() -> Dict:
    """Criar mapa JSON de componentes → footprints."""
    return FOOTPRINT_MAP


def export_footprint_csv(footprint_map: Dict, output_file: str):
    """Exportar footprints em CSV (para importar em KiCad)."""
    print(f"[1/2] Exportando footprints para CSV...", end=" ")
    start = time.time()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Reference', 'Footprint', 'Type', 'Description'])
        writer.writeheader()
        
        for ref, data in sorted(footprint_map.items()):
            writer.writerow({
                'Reference': ref,
                'Footprint': data['footprint'],
                'Type': data['type'],
                'Description': f"{data.get('pins', 'N/A')} pins, {data.get('size', 'N/A')}"
            })
    
    print(f"✓ ({time.time() - start:.2f}s)")
    print(f"   → Gerado: {output_file}")


def export_footprint_json(footprint_map: Dict, output_file: str):
    """Exportar footprints em JSON (para processamento posterior)."""
    print(f"[2/2] Exportando footprints para JSON...", end=" ")
    start = time.time()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(footprint_map, f, indent=2)
    
    print(f"✓ ({time.time() - start:.2f}s)")
    print(f"   → Gerado: {output_file}")


def generate_footprint_report(footprint_map: Dict) -> str:
    """Gerar relatório de footprints por tipo."""
    report = "\n📊 FOOTPRINT REPORT\n"
    report += "═" * 70 + "\n\n"
    
    # Agrupar por tipo
    by_type = {}
    for ref, data in footprint_map.items():
        ftype = data['type']
        if ftype not in by_type:
            by_type[ftype] = []
        by_type[ftype].append(ref)
    
    # Sortear e formatar
    for ftype in sorted(by_type.keys()):
        refs = by_type[ftype]
        report += f"  {ftype:.<30} {len(refs):>3} componentes\n"
        report += f"    {', '.join(refs[:5])}"
        if len(refs) > 5:
            report += f", ... +{len(refs)-5} mais"
        report += "\n\n"
    
    report += f"  {'TOTAL':.<30} {len(footprint_map):>3} componentes\n"
    report += "═" * 70 + "\n"
    
    return report


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("  FASE 2: FOOTPRINT MAPPING")
    print("="*70 + "\n")
    
    # Criar mapa
    footprint_map = create_footprint_map()
    
    # Exportar em múltiplos formatos
    export_footprint_csv(footprint_map, 'footprints_mapping.csv')
    export_footprint_json(footprint_map, 'footprints_mapping.json')
    
    # Gerar relatório
    print(generate_footprint_report(footprint_map))
    
    print("✅ Footprints gerados e prontos para KiCad")
    print("   Próximo: Importar em KiCad GUI: Tools → Footprint Association")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
