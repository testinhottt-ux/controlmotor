# COTAÇÃO BARATA — BOM Controladora PMSM/BLDC (Fase 1 Prototipagem)

**Data:** 2026-08-15
**Objetivo:** Re-cotar a BOM de `bom.csv`/`arquitetura.md` ao menor preço possível,
comprando em AliExpress + LCSC (distribuidor chinês, mesma rede da JLCPCB).
**Resultado:** **~US$ 91 em componentes** (vs US$ 240 da BOM original) → **~US$ 126/placa**
com frete + invólucro (vs US$ 400 da BOM original). **Economia ~68-70%.**

---

## 1. RESUMO

| | BOM Original | Cotação Barata | Economia |
|---|---|---|---|
| Componentes (partes) | US$ 240 | **US$ 91** | -62% |
| PCB | US$ 100 (PCBWay) | US$ 30 (JLCPCB) | -70% |
| Mão de obra | US$ 60 | (DIY / PCBA LCSC) | — |
| Invólucro/mecânica | US$ 100 | US$ 15 | -85% |
| Frete | — | US$ 20 | — |
| **Total / unidade** | **~US$ 400** | **~US$ 126** | **-68%** |

---

## 2. TABELA DE PREÇOS (menor preço encontrado, com fonte)

| Item | Qtd | Orig. | **Barato** | Subtotal | Fonte / Nota |
|------|-----|-------|-----------|----------|--------------|
| ESP32-WROOM-32E | 1 | $12.00 | **$3.50** | $3.50 | LCSC C701343 $5.08 (qty1) / AliExpress ~$3.5 |
| DRV8302DCA gate driver | 1 | $35.00 | **$7.72** | $7.72 | LCSC C84672 $7.72 (qty1). NÃO comprar módulo de $35 |
| MOSFET HS IPP65R600P7 | 3 | $8.00 | **$1.50** | $4.50 | CoolMOS 600V ~$1–3 em distribuição |
| MOSFET LS IPP65R600P7 | 3 | $8.00 | **$1.50** | $4.50 | idem |
| Capacitor 470µF 450V | 2 | $5.00 | **$2.50** | $5.00 | LCSC Samyoung TLS $2.74 / AliExpress $2.47 |
| Bootstrap cap 10µF 50V | 3 | $0.50 | **$0.15** | $0.45 | lote AliExpress |
| Decoupling 100µF 10V | 1 | $0.80 | **$0.30** | $0.30 | LCSC |
| Bypass 100nF | 4 | $0.05 | **$0.01** | $0.04 | lote 0603 |
| Filter 10nF | 1 | $0.05 | **$0.01** | $0.01 | lote |
| Gate resistor 10Ω | 9 | $0.10 | **$0.02** | $0.18 | lote 1206 |
| Gate pull-down 10k | 3 | $0.05 | **$0.01** | $0.03 | lote |
| EMI damping 100Ω | 9 | $0.15 | **$0.05** | $0.45 | lote 0603 |
| Discharge 1M 5W | 1 | $0.50 | **$0.20** | $0.20 | lote |
| Shunt 0.001Ω (1mΩ) | 3 | $2.00 | **$1.50** | $4.50 | AliExpress shunt placa metálica 2–5W $0.99–3.08 |
| NTC 10k | 2 | $0.80 | **$0.15** | $0.30 | lote |
| Indutor LDO 10µH | 1 | $0.30 | **$0.10** | $0.10 | LCSC |
| Ferrite bead 1µH | 3 | $0.15 | **$0.05** | $0.15 | lote |
| Bootstrap diode 3A 200V | 3 | $0.30 | **$0.10** | $0.30 | lote |
| TVS 50V | 2 | $1.00 | **$0.30** | $0.60 | lote |
| Hall sensor A3144 | 3 | $0.80 | **$0.10** | $0.30 | AliExpress 10pcs ~€0.6–$1 |
| Hall debounce 10nF | 3 | $0.05 | **$0.01** | $0.03 | lote |
| Fuse 50A | 1 | $3.00 | **$1.50** | $1.50 | AliExpress |
| Conector XT60 (par) | 1 | $2.00 | **$0.40** | $0.40 | AliExpress 5 pares ~$2.5 |
| Studs M4 latão | 3 | $0.50 | **$0.20** | $0.60 | lote |
| Header JST aux | 1 | $0.50 | **$0.20** | $0.20 | lote |
| Debug connector | 1 | $1.00 | **$0.50** | $0.50 | lote |
| **PCB 4 camadas 300×200mm 2oz** | 1 | $100.00 | **$30.00** | $30.00 | JLCPCB (~$7 p/ 100×100mm; maior +2oz ≈ $25–35). PCBWay cobra $48–116 |
| Heatsink alumínio | 1 | $15.00 | **$8.00** | $8.00 | AliExpress perfil extrudado 300mm |
| Thermal paste | 1 | $3.00 | **$1.50** | $1.50 | AliExpress |
| Cabo potência 6mm² | 2m | $0.50 | **$0.30** | $0.60 | AliExpress silicone |
| Cabo motor blindado | 3m | $0.80 | **$0.40** | $1.20 | AliExpress |
| Shrink tube | 1 | $1.00 | **$0.50** | $0.50 | lote |
| Parafusos M4 | 20 | $0.10 | **$0.05** | $1.00 | lote |
| Potting/sealant | 1 | $10.00 | **$4.00** | $4.00 | AliExpress (silicone) |
| **Buck HV 400V→5/12V** | 1 | $2.00 | **$8.00** | $8.00 | ver Nota 3 (LM7805 NÃO serve p/ 400V) |
| Bulk cap 5V | 1 | $0.30 | **$0.10** | $0.10 | lote |
| Divider VDC | 1 | $0.10 | **$0.02** | $0.02 | lote |
| **TOTAL COMPONENTES** | | **$240** | | **$91.28** | |
| Frete estimado (LCSC + AliExpress) | | | | **$20.00** | |
| Invólucro/mecânica barata | | $100 | | **$15.00** | caixa alumínio AliExpress |
| **TOTAL / UNIDADE** | | **~$400** | | **~$126** | |

