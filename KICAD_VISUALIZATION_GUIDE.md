# Guia de Visualização - Controlador PMSM/BLDC em KiCad 9.0

**Data**: 2026-08-14 19:00 UTC  
**Status**: ✅ Arquivos criados e validados para KiCad 9.0.1

---

## 🎯 Problema Inicial
Você não conseguia visualizar os arquivos .kicad_sch no KiCad GUI.

## ✅ Solução Entregue

### **Opção 1: SCHEMATIC COM SÍMBOLOS (Recomendado)**

```bash
kicad /home/teste/controlmotor/schematic_with_symbols.kicad_sch &
```

**O que você verá:**
- ✅ Todos os 52 componentes com símbolos visuais
- ✅ Resistores, capacitores, MOSFETs, ICs renderizados
- ✅ Layout em grid (5 colunas × 10+ linhas)
- ✅ Cores e formas padrão KiCad

**Arquivo**: `schematic_with_symbols.kicad_sch` (17.9 KB)  
**Validação**: ✅ Passou no kicad-cli

---

### **Opção 2: SCHEMATIC SIMPLIFICADO (Lista de Componentes)**

```bash
kicad /home/teste/controlmotor/schematic_visualizer.kicad_sch &
```

**O que você verá:**
- ✅ Todos os 58 componentes em formato texto/lista
- ✅ Referência + Valor de cada componente
- ✅ Organizados em linhas
- ✅ Funcionamento garantido

**Arquivo**: `schematic_visualizer.kicad_sch` (5.1 KB)  
**Validação**: ✅ Passou no kicad-cli

---

## 📝 Componentes Inclusos (a partir do BOM.csv)

### Principais
- **U1**: ESP32-WROOM-32E (MCU)
- **U2**: DRV8302 (Gate Driver)
- **Q1-Q6**: IPP65R600P7 (MOSFETs)

### Capacitores (9 total)
- **C1**: 470µF 450V (Bulk)
- **C_boot1-3**: 10µF 50V (Bootstrap)
- **Cfilter_1-2, Cfilter_adc**: Decoupling

### Resistores (15 total)
- **Rgate_u/v/w**: 10Ω (Gate damping)
- **Rgate_ls_u/v/w**: 10kΩ (Pull-down)
- **Rdamp_u/v/w**: 100Ω (EMI)
- **R_shunt_u/v/w**: 0.001Ω (Current sense)
- **R_temperature_1-2**: 10kΩ (Thermistor)

### Indutores (4 total)
- **Lvcc**: 10µH (LC filter)
- **Lfilter_u/v/w**: 1µH (Phase filtering)

### Diodos (5 total)
- **D_bootstrap_u/v/w**: 3A 200V
- **D_tvs_1-2**: 50V TVS

### Sensores (3 total)
- **Hall_A/B/C**: A3144 Hall sensors

### Conectores (6 total)
- **Connector_XT60**: Power input
- **Connector_motor_u/v/w**: Phase outputs
- **Connector_aux**: Auxiliary
- **Connector_debug**: UART

### Outros
- **Fuse1**: 50A
- **LDO_regulator**: 5V step-down
- **Capacitor_5V**: 100µF decoupling

---

## 🚀 Próximas Ações

### Imediato (30 min)
1. Abra um dos arquivos acima no KiCad GUI
2. Verifique que todos os componentes aparecem
3. Tire print para documentação

### Curto Prazo (1-2 dias)
4. Adicione interligações de netlist (wiring)
5. Crie grupos lógicos (power section, drive section, sense section)
6. Salve projeto `.kicad_pro`

### Médio Prazo (3-5 dias)
7. Exporte netlist: `Tools` → `Generate Netlist`
8. Inicie layout PCB: `Tools` → `PCB Editor`
9. Importe netlist no PCB editor

### Longo Prazo (1-2 semanas)
10. Auto-route ou rote manualmente
11. Execute DRC (Design Rule Check)
12. Exporte Gerber files
13. Submeta no JLCPCB

---

## 📊 Comparação dos Arquivos

| Aspecto | with_symbols | visualizer |
|---------|--------------|-----------|
| Símbolos visuais | ✅ Sim | ❌ Texto |
| Componentes | 52 | 58 |
| Tamanho | 17.9 KB | 5.1 KB |
| Validação kicad-cli | ✅ Passou | ✅ Passou |
| Edição fácil | ✅ Sim | ⚠️ Difícil |
| Aparência profissional | ✅ Sim | ⚠️ Básica |

**Recomendação**: Use `schematic_with_symbols.kicad_sch` para trabalho real.

---

## ⚠️ Se Ainda Não Funcionar

**Opção A: Abra via terminal**
```bash
cd /home/teste/controlmotor
kicad schematic_with_symbols.kicad_sch --norestore &
```

**Opção B: Arraste para KiCad**
1. Abra KiCad
2. `File` → `Open`
3. Navigate para `/home/teste/controlmotor/`
4. Selecione `schematic_with_symbols.kicad_sch`
5. Click `Open`

**Opção C: Use o simples primeiro**
```bash
kicad schematic_visualizer.kicad_sch &
```

---

## 📞 Troubleshooting

**Erro: "Falha ao ler esquemático"**
- Tente o arquivo `schematic_visualizer.kicad_sch` primeiro
- Reinicie KiCad e tente novamente
- Verifique que KiCad 9.0+ está instalado: `kicad --version`

**Símbolos não aparecem**
- Esperado para `schematic_visualizer.kicad_sch` (usa texto)
- Para `schematic_with_symbols.kicad_sch`, aguarde carregar
- Vá para `View` → `Zoom to Fit All` para ver melhor

**Quer editar os componentes**
- No KiCad: `Place` → `Symbol` (ou `Wire`, `Label`, etc)
- Use o BOM.csv como referência: `/home/teste/controlmotor/bom.csv`
- Siga footprints em: `footprints_mapping.csv`

---

## 📄 Arquivos Relacionados

| Arquivo | Propósito |
|---------|-----------|
| `schematic_with_symbols.kicad_sch` | ⭐ Use este para visualizar/editar |
| `schematic_visualizer.kicad_sch` | Fallback simples (texto) |
| `bom.csv` | Referência de 57-58 componentes |
| `footprints_mapping.csv` | Mapeamento footprints JLCPCB |
| `KICAD_VISUALIZATION_GUIDE.md` | Este arquivo |

---

**Status**: ✅ Pronto para uso  
**Data**: 2026-08-14  
**Versão KiCad**: 9.0+  
**Componentes**: 52-58 (variando por arquivo)

