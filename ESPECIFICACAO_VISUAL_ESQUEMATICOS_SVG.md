# ESPECIFICAÇÃO VISUAL E MATRIZ DE COORDENADAS: ESQUEMÁTICOS SVG

> **Projeto:** Inversor Trifásico BLDC/PMSM Universal (48V / 400V)  
> **Arquivos Alvo:** `esquemaprofisionalsvg`, `esquema.svg`, `controlmotor-dual.html`  
> **Objetivo:** Eliminar 100% de sobreposições de textos, símbolos, linhas de barramento e conexões de gate/shunt, garantindo leitura técnica padrão industrial.

---

## 1. GRID GLOBAL E DIMENSÕES (1600 × 1000 px)

```
(0,0) ──────────────────────────────────────────────────────────── (1600,0)
  │                                                                 │
  │  [INFO / TITLE BLOCK] X: 1180..1550, Y: 15..95                  │
  │                                                                 │
  │ ═══ BARRAMENTO VDC (+48V) ════════════════════════════════════  Y = 110
  │                                                                 │
  │ [BLOCO 1: ENTRADA]    [BLOCO 2: CHOPPER]   [BLOCO 3: DRV8302]  [PONTE TRIFÁSICA U/V/W]  [BORNES]
  │ X: 50..520            X: 560..710          X: 740..950         X: 980..1420             X: 1450..1560
  │ Y: 110..500           Y: 110..500          Y: 140..500         Y: 140..530              Y: 180..480
  │                                                                 │
  │ ──────────────────────────────────────────────────────────────  Y = 535
  │                                                                 │
  │ [BLOCO 4: ESP32-MCU]  [BLOCO 5: SENSORES]  [BLOCO 6: CAN ISO]  [BLOCO 7: POWER MGMT]
  │ X: 80..460            X: 500..730          X: 500..830         X: 880..1480
  │ Y: 560..890           Y: 560..720          Y: 745..885         Y: 560..885
  │                                                                 │
  │ ═══ BARRAMENTO GND (POWER PLANE) ════════════════════════════  Y = 910
  │                                                                 │
(0,1000) ───────────────────────────────────────────────────────── (1600,1000)
```

---

## 2. REGRAS ANTI-SOBREPOSIÇÃO (DESIGN RULES)

1. **Gate Drive vs. RC Snubbers nas Fases:**
   - *Problema anterior:* O snubber lateral esquerdo ocupava $X = -10 \dots 20$, colidindo com o resistor de gate horizontal em $Y = 100$.
   - *Regra aplicada:* Os circuitos de Snubber RC foram posicionados no **lado direito** da fase ($X = +75 \dots 110$), enquanto os resistores de Gate ficaram no **lado esquerdo** ($X = -35 \dots +10$). Separação horizontal $> 65\text{ px}$.
2. **Kelvin Sense vs. Bordas das Fases:**
   - *Problema anterior:* Textos `S_U_P` e `S_U_N` em $X = -15$ cruzavam a linha tracejada delimitadora do bloco.
   - *Regra aplicada:* Pistas Kelvin roteadas em $45^\circ$ com textos destacados em caixas dedicadas em $X = -45 \dots -15$, com largura de bloco ajustada para $150\text{ px}$ (espaçamento entre fases de $160\text{ px}$).
3. **Roteamento das Fases para os Bornes de Saída:**
   - *Problema anterior:* Linhas de fase cruzando horizontalmente por cima dos MOSFETs das fases adjacentes.
   - *Regra aplicada:* Roteamento em três alturas verticais distintas:
     - **Fase U:** Sai em $Y = 220$ e vai direto para o Filtro U ($Y = 220$).
     - **Fase V:** Sai em $Y = 220$, desce para $Y = 310$ em canal livre e entra no Filtro V ($Y = 310$).
     - **Fase W:** Sai em $Y = 220$, desce para $Y = 400$ em canal livre e entra no Filtro W ($Y = 400$).
4. **Espaçamento de Textos de Pinos no MCU e Driver:**
   - Altura de linha mínima padronizada em **26 px** (font-size: 11px monospace).
5. **Chopper de Freio:**
   - Diodo $D_{brake}$ deslocado para a esquerda com texto em posição superior desimpedida ($Y = 115$), resistor $R_{brake}$ no centro ($X = 640$) e MOSFET na parte inferior ($Y = 300$).