---

## 3. ESTRATÉGIA DE COMPRA (mais barato possível)

1. **Pedido 1 — LCSC (componentes SMD + ICs):** DRV8302DCA, ESP32, capacitores,
   resistores, NTC, conectores. Preços são ~50–80% menores que DigiKey/Mouser.
   Bônus: LCSC faz **PCBA** (montagem) com a mesma base de peças.
2. **Pedido 2 — AliExpress (itens de lote):** Hall A3144, XT60, shunt metálico,
   parafusos, shrink, heatsink, silicone, cabos. Comprar em lote (5–10 pcs) barateia
   o custo unitário e sobra estoque para prototipagem.
3. **PCB — JLCPCB:** importar gerbers (já existem em `gerbers/`). 4 camadas a partir
   de ~$7 (100×100mm); reduzir a placa para 150×100mm se possível para cortar custo.

---

## 4. AVISOS TÉCNICOS CRÍTICOS (honestidade factual)

> A cotação usa os preços reais da BOM listada, MAS a BOM original contém 3 erros
> de engenharia que precisam de correção — não dá para apenas "comprar mais barato":

1. **DRV8302 é 8–60V, não 400V.** O datasheet TI (SLES267C) especifica PVDD 8–60V.
   A arquitetura de 400V link DC com DRV8302 direto está **fora de spec**. Para a
   prototipagem na bancada (12–60V) está OK; para 400V é preciso driver HV
   (UCC21520/IR2184) — componente adicional fora desta cotação.
2. **IPP65R600P7 NÃO é 600V/100A/0.01Ω.** É 600V, 0.6Ω, ~6A (CoolMOS P7 pequeno).
   A BOM superestima o MOSFET. Para 100A reais o custo é US$ 15–40/peça. A cotação
   acima serve para protótipo de baixa corrente / bancada (validação FOC).
3. **LM7805 não aceita 400V (máx 35V).** Substituído por buck de alta tensão
   (módulo isolado 400V→12/5V, ~$8). Sem ele a placa queima.
4. **Shunt 1mΩ a 100A dissipa 10W.** Os de 2–5W do AliExpress servem para protótipo
   até ~50A; acima disso usar shunt 10W.
5. **XT60 é 65A.** OK para protótipo de 50A; para 100A+ usar XT90 ou bornes.

---

## 5. FONTES VERIFICADAS (abertas durante a pesquisa)

- LCSC DRV8302DCA (C84672): $7.72 qty1 — https://www.lcsc.com/product-detail/C84672.html
- LCSC ESP32-WROOM-32E-N16 (C701343): $5.08 qty1 — https://www.lcsc.com/product-detail/C701343.html
- LCSC 470µF 450V Samyoung (C53330121): $2.74 — https://www.lcsc.com/product-detail/C53330121.html
- AliExpress 470µF 450V 30×50mm: $2.47 — https://alitools.io/en/showcase/470uf-450v-30-50mm-electrolytic-capacitor-capacitors-1005001622272570
- AliExpress 450V 470µF 35×50mm: $3.17 — https://alitools.io/en/showcase/450v-470uf-35-50mm-470uf-450v-aluminum-electrolytic-capacitor-capacitors-1175908928
- AliExpress shunt 1mΩ: $0.99–3.08 — https://www.aliexpress.com/w/wholesale-0.001%20ohm%20shunt.html
- A3144 ~€0.6/10pcs — https://www.luisllamas.es/en/detect-magnetic-fields-arduino-hall-sensor-a3144
- CoolMOS 600V $1–3 — https://www.ad-hoc-news.de/boerse/news/ueberblick/the-coolmos-p7-infineon-pushes-efficient-home-power-designs/69834285
- JLCPCB 4L ~$7/100×100mm — https://www.diyaudio.com/community/threads/jlcpcb-just-changed-the-cost-of-via-sizes.404166
- PCBWay 4L 100×100mm $48 / 150×100mm $116 — https://www.pcbway.com/pcb_prototype/4_Layer_pcb/100x100mm.html
- DRV8302 datasheet (8–60V) — https://www.ti.com/lit/gpn/DRV8302
- XT60 par ~$0.40 — https://www.aliexpress.us/item/3256806667274442.html

**Preços são médias do momento da pesquisa (ago/2026); variam com promoções e lote.**