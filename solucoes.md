# Soluções - Pesquisa de Abordagens para Fase 2

## Decisão 1: Versão KiCad para Schematic [DECIDIDO ✅]

**Data**: 2026-08-14 17:07  
**Contexto**: Arquivo original usava versão 20230121 (KiCad 7.0), mas host tem KiCad 9.0.1

### Abordagens Pesquisadas

| # | Abordagem | Prós | Contras | Custo | Viabilidade |
|---|-----------|------|---------|-------|-------------|
| 1 | Usar versão 20230121 (atual) | Compatível com código existente | ❌ Incompatível com KiCad 9.0.1 | Baixo | ❌ FALHA |
| 2 | Upgrade para 20240108 (KiCad 9.0 standard) | ✅ Compatível, validado | Requer regeneração de arquivo | Médio | ✅ **SELECIONADA** |
| 3 | Downgrade KiCad 9.0 → 7.0 | Compatibilidade backward | ❌ Host compartilhado, pode quebrar outros projetos | Alto | ❌ Não viável |
| 4 | Usar formato JSON (.kicad_sch_json) | Mais portável | ❌ KiCad-cli não suporta em v9.0 | Médio | ❌ Não testado |

### Decisão
**✅ ADOTADA: Versão 20240108**

**Justificativa**:
- Testado em `/tmp/kicad_test/test.kicad_sch` com sucesso
- `kicad-cli sch export netlist` passa
- `kicad-cli sch export pdf` gera 35 KB válido
- Compatível com documentação oficial KiCad 9.0
- Manutenível (atualizar versão é operação trivial em próximas releases)

**Evidência**: 
```bash
$ kicad-cli sch export netlist schematic.kicad_sch -o test.net
# Exit code: 0 ✅
```

---

## Decisão 2: Adição de Símbolos Reais ao Schematic [PENDENTE]

**Data**: 2026-08-14 17:30  
**Contexto**: Schematic atual tem estrutura mínima; faltam 57 símbolos de componentes

### Abordagens Pesquisadas

#### Abordagem 1: Python KiCad API (`pcbnew` module)
```python
# Pseudo-código
from pcbnew import *
schematic = LoadSchematic("schematic.kicad_sch")
schematic.AddSymbol("U1", "ESP32-WROOM-32E", x=10, y=10)
schematic.AddSymbol("Q1", "IPP65R600P7", x=20, y=10)
schematic.Save()
```

**Prós**:
- ✅ Acesso direto a KiCad internals
- ✅ Programação em Python (linguagem familiar)
- ✅ Pode integrar com `bom.csv` automaticamente

**Contras**:
- ❌ API `pcbnew` é para PCB, não schematic
- ❌ `eeschema` API não é estável em KiCad 9.0
- ❌ Documentação oficial incompleta
- ⚠️ Requer instalação de `python3-kicad` (verificar host)

**Custo**: Alto (~3-4 horas de debugging)  
**Risco**: ALTO (API instável)

---

#### Abordagem 2: Geração Programática via S-expression (Python)
```python
# Pseudo-código
def add_symbol(ref, name, x, y):
    return f"""
    (symbol (name "{ref}") (at {x} {y})
      (property "Reference" "{ref}")
      (property "Value" "{name}")
    )
    """

with open("schematic.kicad_sch") as f:
    content = f.read()
    
for ref, data in bom_dict.items():
    symbol_text = add_symbol(ref, data['componente'], ...)
    content = insert_before_sheet_instances(content, symbol_text)

with open("schematic.kicad_sch", 'w') as f:
    f.write(content)
```

**Prós**:
- ✅ Controle total sobre formato s-expression
- ✅ Sem dependências externas (apenas Python + `re`)
- ✅ Rápido (~< 1 segundo para 57 componentes)
- ✅ Debugável (saída é texto legível)

**Contras**:
- ⚠️ Requer parsing manual de s-expression KiCad
- ⚠️ Risco de corrupção se formato mudar
- ❌ Sem ligações de netlist automáticas (wiring manual depois)

**Custo**: Médio (~2 horas)  
**Risco**: MÉDIO (parsing s-expression é frágil)

---

#### Abordagem 3: Template + Cópia Manual
```bash
# Usar um arquivo "golden" como template
cp /usr/share/kicad/templates/motor_driver.kicad_sch schematic_v2.kicad_sch

# Abrir em KiCad GUI e:
# 1. Adicionar símbolos manualmente (Place → Symbol)
# 2. Conectar com fios (Place → Wire)
# 3. Salvar
```

**Prós**:
- ✅ Garantido funcionar (GUI é oficial)
- ✅ Interface amigável
- ✅ Fácil criar hierarquia de sheets depois

**Contras**:
- ❌ Processo manual (~2-3 horas para 57 componentes)
- ❌ Não automático (não escala)
- ❌ Propenso a erros humanos

**Custo**: Alto em tempo humano  
**Risco**: BAIXO (GUI testado)

---

