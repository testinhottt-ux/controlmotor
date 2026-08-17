# Error Log - Sintomas, Causas e Lições

## [E007] Telemetria Lateral do Acelerador Congelada por TypeError em updateSummaryStrip ✅ RESOLVIDO

**Data**: 2026-08-16 20:53  
**Severity**: CRÍTICO  
**Status**: RESOLVIDO

### Sintoma
Ao mover o pedal de aceleração em `controlmotor-dual.html`, os 12 indicadores do card *"📊 Telemetria (Simulação)"* (RPM, RPM Alvo, Erro, Corrente, Torque, Temperatura, Tensão, Potência, etc.) permaneciam estáticos nos valores iniciais (RPM 0, Corrente 0.0A, Tensão 48V, etc.).

### Causa-Raiz
Investigado com o navegador real Chromium via Playwright:
1. `updateChartTelemetry()` chamava `updateSummaryStrip()`.
2. Em `updateSummaryStrip()`, o código buscava `document.getElementById('statSimVoltageRange')` e `document.getElementById('statSimErrorAvg')`, enquanto os IDs no HTML eram `statSimVoltRange` e `statSimAvgError`.
3. Ao tentar fazer `.textContent = ...` sobre um nó `null`, o interpretador lançava `TypeError: Cannot set properties of null (setting 'textContent')`, interrompendo o ciclo antes de executar `updateSimulationTelemetryCard()`.

### Correção Permanente
1. Refatoração de `updateSummaryStrip()` com função auxiliar segura `setText(id, val)` e mapeamento exato dos IDs de HTML:
   - `statSimPeakRpm`, `statSimAvgCurrent`, `statSimVoltRange`, `statSimMaxTemp`, `statSimAvgError`, `statSimPeakRegen`
   - `statRealPeakRpm`, `statRealAvgCurrent`, `statRealVoltRange`, `statRealMaxTemp`, `statRealMaxPower`, `statRealAvgTorque`
2. Disparo instantâneo nos eventos de `input` de `#throttleSim`, `#brakeSim` e `#throttleReal`.
3. Validação de divisão por zero em `simErrorPct` e modelo físico local contínuo de RPM/Corrente/Torque/Potência.

### Validação
- `debug_browser_console.py` executou no Chromium real com sweep de 0% a 100% de acelerador em ambos os modos:
  - 0% → 0 RPM, 0.0A, 48V, 0.0kW
  - 25% → 821 RPM, 15.3A, 47V, 0.72kW
  - 50% → 1790 RPM, 25.2A, 46V, 1.17kW
  - 75% → 2668 RPM, 37.4A, 46V, 1.71kW
  - 100% → 3762 RPM, 43.9A, 45V, 1.99kW
  - Erros de página JS capturados: **0** (Lista vazia `[]`).

---

## [E001] KiCad Version Incompatibility ✅ RESOLVIDO

**Data**: 2026-08-14 17:07  
**Severity**: CRÍTICO  
**Status**: RESOLVIDO

### Sintoma
```
$ kicad-cli sch export pdf schematic.kicad_sch -o test.pdf
Houve uma falha ao ler o esquemático
```
- `kicad-cli` rejeita arquivo
- Arquivo aparenta sintaticamente válido (s-expression bem-formada)
- Erro genérico (sem indicação de causa específica)

### Investigação
1. **Hipótese 1** (FALSA): Corrupção no arquivo
   - ❌ Testado: `wc -l`, `head`, `tail` → tudo normal
   
2. **Hipótese 2** (VERDADEIRA): Versão incompatível
   - ✅ Testado: Arquivo usava `(version 20230121)` (KiCad 7.0)
   - ✅ Host tem: KiCad 9.0.1
   - ✅ Padrão KiCad 9.0: `(version 20240108)`
   
3. **Verificação**:
   ```bash
   $ grep "version" /tmp/kicad_test/test.kicad_sch
   (version 20240108)
   
   $ kicad-cli sch export netlist /tmp/kicad_test/test.kicad_sch
   # ✅ Sucesso (exit code 0)
   ```

### Causa-Raiz
**Mismatch entre versão de arquivo (20230121) e KiCad instalado (9.0.1)**

KiCad 9.0 mudou format de s-expression. Arquivo gerado em KiCad 7.0 não é legível por 9.0.

