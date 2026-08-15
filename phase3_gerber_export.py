#!/usr/bin/env python3
"""
phase3_gerber_export.py - Exportar Gerber files para JLCPCB

Fase 3: Longo Prazo (1-2 semanas)
Objetivo: Gerar arquivos para submissão JLCPCB
"""

import subprocess
import os
import json
import time
from pathlib import Path
from typing import Tuple, List

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

PCB_FILE = "layout.kicad_pcb"  # Será criado em Fase 2 via KiCad GUI
GERBER_DIR = "gerbers"
BOM_FILE = "bom.csv"

# Arquivos Gerber necessários para JLCPCB
GERBER_LAYERS = {
    'F.Cu': 'Top copper layer',
    'B.Cu': 'Bottom copper layer',
    'F.Silks': 'Front silkscreen',
    'B.Silks': 'Back silkscreen',
    'F.Mask': 'Front solder mask',
    'B.Mask': 'Back solder mask',
    'Dwgs.User': 'Board outline (edge cuts)',
}

# ============================================================================
# FUNÇÕES
# ============================================================================

def create_gerber_directory():
    """Criar diretório para exportação Gerber."""
    if not os.path.exists(GERBER_DIR):
        os.makedirs(GERBER_DIR)
        print(f"✓ Criado diretório: {GERBER_DIR}/")
    return GERBER_DIR