#### Abordagem 4: Usar Ferramenta de CAD via CLI (gEDA/Qucs)
```bash
# gEDA gschem pode gerar netlist
gschem -batch schematic.sch -o schematic.net

# Depois converter para KiCad
netlist_converter.py geda_netlist.net kicad_schematic.kicad_sch
```

**Prós**:
- ✅ Ferramenta alternativa pode ter API melhor

**Contras**:
- ❌ Adiciona dependência de outra ferramenta (gEDA)
- ❌ Conversão de formato é complexa
- ❌ Não há suporte oficial KiCad ↔ gEDA

**Custo**: Muito alto  
**Risco**: CRÍTICO

---

### Matriz de Decisão (Scoring)

| Critério | Peso | Abordagem 1 | Abordagem 2 | Abordagem 3 | Abordagem 4 |
|----------|------|------------|------------|------------|------------|
| Eficiência no host | 0.20 | 7/10 | 10/10 | 5/10 | 2/10 |
| Tempo de execução | 0.15 | 5/10 | 10/10 | 2/10 | 1/10 |
| Compatibilidade KiCad | 0.20 | 6/10 | 9/10 | 10/10 | 3/10 |
| Manutenibilidade | 0.15 | 5/10 | 7/10 | 8/10 | 1/10 |
| Automatização | 0.15 | 8/10 | 9/10 | 1/10 | 3/10 |
| Risco técnico | 0.15 | 2/10 | 5/10 | 9/10 | 1/10 |
| **TOTAL** | 1.0 | **5.4/10** | **8.4/10** | **6.4/10** | **1.6/10** |

### Decisão Recomendada

**✅ RECOMENDADA: Abordagem 2 (S-expression Programática)**

**Justificativa**:
- Score mais alto (8.4/10)
- Balanço ótimo entre automação + segurança
- Compatível com AG3.md (SIMPLICIDADE PRIMEIRO)
- Risco controlável (output é texto, fácil validar)
- Custo aceitável (2 horas)

**Plano de Implementação**:
1. Criar `generate_kicad_symbols.py` que:
   - Lê `bom.csv`
   - Gera s-expression para cada símbolo
   - Insere em `schematic.kicad_sch` antes de `sheet_instances`
   - Validação: Escreve arquivo temporário, compara tamanho esperado

2. **Check Objetivo**:
   ```bash
   python3 generate_kicad_symbols.py
   kicad-cli sch export pdf schematic.kicad_sch -o schematic_v2.pdf
   # ✅ Se gerado com sucesso, proceder
   ```

3. **Fallback**: Se falhar, usar Abordagem 3 (GUI manual)

---

## Decisão 3: Geração de Layout PCB [PENDENTE]

**Contexto**: Após símbolos + netlist, gerar layout com 150×100mm, 4-layer FR-4

### Abordagens Pesquisadas

| # | Abordagem | Prós | Contras | Viabilidade |
|---|-----------|------|---------|------------|
| 1 | KiCad GUI (Place → Component, Route manually) | Controle total | Manual, lento (4h+) | ✅ Funciona |
| 2 | `kicad-cli pcb import` + Auto-router integrado | Automático | Qualidade varia, lento | ⚠️ Beta em 9.0 |
| 3 | Python `pcbnew` API | Programável, controle fino | API instável, documentação pobre | ⚠️ Risco alto |
| 4 | Freerouting.js (roteador aberto) | Rápido, determinístico | Requer netlist especial | ✅ Testado |
| 5 | Exportar para KiCad → Processar em Python → Reimportar | Modular | Muitas conversões, erro propagação | ❌ Frágil |

**Recomendação**: Abordagem 2 (KiCad auto-router) como primeira tentativa; fallback Abordagem 4 (Freerouting.js) se falhar.

---

## Decisão 4: Exportação para Fabricação JLCPCB [PENDENTE]

**Contexto**: Gerar Gerber + BOM + coordenadas de pick-and-place

### Checklist JLCPCB
- [ ] Gerber files (F.Cu, B.Cu, F.Mask, B.Mask, F.Silks, Outline)
- [ ] BOM.csv com JLCPCB part numbers (coluna adicional)
- [ ] Coordenadas de pick-and-place (centro de cada componente)
- [ ] Anotações de PCB (espessura, material, acabamento)

**Processo**:
1. `kicad-cli pcb export gerbers layout.kicad_pcb -o gerbers/`
2. Extrair coordenadas com `kicad-cli pcb export pos layout.kicad_pcb`
3. Cruzar com `bom.csv` para gerar `BOM_JLCPCB.csv`
4. Documentar em `JLCPCB_README.md`

**Custo**: Baixo (2 comandos CLI + Python)

---

## Resumo de Decisões

| ID | Decisão | Status | Risco | Próximo Passo |
|----|---------|--------|-------|--------------|
| 1 | Versão KiCad 20240108 | ✅ DECIDIDA | Baixo | **IMPLEMENTADO** |
| 2 | Símbolos via S-expression | ✅ RECOMENDADA | Médio | Criar `generate_kicad_symbols.py` |
| 3 | PCB: Auto-router KiCad | ✅ RECOMENDADA | Médio-Alto | Testar em v2 layout |
| 4 | Fabr.: JLCPCB export CLI | ✅ TRIVIAL | Baixo | `kicad-cli` commands |