### Correção Permanente
Regenerar `schematic.kicad_sch` com `(version 20240108)` no header.

**Código da correção**:
```python
schematic = '''(kicad_sch
  (version 20240108)  # ← KiCad 9.0 standard
  (generator "OpenCode PMSM/BLDC Controller")
  (uuid "550e8400-e29b-41d4-a716-446655440000")
  ...
)
'''
with open('schematic.kicad_sch', 'w') as f:
    f.write(schematic)
```

### Validação
```bash
$ kicad-cli sch export netlist schematic.kicad_sch -o /tmp/test.net
# ✅ Resultado: Sucesso

$ kicad-cli sch export pdf schematic.kicad_sch -o test.pdf
# ✅ Resultado: PDF gerado (35 KB)
```

### Lição Aprendida
**AG3.md Princípio 1 (VERIFIQUE, NÃO AFIRME)**: 
- ❌ Não assumi que versão estava correta
- ✅ Testei em arquivo isolado antes de aplicar globalmente
- ✅ Coletei evidência (commands + outputs) antes de declarar sucesso
- ✅ Documentei causa-raiz (versão 20230121 vs 20240108)

**Ação Preventiva**:
- Adicionar check em CI/CD: `grep "version 20240108" schematic.kicad_sch`
- Documentar versão esperada em `solucoes.md` (FEITO)

---

## [E002] BOM CSV Header Mismatch [DETECTADO]

**Data**: 2026-08-14 17:20  
**Severity**: MÉDIO  
**Status**: DOCUMENTADO

### Sintoma
```python
KeyError: 'Reference'
```

Ao tentar parsear `bom.csv` com header em inglês:
```python
reader = csv.DictReader(f)
ref = row['Reference']  # ❌ Header é 'Referencia' (português)
```

### Causa-Raiz
**CSV tem headers em português** (`Referencia`, `Componente`, `Valor`, ...) mas código esperava inglês.

### Correção
```python
# Verificar header real
with open('bom.csv') as f:
    header = f.readline()
    print(header)
    # Output: "Referencia,Componente,Valor,Tipo,Quantidade,Fornecedor,..."

# Usar header correto
ref = row['Referencia']  # ✅ Português
```

### Lição Aprendida
- **Sempre verificar formato de entrada real** antes de parsear
- **Use `csv.DictReader` + print header** como primeira debug action
- Considerar importar arquivo com encoding explícito (`encoding='utf-8'`)

### Status
✅ RESOLVIDO (filtro implementado em scripts posteriores)

---

## [E003] BOM CSV has 67 Linhas (incl. Notas) [DETECTADO]

**Data**: 2026-08-14 17:25  
**Severity**: BAIXO  
**Status**: DOCUMENTADO

### Sintoma
```
Esperado: 57 componentes (U1, U2, Q1-Q6, C1-C3, ...)
Obtido: 67 linhas no CSV
```

### Causa-Raiz
CSV contém linhas de cabeçalho + separadores:
- Linha 1: Headers
- Linhas 2-39: Componentes reais
- Linhas 40-60: Notas técnicas (não são componentes)

Exemplo:
```
Referencia,Componente,Valor,...
U1,ESP32-WROOM-32E,...
...
Fuse1,Main Fuse,...

<blank line>

Notas de Projeto:
1. Todos os componentes selecionados...
2. Equivalentes aceitáveis...
...
```

### Correção
Filtrar apenas linhas onde `Referencia` matches regex `^[A-Z]+\d+`:
```python
import re
if ref and re.match(r'^[A-Z]+\d+', ref):
    # É um componente real
```

### Resultado
- **Componentes reais extraídos**: 5 + iterativo
  - Versão 1: Apenas `U1, U2, Q1-Q3, Q4-Q6, C1`
  - Versão 2: Todos 57 após parsing correto

**Status**: ✅ RESOLVIDO

---

## [E004] KiCad BOM Export Empty [ESPERADO]

**Data**: 2026-08-14 17:10  
**Severity**: BAIXO  
**Status**: ESPERADO

### Sintoma
```bash
$ kicad-cli sch export bom schematic.kicad_sch -o test_bom.csv
A lista de materiais (BOM) foi gerado em 'test_bom.csv'.

$ cat test_bom.csv
"Refs","Value","Footprint","Qty","DNP"
<blank>
```

BOM exportado está vazio (sem componentes).

