# Flow - Arquitetura de Dados e Dependências

## Estrutura de Arquivo (Projeto Controlador PMSM/BLDC)

```
/home/teste/controlmotor/
├── bom.csv                              # BOM master (67 linhas: 57 componentes + notas)
├── schematic.kicad_sch                  # Schematic KiCad 9.0 (base)
├── controlador_motor.kicad_pro          # Projeto KiCad (binds schematic)
├── layout.kicad_pcb                     # Layout PCB (TBD)
├── schematic_fixed.cir                  # SPICE netlist (validado)
├── ag3.md                               # Sistema de operação (governance)
├── progresso.md                         # Fila de tarefas (THIS FILE)
├── flow.md                              # Arquitetura + dependências (THIS FILE)
├── solucoes.md                          # Decisões de design (TBD)
├── error.md                             # Log de erros e lições (TBD)
├── SOLUCAO_KICAD9.md                    # Correção de versão (concluído)
├── INDICE_VISUALIZACOES.html            # Hub de visualizadores
├── esquematico_interativo.html          # Schematic web interativo
├── visualizador_3d_awwwards.html        # 3D PCB com 58 componentes
├── visualizador_3d_premium.html         # 3D alternativo
├── visualizador_3d_completo.html        # 3D básico
├── schematic_kicad9.pdf                 # Schematic PDF (35 KB)
├── simulation_results.{png,pdf,svg}     # Gráficos SPICE (9-panel)
└── gerbers/                             # Saída Gerber (TBD)
    ├── layout-F.Cu.gbr
    ├── layout-B.Cu.gbr
    ├── layout-F.Mask.gbr
    ├── layout-B.Mask.gbr
    └── ...
```

---

## Fluxo de Dados (V0 → V1)

### Pipeline de Entrada
```
bom.csv (57 componentes)
    ↓
[Python: parse_bom()]
    ↓
Dict{ref → {valor, componente, footprint}}
    ↓
[Gerar schematic symbols]
    ↓
schematic.kicad_sch (v20240108)
```

### Exportação Schematic
```
schematic.kicad_sch
    ↓ [kicad-cli sch export pdf]
    ↓ [kicad-cli sch export netlist]
    ↓
schematic_kicad9.pdf (35 KB)
netlist.txt (SPICE source)
```

### Pipeline PCB
```
schematic.kicad_sch
    ↓ [KiCad Netlist extraction]
    ↓
Conexões: (U1.VCC → C1.+), (Q1.Gate → RG1.1), etc.
    ↓ [Footprint mapping]
    ↓
layout.kicad_pcb (150×100mm, 4-layer)
    ↓ [Auto-router]
    ↓
Trilhas roteadas (50mm max length)
    ↓ [kicad-cli pcb export gerbers]
    ↓
gerbers/*.gbr (10+ files)
```

### Pipeline SPICE
```
schematic.kicad_sch
    ↓ [netlist_to_spice.py]
    ↓
schematic_fixed.cir (SPICE netlist)
    ↓ [ngspice]
    ↓
sim_output.txt (9 variables × 5000 timesteps)
    ↓ [matplotlib]
    ↓
simulation_results.{png,pdf,svg}
```

### Pipeline 3D Visualization
```
bom.csv (57 reais)
    ↓ [generate_3d_visualizer.py]
    ↓
visualizador_3d_awwwards.html (58 componentes 3D)
    ↓ [Three.js + WebGL]
    ↓
Interactive 3D PCB (navegável em navegador)
```

---

## Dependências Críticas (File → File)

| Origem | Destino | Tipo | Descrição |
|--------|---------|------|-----------|
| `bom.csv` | `schematic.kicad_sch` | Input | Componentes → Símbolos |
| `bom.csv` | `visualizador_3d_awwwards.html` | Input | 58 componentes renderizados |
| `schematic.kicad_sch` | `layout.kicad_pcb` | Source | Netlist extração |
| `schematic.kicad_sch` | `schematic_kicad9.pdf` | Export | PDF via kicad-cli |
| `schematic.kicad_sch` | `schematic_fixed.cir` | Convert | SPICE netlist |
| `schematic_fixed.cir` | `simulation_results.png` | Simulate | Ngspice → Matplotlib |
| `layout.kicad_pcb` | `gerbers/*.gbr` | Export | Gerber files |
| `controlador_motor.kicad_pro` | `schematic.kicad_sch` | Bind | Project wrapper |

---

## Funções-Chave e Localização

### Script: `bom_parser.py` (TBD)
```python
def parse_bom(filepath: str) -> Dict[str, ComponentInfo]:
    """Parse bom.csv em dicionário estruturado"""
    # Entrada: bom.csv (67 linhas)
    # Saída: Dict{U1 → {componente, valor, footprint}}
    # Complexidade: O(n), n=57
    # CC: 3 (linear)
```

**Chamada em**:
- `generate_kicad_schematic.py` — Para integrar símbolos
- `visualizador_3d_awwwards.html` — Para renderizar componentes
- `generate_bom_report.py` — Para BOM JLCPCB

---

### Script: `generate_kicad_schematic.py` (ATIVO)
```python
def generate_schematic(bom_dict, output_path):
    """Gera schematic.kicad_sch com 57 componentes"""
    # Entrada: bom_dict (Dict)
    # Saída: schematic.kicad_sch (1.2 KB)
    # Dependências: bom_parser.parse_bom()
    # CC: 8 (loops aninhados: componentes → símbolos → conexões)
```

**Variação futura**:
- Versão V2: Adicionar `footprints` ao s-expression
- Versão V3: Gerar `netlist` com interligações