def export_gerbers_kicad_cli(pcb_file: str, output_dir: str) -> Tuple[bool, str]:
    """
    Exportar Gerber files usando kicad-cli.
    
    Nota: Requer que layout.kicad_pcb exista (criado em Fase 2 via KiCad GUI)
    """
    if not os.path.exists(pcb_file):
        return False, f"❌ PCB file não encontrado: {pcb_file}"
    
    print(f"[1/3] Exportando Gerber files via kicad-cli...", end=" ", flush=True)
    start = time.time()
    
    try:
        result = subprocess.run(
            ['kicad-cli', 'pcb', 'export', 'gerbers', pcb_file, '-o', output_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print(f"✓ ({elapsed:.2f}s)")
            return True, f"✅ Gerber files exportados para {output_dir}/"
        else:
            return False, f"❌ kicad-cli falhou: {result.stderr[:200]}"
    
    except subprocess.TimeoutExpired:
        return False, "❌ kicad-cli timeout"
    except FileNotFoundError:
        return False, "❌ kicad-cli não encontrado"


def export_drill_files(pcb_file: str, output_dir: str) -> Tuple[bool, str]:
    """Exportar arquivos de furação (NC drill)."""
    if not os.path.exists(pcb_file):
        return False, "PCB file não encontrado"
    
    print(f"[2/3] Exportando drill files...", end=" ", flush=True)
    start = time.time()
    
    try:
        result = subprocess.run(
            ['kicad-cli', 'pcb', 'export', 'drill', pcb_file, '-o', output_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print(f"✓ ({elapsed:.2f}s)")
            return True, "✅ Drill files exportados"
        else:
            return False, f"⚠️  Drill export skipped (pode ser normal se não há furos)"
    
    except:
        return False, "⚠️  Drill export indisponível"


def export_pos_file(pcb_file: str, output_file: str) -> Tuple[bool, str]:
    """Exportar arquivo de posicionamento (pick-and-place)."""
    if not os.path.exists(pcb_file):
        return False, "PCB file não encontrado"
    
    print(f"[3/3] Exportando posicionamento (PnP)...", end=" ", flush=True)
    start = time.time()
    
    try:
        result = subprocess.run(
            ['kicad-cli', 'pcb', 'export', 'pos', pcb_file, '-o', output_file, '--format', 'csv'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print(f"✓ ({elapsed:.2f}s)")
            return True, f"✅ PnP file exportado: {output_file}"
        else:
            return False, f"⚠️  PnP export skipped"
    
    except:
        return False, "⚠️  PnP export indisponível"


def verify_gerber_files(gerber_dir: str) -> Tuple[int, List[str]]:
    """Verificar quantos arquivos Gerber foram criados."""
    if not os.path.exists(gerber_dir):
        return 0, []
    
    files = []
    for ext in ['gbr', 'gbl', 'gbs', 'gkf', 'gbp', 'GBL', 'GBS', 'GKF', 'GBP']:
        files.extend(Path(gerber_dir).glob(f'*.{ext}'))
    
    return len(files), [f.name for f in sorted(files)]


def create_jlcpcb_submission_checklist() -> str:
    """Criar checklist para submissão JLCPCB."""
    checklist = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   JLCPCB SUBMISSION CHECKLIST                             ║
╚════════════════════════════════════════════════════════════════════════════╝

ANTES DE SUBMETER:

□ Arquivos Gerber
  □ gerbers/layout-F.Cu.gbr (cobre superior)
  □ gerbers/layout-B.Cu.gbr (cobre inferior)
  □ gerbers/layout-F.Mask.gbr (máscara superior)
  □ gerbers/layout-B.Mask.gbr (máscara inferior)
  □ gerbers/layout-F.Silks.gbr (serigrafia superior)
  □ gerbers/layout-B.Silks.gbr (serigrafia inferior)
  □ gerbers/layout-Edge.Cut.gbr (contorno)

□ Arquivo de Furação
  □ gerbers/layout.drl (furação via kicad-cli)

□ BOM
  □ BOM.csv revisado com JLCPCB part numbers
  □ Colunas: Reference, Value, Footprint, Quantity, Supplier, Supplier SKU

□ Posicionamento (Pick & Place)
  □ pos_file.csv (coordenadas X/Y de cada componente)

□ Documentação
  □ schematic_kicad9.pdf (aprovado)
  □ manufacturing_notes.md (notas de fabricação)

CONFIGURAÇÕES RECOMENDADAS (no site JLCPCB):

✓ Placa: FR-4 2-layer (ou 4-layer se necessário)
✓ Espessura: 1.6mm
✓ Cobre: 1oz (padrão)
✓ Máscara de solder: Verde (padrão)
✓ Serigrafia: Branco
✓ Acabamento: HASL (Hot Air Solder Leveling)
✓ Furação: PTH + NPTH (se necessário)
✓ QA: Enabled (Qualidade)

═════════════════════════════════════════════════════════════════════════════

PRÓXIMAS AÇÕES:

1. Upload dos arquivos Gerber (arquivo ZIP)
2. Upload de BOM.csv
3. Review automático do JLCPCB
4. Pagamento
5. Fabricação (7-10 dias)
6. Envio

═════════════════════════════════════════════════════════════════════════════
"""
    return checklist


def generate_manufacturing_notes() -> str:
    """Gerar notas técnicas de fabricação."""
    notes = """# Manufacturing Notes - Controlador PMSM/BLDC

## Especificações de PCB

- **Tamanho**: 150mm × 100mm (4 camadas, FR-4, 2oz Cu)
- **Espessura**: 1.6mm
- **Acabamento**: HASL (Hot Air Solder Leveling)
- **Máscara de solder**: Verde
- **Serigrafia**: Branco
- **Via mínima**: 0.3mm drill / 0.5mm pad
- **Clearance mínimo**: 0.2mm
- **Espessura de trilha**: ≥10mil (0.254mm) para correntes >10A

## Componentes Críticos

### MOSFETs (Q1-Q6): TO-247
- **Dissipação térmica**: ~170W @ 50A contínuo
- **Heatsink**: Alumínio 300×200×10mm (0.3K/W)
- **Pasta térmica**: 3W/mK (Arctic Silver ou equivalente)
- **Vias térmicas**: ~200 sob cada MOSFET

### Capacitores Bulk (C1, C2): 470µF 450V
- **ESR máximo**: 20mΩ (crítico para estabilidade)
- **Localização**: Próximo ao XT60 (entrada DC)
- **Distância máxima**: <50mm de fonte

### Sensores Hall (Hall_A/B/C)
- **Calibração**: Verificar durante testes
- **Alimentação**: 5V referenciada a GND
- **Comprimento do fio**: ≤1m (para minimizar ruído)

## Testes Recomendados

1. **Continuidade** (multímetro)
   - VCC → GND não deve dar curto < 10Ω
   - Fases U/V/W não devem estar conectadas entre si

2. **Polaridade**
   - Verificar XT60: +400V no pino vermelho

3. **Resistência de isolamento**
   - Mega-ohm meter: >1MΩ entre GND e qualquer trilha de potência

4. **Funcionamento** (com firmware ESP32)
   - Alimentar com fonte limitada (0-10A)
   - Verificar leitura dos sensores Hall
   - Testar PWM dos gates com osciloscópio

## Notas de Solda

- **Temperatura de reflow**: 240-260°C, pico <260°C
- **Tempo acima de 217°C**: <60s
- **Componentes suscetíveis**: MOSFETs (verificar datasheet)

## BOM Completo

Ver arquivo: BOM.csv (57 componentes + notas)

---

**Data**: 2026-08-14  
**Revisão**: 1.0  
**Status**: Pronto para Fabricação
"""
    return notes


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("  FASE 3: GERBER EXPORT + JLCPCB SUBMISSION")
    print("="*70 + "\n")
    
    # ✅ Criar diretório
    create_gerber_directory()
    print()
    
    # ⚠️ Avisar que PCB file é prerequisito
    print("⚠️  NOTA: Este script requer que layout.kicad_pcb exista")
    print("   (criado em Fase 2 via KiCad GUI)\n")
    
    if not os.path.exists(PCB_FILE):
        print(f"❌ PCB_FILE não encontrado: {PCB_FILE}")
        print("\n📝 PLANO: Quando layout.kicad_pcb estiver pronto, rode:")
        print(f"   $ python3 phase3_gerber_export.py\n")
        print("="*70)
        return False
    
    # Exportar
    success1, msg1 = export_gerbers_kicad_cli(PCB_FILE, GERBER_DIR)
    print(msg1 + "\n")
    
    success2, msg2 = export_drill_files(PCB_FILE, GERBER_DIR)
    print(msg2 + "\n")
    
    success3, msg3 = export_pos_file(PCB_FILE, "pos_file.csv")
    print(msg3 + "\n")
    
    # Verificar
    num_gerbers, gerber_files = verify_gerber_files(GERBER_DIR)
    if num_gerbers > 0:
        print(f"✅ Encontrados {num_gerbers} arquivos Gerber:")
        for fname in gerber_files[:5]:
            print(f"   • {fname}")
        if len(gerber_files) > 5:
            print(f"   ... + {len(gerber_files) - 5} mais")
    else:
        print("⚠️  Nenhum arquivo Gerber gerado (verifique PCB file)")
    
    print("\n" + "="*70)
    
    # Salvar checklist e notas
    with open("JLCPCB_CHECKLIST.md", 'w') as f:
        f.write(create_jlcpcb_submission_checklist())
    
    with open("manufacturing_notes.md", 'w') as f:
        f.write(generate_manufacturing_notes())
    
    print("✅ Documentação salva:")
    print("   • JLCPCB_CHECKLIST.md (use para submissão)")
    print("   • manufacturing_notes.md (compartilhe com fornecedor)")
    print("\n" + "="*70 + "\n")
    
    return True


if __name__ == '__main__':
    success = main()