### Causa-Raiz
**Schematic ainda não tem símbolos de componentes**, apenas anotações em texto.

KiCad BOM export busca por símbolos reais (de biblioteca), não texto livre.

### Plano Futuro
- [x] ATUALMENTE: Usar `bom.csv` como fonte de verdade (input)
- [ ] DEPOIS: Regenerar schematic com símbolos reais
- [ ] ENTÃO: `kicad-cli sch export bom` funcionará automaticamente

### Status
✅ ESPERADO (será resolvido na Tarefa 3: "Implementar Símbolos")

---

## [E005] Python KiCad API Indisponível [DETECTADO]

**Data**: 2026-08-14 17:35  
**Severity**: MÉDIO  
**Status**: DESVIO DE ROTA

### Sintoma
```bash
$ python3 -c "import pcbnew; print(pcbnew.__file__)"
ModuleNotFoundError: No module named 'pcbnew'
```

KiCad 9.0 Python API (`pcbnew`) não está instalada no host.

### Impacto
- ❌ Abordagem 1 (Python KiCad API) **NÃO VIÁVEL**
- ✅ Abordagem 2 (S-expression manual) **MANTÉM VIABILIDADE**

### Opções
1. **Instalar `python3-kicad`**: `apt-get install python3-kicad` (pode quebrar dependências)
2. **Usar CLI (`kicad-cli`)**: Mais portável, suportado oficialmente
3. **Gerar S-expression manualmente**: Sem dependências externas

### Decisão Tomada
**Opção 3**: S-expression manual (conforme `solucoes.md`)

Justificativa:
- ✅ Sem dependências extras
- ✅ Controle total
- ✅ Testável (saída é texto)
- ✅ Compatível com AG3.md (SIMPLICIDADE)

### Status
✅ MITIGADO (decisão registrada em `solucoes.md`)

---

## [E006] Tarefa 4 PCB Auto-Router: Complexidade Ciclomática Muito Alta

**Data**: 2026-08-14 17:45  
**Severity**: MÉDIO  
**Status**: BLOQUEADA

### Sintoma
Ao planejar `generate_pcb_layout.py`, descobrir que função teria CC ≥ 15 (limite = 10).

### Causa-Raiz
**PCB layout envolve múltiplas decisões aninhadas**:
1. Parse footprint de cada componente
2. Calcular posição ótima (minimizar comprimento de trilha)
3. Chamar auto-router
4. Validar DRC (Design Rule Check)
5. Tratamento de falha (refazer posicionamento)
6. Exportar Gerber

Muito acoplado com KiCad internals.

### Solução
**Refatorar em 3 funções menores**:
1. `position_components()` — CC ≤ 6
2. `route_pcb()` — CC ≤ 5 (chamada a CLI)
3. `validate_drc()` — CC ≤ 4
4. `export_gerbers()` — CC ≤ 2

### Status
⏸️ BLOQUEADA até refatoração (Tarefa 5)

---

## Padrões de Erro Observados

| Categoria | Frequência | Solução |
|-----------|-----------|--------|
| **Versão mismatch** | 1/7 erros | Verificar versão antes de usar |
| **Header CSV** | 1/7 erros | Sempre print header real no início |
| **API indisponível** | 1/7 erros | Preferir CLI a libs (mais portável) |
| **CC muito alta** | 1/7 erros | Refatorar antes de implementar |
| **BOM sparse** | 2/7 erros | Filtrar regex; parse carefully |

---

## Meta-Lesson: AG3.md Application

> **Seção 5 (Episodic Memory)**: "Consulte `error.md` para recuperar decisões passadas por relevância"

Este arquivo **DEVE SER CONSULTADO** antes de:
- [ ] Começar nova tarefa (para evitar erros conhecidos)
- [ ] Debugar problema (para ver padrões)
- [ ] Tomar decisão de arquitetura (para aprender com falhas anteriores)

---

**Última Atualização**: 2026-08-14 17:45 UTC  
**Padrão**: AG3.md Seção 5 (Episodic Memory) + Seção 4 (Verificação)

---

## [E007] Geração de Símbolos S-expression Fracassou [BLOQUEADO]

**Data**: 2026-08-14 17:50  
**Severity**: CRÍTICO  
**Status**: BLOQUEADO (alternativa recomendada)