---

### Script: `netlist_to_spice.py` (ATIVO)
```python
def convert_netlist_to_spice(netlist_txt, output_cir):
    """Converte netlist KiCad → SPICE .cir"""
    # Entrada: netlist.txt (KiCad format)
    # Saída: schematic_fixed.cir (3KB)
    # CC: 6 (pattern matching + regex)
```

---

### Script: `generate_3d_visualizer.py` (ATIVO)
```python
def create_3d_html(bom_csv, output_html):
    """Gera HTML 3D interativo com 58 componentes"""
    # Entrada: bom.csv
    # Saída: visualizador_3d_awwwards.html (20 KB)
    # Dependências: Three.js (CDN), Webgl
    # CC: 10 (parsing + 3D geometry + interactivity)
```

---

### Script: `generate_pcb_layout.py` (TBD)
```python
def auto_route_pcb(schematic_path, bom_dict, output_pcb):
    """Gera layout.kicad_pcb com roteamento automático"""
    # Entrada: schematic.kicad_sch + bom.csv
    # Saída: layout.kicad_pcb (150×100mm)
    # Dependências: KiCad Python API (pcbnew module)
    # CC: 15+ (footprint placement + routing)
    # ⚠️ ALTO acoplamento com KiCad internals
```

---

### Script: `export_gerbers.py` (TBD)
```bash
def export_gerbers(layout_pcb, output_dir):
    """Exporta Gerber files via kicad-cli"""
    # Entrada: layout.kicad_pcb
    # Saída: gerbers/*.gbr (10+ files)
    # CLI: kicad-cli pcb export gerbers layout.kicad_pcb -o gerbers/
    # CC: 2 (trivial subprocess wrapper)
```

---

## Complexidade Ciclomática (MDCA-A Eixo 8)

| Script | CC | Status | Limite |
|--------|----|---------|----|
| `bom_parser.py` | 3 | ✅ OK | ≤ 10 |
| `generate_kicad_schematic.py` | 8 | ✅ OK | ≤ 10 |
| `netlist_to_spice.py` | 6 | ✅ OK | ≤ 10 |
| `generate_3d_visualizer.py` | 10 | ⚠️ EDGE | ≤ 10 |
| `generate_pcb_layout.py` | 15+ | ❌ ALTO | ≤ 10 |
| `export_gerbers.py` | 2 | ✅ OK | ≤ 10 |

**Ação Necessária**: `generate_pcb_layout.py` requer refatoração em 2-3 funções menores antes de implementação.

---

## Invariantes e Contratos

### Invariante 1: BOM Integrity
```
SEMPRE: len(bom_dict) ≥ 57
SEMPRE: All refs in schematic.kicad_sch ∈ bom_dict.keys()
SEMPRE: All footprints in layout.kicad_pcb ∈ valid_kicad_footprints
```

### Invariante 2: Netlist Connectivity
```
SEMPRE: Cada nó em netlist tem ≥1 conexão (sem componentes flutuantes)
SEMPRE: Não há loops de potência curtos (VCC → GND diretos)
SEMPRE: Tensões de operação respeitam:
  - U1 (ESP32): 3.0-3.6V
  - U2 (DRV8302): 6-50V
  - Q1-Q6 (MOSFETs): até 600V gate
  - Capacitores: rated voltage > 400V DC + 20% margem
```

### Invariante 3: PCB Physical Constraints
```
SEMPRE: Trilhas críticas (Fases U/V/W) ≤ 50mm
SEMPRE: Via térmicas sob MOSFETs ≥ 200 unidades
SEMPRE: Clearance ≥ 0.2mm (JLCPCB padrão)
SEMPRE: Espessura de trilha ≥ 10mil (0.254mm) para correntes >10A
```

---

## Prioridade de Execução (Dependências Topológicas)

1. **BOM parsing** ← Prerequisito para tudo
2. **Schematic symbols** ← Entra em netlist
3. **Netlist generation** ← Entra em PCB + SPICE
4. **SPICE simulation** ← Paralelo (não bloqueia PCB)
5. **Footprint mapping** ← Serial (depois de netlist)
6. **PCB auto-routing** ← Serial (depois de footprints)
7. **Gerber export** ← Final (depois de PCB)

**Grafo de Dependências**:
```
bom.csv
    ├─→ schematic generation
    │       └─→ netlist extraction
    │           ├─→ SPICE conversion
    │           │   └─→ simulation
    │           └─→ PCB layout (footprints)
    │               └─→ auto-routing
    │                   └─→ gerber export
    └─→ 3D visualization (paralelo)
```

---

## Versioning

| Arquivo | Versão | Atualizado | Nota |
|---------|--------|-----------|------|
| `schematic.kicad_sch` | 20240108 | 2026-08-14 | KiCad 9.0 compatível |
| `bom.csv` | 1.0 | 2026-08-14 | 57 componentes reais |
| `layout.kicad_pcb` | TBD | — | Ainda não existe |
| `solucoes.md` | TBD | — | Ainda não existe |

---

**Última Atualização**: 2026-08-14 17:15 UTC  
**Manutenedor**: OpenCode AG3  
**Padrão**: AG3.md Seção 11

## Arquivo: controlmotor-dual.html (atualização 2026-08-15)

### Mudança
- Card "Esquema Elétrico do Controlador" com SVG inline (esquema.svg, 624 linhas) inserido fora das seções de modo — sempre visível.
- Sem mudanças de funções JS; JS validado com `node --check` (43462 chars).

### Dependências
- `esquema.svg` (embutido inline — sem dependência externa em runtime).
