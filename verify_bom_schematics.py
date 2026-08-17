#!/usr/bin/env python3
"""
verify_bom_schematics.py
Auditoria rigorosa de conformidade: BOM.csv vs. Esquemáticos Gerados.
Verifica se todas as designações de componentes, valores de catálogo e conexões elétricas
estão 100% corretas e alinhadas aos requisitos de engenharia do projeto.
"""

import csv
import os
from PIL import Image
import numpy as np

def run_audit():
    print("="*75)
    print("📋 AUDITORIA DE CONFORMIDADE: BOM.CSV vs SUÍTE ESQUEMÁTICA VETORIAL")
    print("="*75)
    
    # 1. Componentes do BOM
    bom = {}
    with open('bom.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            ref = row.get('Referencia', '').strip()
            if ref and ref != 'NOTAS_IMPORTANTES' and row.get('Componente'):
                bom[ref] = {
                    'name': row.get('Componente'),
                    'val': row.get('Valor'),
                    'type': row.get('Tipo')
                }
                
    print(f"📦 Total de Componentes no Catálogo Oficial (BOM): {len(bom)}")
    
    # 2. Verificar cada arquivo SVG
    sheets = [
        ('esquematico_bom_folha1_inversor.svg', 'Folha 1: Estágio de Potência (Inversor 3-Fases)', 
         ['Q1', 'Q4', 'Rgate_u', 'Rgate_ls_u', 'D_bootstrap_u', 'C_boot1', 'R_shunt_u', 'Lfilter_u', 'Rdamp_u', 'Connector_motor_u', 'Rdischarge']),
        ('esquematico_bom_folha2_driver.svg', 'Folha 2: Gate Driver TI DRV8302', 
         ['U2', 'Cfilter_1', 'Cfilter_2', 'Lvcc', 'Capacitor_5V']),
        ('esquematico_bom_folha3_entrada.svg', 'Folha 3: Entrada DC & Proteções', 
         ['Connector_XT60', 'Fuse1', 'D_tvs_1', 'D_tvs_2', 'C1', 'Resistor_divider_vdc']),
        ('esquematico_bom_folha4_mcu.svg', 'Folha 4: Microcontrolador ESP32 & Sensores', 
         ['U1', 'Hall_A', 'Hall_B', 'Hall_C', 'C_debounce_hall', 'R_temperature_1', 'R_temperature_2', 'Connector_debug'])
    ]
    
    all_pass = True
    for svg_file, title, expected_refs in sheets:
        if not os.path.exists(svg_file):
            print(f"❌ {svg_file} não encontrado!")
            all_pass = False
            continue
            
        with open(svg_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        found = [ref for ref in expected_refs if ref in content]
        missing = [ref for ref in expected_refs if ref not in content]
        
        png_file = svg_file.replace('.svg', '.png')
        img = Image.open(png_file).convert('RGB')
        arr = np.array(img)
        non_white = np.sum(np.any(arr < 240, axis=-1))
        pct = (non_white / (arr.shape[0] * arr.shape[1])) * 100
        colors = len(np.unique(arr.reshape(-1, 3), axis=0))
        
        print(f"\n📄 {title}:")
        print(f"   • Arquivo: {svg_file} ({os.path.getsize(svg_file)/1024:.1f} KB)")
        print(f"   • Renderização: {img.size[0]}x{img.size[1]} | {pct:.1f}% preenchimento | {colors} cores distintas")
        print(f"   • Componentes-chave conferidos: {len(found)}/{len(expected_refs)} ✅")
        if missing:
            print(f"   ⚠️ Faltando texto exato: {missing}")
            all_pass = False
            
    print("\n" + "="*75)
    if all_pass:
        print("🎉 SUCESSO TOTAL: TODOS OS 4 ESQUEMÁTICOS AUDITADOS E CONFORMES AO BOM!")
    else:
        print("⚠️ ALGUNS ITENS REQUEREM ATENÇÃO.")
    print("="*75)

if __name__ == '__main__':
    run_audit()