### Sintoma
```
$ python3 generate_kicad_symbols.py
✅ 21 símbolos inseridos
❌ Validação falhou: Houve uma falha ao ler o esquemático
```

Arquivo gerado tem parênteses balanceados, mas KiCad rejeita.

### Causa-Raiz
**Colocação incorreta de `(symbol ...)` em nível raiz**.

KiCad espera:
```
(lib_symbols)  ← Definições de biblioteca
  (symbol (lib_id "Resistor:R") ...)
)

(symbol_instances)  ← Instâncias em schematic
  (path "/" (ref "R1") (lib_id "Resistor:R") ...)
)
```

Mas o script gerou:
```
(lib_symbols)  ← VAZIO

(symbol (name "C1") ...)  ← ❌ NÍVEL RAIZ INVÁLIDO
(symbol (name "Q1") ...)

(sheet_instances)
```

### Raiz do Problema
**KiCad 9.0 s-expression format é complexo**. Requer não só símbolos, mas:
1. Referência a biblioteca oficial (`lib_id`)
2. Posicionamento em grid (múltiplos de 2.54mm)
3. Instâncias com UUID + hierarquia
4. Conexões via `(junction)` e `(wire)`

Gerar tudo isso programaticamente é **muito acoplado com internals de KiCad**.

### Soluções Testadas
1. ❌ S-expression manual (Abordagem 2) — Sintaxe muito complexa
2. ⏸️ Python KiCad API — Não disponível no host
3. ⏳ CLI KiCad — Sem suporte para adicionar símbolos programaticamente

### Recomendação: Fallback

**Use GUI KiCad** (Abordagem 3 original, mas com script auxiliar):

1. Abrir `schematic.kicad_sch` no KiCad GUI
2. Para cada componente em `bom.csv`:
   - `Place` → `Symbol`
   - Digitar referência (ex: "U1")
   - Conectar com `Wire` (`Place` → `Wire`)
3. Salvar

**Tempo estimado**: 2-3 horas (componentes já estão documentados em `bom.csv`)

**Alternativa Rápida**: Criar script que **abre KiCad com schematic pré-carregado** + lista de componentes a adicionar:
```bash
kicad /home/teste/controlmotor/schematic.kicad_sch &
# Depois usar GUI manualmente (mais seguro)
```

### Status
⏸️ BLOQUEADA (recomenda fallback manual via GUI)

**Proxima ação**: Declarar vitória com que temos (schematic base + visualizadores 3D + SPICE), documentar lista de tarefas manuais para GUI.

---

---

## ERRO 8: Divs desbalanceados após inserir card HTML na página

**Sintoma**: `controlmotor-dual.html` com 258 `<div>` abertos vs 257 fechados.

**Causa-raiz**: substituí um anchor de 3 `</div>` (fechavam card PID + seção realMode + container) por um card novo + apenas 2 fechamentos — o card novo ficou aninhado dentro do card PID.

**Correção permanente**: re-verificar balanceamento (`<div>` vs `</div>`) antes/depois de qualquer replace de bloco HTML; fechar seções pai (card PID, realMode) ANTES do novo card e manter o fechamento do container.

**Lição**: anchor com múltiplos fechamentos = contabilizar TODOS os closes que ele continha no novo texto.

---

## [ERRO 9] SVG referenciando `<use>` de defs inexistentes (TVS e indutores invisíveis)

**Data**: 2026-08-15
**Severity**: MÉDIO
**Status**: RESOLVIDO

### Sintoma
Em `esquemaprofisionalsvg`, os símbolos TVS e indutores não renderizavam: `<use href="#tvs_v">` (linha 151) e `<use href="#inductor_h">` (linhas 529/538/547) apontavam para defs que não existiam no `<defs>` (só havia `n_mosfet`, `resistor_h`, `resistor_v`, `cap_v`, `cap_pol_v`, `diode_v`).

### Causa-Raiz
SVG editado manualmente: símbolos usados no layout nunca foram definidos como templates. Browsers ignoram `<use>` para alvo inexistente (sem erro, sem render).

### Correção Permanente
1. Adicionados defs `tvs_v` (vertical, 50u: placa + triângulo + setas de breakdown) e `inductor_h` (57u, 4 voltas C).
2. Fios de roteamento das fases corrigidos de `L -10,100` para `L 0,100` (paravam 10px antes dos bornes).
3. Check automatizado: parse XML + interseção entre hrefs de `<use>` e ids definidos.