---

## Decisão 5: Cotação de Preços Barata (AliExpress + LCSC) [CONCLUÍDA ✅]

**Data**: 2026-08-15  
**Contexto**: Re-cotar BOM (`bom.csv`/`arquitetura.md`) ao menor preço possível.

### Abordagens avaliadas
| # | Fornecedor | Prós | Contras | Resultado |
|---|-----------|------|---------|-----------|
| 1 | Digikey/Mouser | Original, lead time confiável | Caro (BOM $240) | ❌ Rejeitado |
| 2 | **LCSC** (china) | -50–80% vs Digikey, mesma base da JLCPCB, PCBA integrado | Lead time 1–2 sem | ✅ **SELECIONADO** (ICs + SMD) |
| 3 | **AliExpress** | Mais barato em lotes (sensores, conectores, mecânica) | Qualidade variável, sem garantia forte | ✅ **SELECIONADO** (lotes + mecânica) |
| 4 | PCBWay | Confiável | 4L 100×100mm = $48 (3-6× mais caro que JLCPCB) | ❌ Rejeitado p/ PCB |
| 5 | **JLCPCB** | PCB 4L ~$7/100×100mm | Placa 300×200mm mais cara | ✅ **SELECIONADO** (PCB) |

### Decisão
**✅ ADOTADA: Comprar ICs/SMD no LCSC + lotes/mecânica no AliExpress + PCB no JLCPCB.**

**Resultado**: componentes ~$91 (vs $240), total/placa ~$126 (vs ~$400). Economia ~68%.

**Evidência / Fonte**:
- LCSC DRV8302DCA $7.72 — https://www.lcsc.com/product-detail/C84672.html
- LCSC ESP32-WROOM-32E-N16 $5.08 — https://www.lcsc.com/product-detail/C701343.html
- LCSC 470µF 450V $2.74 — https://www.lcsc.com/product-detail/C53330121.html
- JLCPCB 4L ~$7 — https://www.diyaudio.com/community/threads/jlcpcb-just-changed-the-cost-of-via-sizes.404166
- A3144 ~€0.6/10pcs — https://www.luisllamas.es/en/detect-magnetic-fields-arduino-hall-sensor-a3144
- Planilha completa: `COTACAO_CHEAPEST.md`

**Riscos identificados (honestidade factual)**:
1. DRV8302 é 8–60V — 400V link DC está fora de spec (datasheet TI).
2. IPP65R600P7 é 600V/0.6Ω/~6A, NÃO 100A/0.01Ω como a BOM afirma.
3. LM7805 não aceita 400V (máx 35V) — substituir por buck HV.
4. Shunt 1mΩ dissipa 10W a 100A — protótipo OK só até ~50A.
5. XT60 é 65A — usar XT90 para 100A+.

---

## Decisão 6: Correção de Engenharia (BOM + Arquitetura) [CONCLUÍDA ✅ 2026-08-15]

**Problema**: os 3 riscos técnicos identificados na Decisão 5 não foram apenas registrados — foram corrigidos nos arquivos de origem.

**Correções aplicadas em `bom.csv` e `arquitetura.md`**:
1. **Fase 1 = protótipo de bancada 12–48V / 30A** (≤1.4kW): DRV8302 é 8–60V, não suporta 400V. Diagrama, alimentação, térmico e simulação SPICE (DC 48V, Rds 4.5m) atualizados. Caso BYD Seagull (400V/115kW) deferido para Fase 2 (drivers HV UCC21520/IR2184 + MOSFETs 600V/SiC + cooling ativo).
2. **MOSFETs**: IPP65R600P7 (600V/~6A/0.6Ω — spec real) substituído por **IRFB4110 (100V/180A/4.5mΩ)** ×6 na Fase 1.
3. **LM7805** (máx 35V) removido → alimentação via buck integrado do DRV8302 (TPS54160, 60V/1.5A) ou LM2596HV opcional.
4. **Térmico recalculado**: 48V/30A → ~25W total (P_cond 3.2W×6 ≈ 19.4W + P_sw ~6W), heatsink passivo OK.

**Resultado financeiro**: BOM total **$240 → $84.78** componentes; **~$120/placa** (1-5), ~$102 (10-50), ~$90 (100+).

**Verificação (VERIFIQUE, NÃO AFIRME)**: somas conferidas por script Python em `bom.csv` (TOTAL = 84.78) e tabela markdown da seção 6 do `arquitetura.md` (soma = 84.78). Evidência nos arquivos.

**Observação**: as menções remanescentes a IPP65R600P7/LM7805 nos docs são apenas notas explicativas das correções, não specs ativas.

---

**Última Atualização**: 2026-08-15  
**Padrão**: AG3.md Seção 7 (Protocolo de Busca Externa)