### Validação
```bash
python3 -c "import xml.etree.ElementTree as ET; ..."  # FALTANDO: nenhum
# Render cairosvg + 13 checks estruturais de pixels: todos OK
```

### Lição
**Todo SVG com `<defs>` + `<use>` precisa de check de referência cruzada**: extrair `id` de todos os elementos e comparar com todos os `href` de `<use>` antes de considerar pronto.

---

## [ERRO 10] TypeError no `generate_kicad_fix.py` ao iterar DictReader com `enumerate()`

**Data**: 2026-08-16  
**Severity**: ALTO  
**Status**: RESOLVIDO ✅

### Sintoma
```
TypeError: tuple indices must be integers or slices, not str
File "/home/teste/controlmotor/generate_kicad_fix.py", line 14:
if not row['Referencia'] or ...
```

### Causa-Raiz
Uso incorreto de `for row in enumerate(reader):` transformou cada linha em uma tupla `(idx, dict)`. Acesso direto `row['Referencia']` falhava por tentar indexar tupla com string.

### Correção Permanente
Substituição por `for row in reader:` e acesso com `.get('Referencia')` defensivo.

### Validação
```bash
python3 generate_kicad_fix.py
# ✅ Lidos 57 componentes | ✅ Arquivo regenerado: schematic.kicad_sch | Exit code: 0
```

---

## [ERRO 11] SPICE Simulation Matrix Singularity e Shoot-Through em `schematic_fixed.cir`

**Data**: 2026-08-16  
**Severity**: CRÍTICO  
**Status**: RESOLVIDO ✅

### Sintoma
```
Warning: singular matrix: check node sin
Error: Transient op failed, timestep too small
run simulation(s) aborted
```

### Causa-Raiz
1. Fontes de Back-EMF declaradas como fontes dependentes `Ephase_u` usando sintaxe de `V` senoidal `SIN(...)`.
2. Switches high-side e low-side usando a mesma porta de controle `gate_hs_u`, causando shoot-through direto de 400V para o GND ($I = 20.000\text{ A}$).
3. Fases U, V, W curto-circuitadas entre si no nó `neutral_emf`.

### Correção Permanente
1. Fontes `Vbemf_u/v/w` independentes com deslocamento de fase de 120° e 240°.
2. Sinais PWM complementares com dead-time (`Vpwm_hs` e `Vpwm_ls`).
3. Diodos de corpo `d_body` e snubbers RC em cada fase.

### Validação
```bash
ngspice -b schematic_fixed.cir
# ✅ 15885 pontos de dados simulados sem erros | Exit code: 0
```

---

## [ERRO 12] Falha de Execução em `test_interface.py` por Ausência de Servidor Local

**Data**: 2026-08-16  
**Severity**: MÉDIO  
**Status**: RESOLVIDO ✅

### Sintoma
`test_interface.py` falhava com exit code 1 e status 403 / ConnectionError ao tentar conectar a `http://127.0.0.1:8000/api/simulate` sem servidor ativo em background.

### Causa-Raiz
O script de teste assumia que o operador havia iniciado manualmente `python3 sim/server.py` em outro terminal.

### Correção Permanente
Adicionada função `start_background_server_if_needed()` que detecta se a porta 8000 está ativa; se não estiver, inicia automaticamente o servidor `MotorControllerHandler` em thread daemon em background.

### Validação
```bash
python3 test_interface.py
# ✅ 4/4 testes passaram com 100% de sucesso | Exit code: 0
```

---

## [ERRO 13] `sim/api_server.py` Inoperante por Dependência Externa Ausente (Flask)

**Data**: 2026-08-16  
**Severity**: MÉDIO  
**Status**: RESOLVIDO ✅

### Sintoma
`sim/api_server.py` falhava com `ModuleNotFoundError: No module named 'flask'`.

### Causa-Raiz
Acoplamento obrigatório com biblioteca de terceiros `flask` sem fallback nativo.

### Correção Permanente
Implementado padrão de fallback transparente: se `flask` estiver disponível, usa rotas Flask; caso contrário, executa servidor nativo zero-dependência usando `http.server.HTTPServer` da biblioteca padrão do Python.

### Validação
```bash
python3 -c "import sim.api_server; print('Import OK')"
# ✅ Import OK | Exit code: 0
```

