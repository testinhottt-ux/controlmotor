# ARQUITETURA TÉCNICA - Controladora Universal PMSM/BLDC

**Projeto:** Controladora de rotação universal para motores elétricos automotivos
**Fase Inicial:** Track A (Prototipagem + Piloto)
**Plataforma:** ESP32 (prototipagem) → STM32H7 (piloto)

---

## 1. REQUISITOS FUNCIONAIS

### 1.1 Suporte de Motores
- **Tipos**: PMSM (Permanent Magnet Synchronous), BLDC (Brushless DC)
- **Faixa de potência**: alvo 50-250 kW nominal (Fase 2+); **Fase 1 prototipagem em bancada ≤1.4 kW (48V × 30A)** para validação FOC
- **Tensão sistema**: **Fase 1 bancada: 12-48V DC** (limite do DRV8302 = 8-60V); **Fase 2: 400V nominal (320-480V)** com drivers de alta tensão
- **RPM máximo**: 5,000-16,000 RPM (dependente motor)
- **Sensores**: Hall effect (obrigatório), encoder SPI (opcional)

### 1.2 Controle
- **Algoritmo**: Field Oriented Control (FOC) com modulação SVPWM
- **Loop time**: 100 µs (10 kHz update rate mínimo)
- **Modos**: Sensorless (startup + steady-state), sensored (hall + encoder)
- **Proteções**: Over-current, over-voltage, over-temperature, phase loss detection

### 1.3 Interface & Tuning
- **Wireless**: Bluetooth LE (para app web)
- **Parâmetros ajustáveis**: Kp/Ki/Kd (PID loops), PWM frequency, corrente máxima, modo FOC
- **Telemetria**: RPM, Torque, Corrente/fase, Temperatura motor+controlador, Eficiência
- **Persistência**: Parâmetros salvos em EEPROM/Flash

### 1.4 Conformidade
- **Faixa temperatura**: 0-80°C operacional (expandir para -40 a +125°C em série)
- **Proteção mecânica**: IP54 (dust/water resistant)
- **EMI/EMC**: Gerenciado via layout PCB + filtros (validação fase 2)

---

## 2. ARQUITETURA DE HARDWARE

### 2.1 Bloco de Potência (3-Phase Inverter)

```
        +--[FUSE 50A]--+
        |              |
  48V DC (bancada)  Capacitor bank
        |         (2x 470µF, 450V)
        |         Safety discharge R
        |              |
        +--[Gate Driver DRV8302]--+
        |   (PVDD 8-60V)          |
        +------+-------+-------+
        |      |       |       |
      [HS1]  [HS2]  [HS3]  [Predriver]
     MOSFET MOSFET MOSFET (100V/180A)
        |      |       |       |
        LS1   LS2     LS3     Current sense
        |      |       |       (shunt 0.001Ω)
        +------+-------+-------+
              |   |   |
           U  V  W  (saída para motor)
```

**Componentes:**
- **MOSFETs High-Side**: 3x IRFB4110 (100V, 180A, Rds 4.5mΩ) — substitui o IPP65R600P7
  (que é 600V/~6A/0.6Ω e NÃO aguenta 50A como a BOM antiga afirmava)
- **MOSFETs Low-Side**: 3x IRFB4110 (same)
- **Gate Driver**: TI DRV8302 (3-phase, bootstrap built-in, **PVDD 8-60V → apenas bancada**)
- **Capacitor Bank**: 2x 470µF 450V (vale para 48V agora e 400V na Fase 2)
- **Shunt resistor**: 0.001Ω 2% 3W (lido pelo amplificador de shunt interno do DRV8302)
- **Fuse**: 50A automotive-grade (fast-blow)
- **Fase 2 (400V)**: drivers HV (UCC21520 ou IR2184 ×3) + MOSFETs 600V de alta corrente
  (IXFN100N60P / SiC) + cooling ativo — **fora da BOM da Fase 1**

### 2.2 Bloco de Controle (MCU)

```
        ┌─────────────────┐
        │   ESP32-WROOM   │
        │   240MHz Xtensa │
        │   (Fase 1)      │
        ├─────────────────┤
        │ GPIO: 34 pins   │ ─→ PWM (3x para HS, 3x para LS, 1x fault)
        │ ADC: 12-bit     │ ─→ Corrente fases U,V,W + temperatura
        │ SPI/I2C         │ ─→ Hall sensors, encoder (SPI)
        │ UART×2          │ ─→ Debug + CAN bridge
        │ Bluetooth LE    │ ─→ App web (tuning, telemetria)
        │ WiFi (802.11b)  │ ─→ Opcional: OTA firmware
        └─────────────────┘
         
        [STM32H7 substitui ESP32 na Fase 2]
        - 400MHz ARM Cortex-M7
        - 12x PWM timers (resolução maior)
        - 16x ADC converters
        - CAN/CANFD nativo
```

> **Alimentação (corrigido):** o buck integrado do DRV8302 (TPS54160, até 60V / 1.5A)
> fornece 5V/3.3V ao MCU. **Não usar LM7805** (entrada máx. 35V — queimaria com
> 48V ou 400V).

**Pinagem Crítica (ESP32):**
- GPIO32-33: PWM U/V/W high-side (Timer1, 20 kHz)
- GPIO14-27: PWM U/V/W low-side + fault (Timer3)
- ADC1_0-7: Corrente U/V/W, Temp motor, Tensão link DC
- GPIO21-22: I2C (encoder, sensor)
- GPIO16-17: UART debug
- GPIO5-19: Hall sensor inputs (capacitor debounce 10nF)

### 2.3 Sensores & Feedback

| Sensor | Tipo | Sinal | Função |
|--------|------|-------|--------|
| **Hall A/B/C** | Digital | GPIO | Posição rotor (6 estados/rev) |
| **Encoder** | SPI | GPIO21-22 | Feedback velocidade (opcional) |
| **Shunt** | 0-1V | ADC | Corrente motor (0-100A) |
| **Temp motor** | NTC 10k | ADC | Proteção thermal |
| **Temp driver** | NTC 10k | ADC | Proteção térmica gate driver |
| **Tensão link** | Divisor 10:1 | ADC | Over/under voltage detection |

### 2.4 Proteções & Filtragem

```
Power Entry:
  ┌─[50A Fuse]─[EMI filter (CLC)]─[Capacitor]
  │                   
  ├─[Brake Resistor, 10Ω 50W] (recarga, opcional)
  │
  └─[Gate driver Bootstrap]

Control signals:
  ├─[Pull-up 10k + Cap 10nF] Hall sensors
  ├─[Ferrite bead] ADC supply (filtro LC)
  └─[Ferrite bead + 10nF] PWM cables (EMI mitigation)
```

---

## 3. SOFTWARE & FIRMWARE

### 3.1 Stack de Firmware (Fase 1 - ESP32)

```
┌─────────────────────────────────────┐
│        Application Layer            │ (Tuning, telemetria, BLE API)
├─────────────────────────────────────┤
│     SimpleFOC Library (C++)         │ (FOC algorithm, SVPWM modulation)
├─────────────────────────────────────┤
│  Arduino Framework (esp32-hal)      │ (GPIO, PWM, ADC drivers)
├─────────────────────────────────────┤
│  FreeRTOS (built-in esp32)          │ (Task scheduling, 2-core parallel)
├─────────────────────────────────────┤
│  lwIP + Bluetooth LE stack          │ (Wireless communication)
└─────────────────────────────────────┘
```

**SimpleFOC Customizações:**
- Adicionar suporte IPM-SynRM (saliência rotor para startup sensorless)
- Otimizar loop time 100µs → 50µs (20kHz control)
- EEPROM: Salvar PID gains, limites corrente, calibração motor

### 3.2 Estrutura de Código

```
firmware/
├── src/
│   ├── main.cpp               # Inicialização, setup tasks
│   ├── motor_control.cpp      # FOC loop (high priority)
│   ├── sensors.cpp            # Hall/encoder/ADC reading
│   ├── safety.cpp             # Proteções (overcurrent, thermal)
│   ├── bluetooth_api.cpp      # BLE characteristic definitions
│   └── telemetry.cpp          # Streaming dados (RPM, corrente)
├── lib/
│   └── SimpleFOC/             # Modified SimpleFOC source
├── .gitignore
└── platformio.ini             # Build config (PlatformIO)
```

**Loop Tempo Real (Core 0 - dedicado controle):**
```c
// Task executada a 10 kHz (100µs)
void motor_control_task(void *pvParameter) {
  while(1) {
    // 1. Ler correntes (ADC): 5µs
    read_currents();
    
    // 2. Ler posição rotor (Hall/encoder): 3µs
    update_rotor_position();
    
    // 3. Algoritmo FOC (PID + SVPWM): 50µs
    foc_loop();
    
    // 4. Atualizar PWM gate driver: 10µs
    update_pwm();
    
    // 5. Verificar proteções: 15µs
    check_safety();
    
    // 6. Wait para próximo ciclo (alguns µs padding)
    vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(0.1));
  }
}
```

### 3.3 Bluetooth LE API (Web App ↔ Firmware)

**Serviços BLE:**
```
Service: 180A (Motor Control Service)
├── Characteristic: 2A58 (Voltage) - Leitura
│   └── Valor: Tensão link DC (float 32-bit)
├── Characteristic: 2A19 (Battery Level) - Leitura
│   └── Valor: SoC (0-100%)
├── Characteristic: 2A6E (Temperature) - Leitura/Notify
│   └── Valor: Temp motor (int16 -40 a 125°C)
└── Characteristic: Custom_RPM (Custom UUID)
    └── Valor: RPM motor (uint16)

Service: 180D (Motor Control Config)
├── Characteristic: Kp_PID (uint16) - Read/Write
├── Characteristic: Ki_PID (uint16) - Read/Write
├── Characteristic: Kd_PID (uint16) - Read/Write
├── Characteristic: Max_Current (uint16) - Read/Write
├── Characteristic: Target_RPM (uint16) - Read/Write
└── Characteristic: Tuning_Mode (uint8) - Read/Write
    0=Disabled, 1=Performance, 2=Efficiency
```

**App Web (React.js + Web Bluetooth API):**
- Interface real-time com gauges (RPM, Corrente, Temp)
- Sliders para ajustar Kp/Ki/Kd
- Toggle modos (sensorless/sensored, FOC normal/IPM)
- Gráficos histórico (últimos 60s telemetria)
- Botão "Salvar preset"

---

## 4. ESPECIFICAÇÕES DE POTÊNCIA

> **Nota de correção:** a BOM antiga especificava IPP65R600P7 com 600V/100A/Rds 0.01Ω.
> Spec real: **600V, ~6A, 0.6Ω** — incompatível com 50A. Todos os cálculos abaixo foram
> recalculados. O DRV8302 é de 8-60V, então **a Fase 1 opera em bancada (48V/30A)**.

### Caso Fase 1 — Prototipagem em bancada (48V / 30A)

```
Tensão link:   48V DC (bancada)
Corrente:      30A contínuo
Potência:      ~1.4 kW (validação de controle/FOC, não potência plena)

Controladora:
- MOSFETs 100V/180A (IRFB4110, Rds 4.5mΩ) → margem térmica ampla a 30A
- PWM frequency: 20 kHz (compromisso EMI vs eficiência)
- Dissipação: ~25W @ 30A → heatsink passivo OK
- Tamanho: 300x200x60mm (retrofit under-floor)
```

### Dissipação Térmica (MOSFET — Fase 1)
```
P_loss = R_ds(on) × I²rms + P_sw

R_ds(on) ≈ 5.4 mΩ (IRFB4110 @ 125°C)
I_rms @ 30A trifásico ≈ 24.5A
P_cond = 0.0054 × 24.5² = 3.2 W × 6 MOSFETs = ~19.4 W
P_sw ≈ 1 W × 6 = ~6 W
Total ≈ 25 W dissipado

Heatsink: 2-3 K/W (natural convection) → ΔT ≈ 60°C
Operação: 25°C ambient → 85°C case (OK em bancada)
```

### Caso Alvo Fase 2 — BYD Seagull (400V / 115 kW)

```
Motor:      115 kW @ 12,000 RPM
            220 Nm torque @ 5,000 RPM
Tensão:     ~370V nominal (285-470V operacional)
Corrente:   ~200A pico (85A nominal a 115kW)

Nota:       400V/85A exige dispositivos 600-750V de alta corrente
            (SiC / módulo IGBT) + drivers HV (UCC21520 / IR2184 ×3) +
            cooling ativo (líquido ou ventilação forçada).
            Cálculo térmico final depende do dispositivo escolhido —
            DEFERIDO para a Fase 2 (fora da BOM atual).
```

---

## 5. SIMULAÇÃO ELÉTRICA (SPICE)

**Arquivo**: `schematic.cir` (LTspice)

```spice
* 3-Phase BLDC Motor & Gate Driver Simulation
* Objective: Validar duty cycle, EMI ripple, overshoot transient

.title BLDC Motor Control Simulation

* Power Supply (Fase 1 bancada 48V)
Vdc 1 0 DC 48

* Gate Driver Model (PWM 20kHz)
Vgp1 gp1 0 PULSE(0 12 0 100n 100n 25u 50u)  ; U high-side
Vgp2 gp2 0 PULSE(0 12 8.33u 100n 100n 25u 50u)  ; V phase shift
Vgp3 gp3 0 PULSE(0 12 16.66u 100n 100n 25u 50u) ; W phase shift

* High-Side MOSFETs (IRFB4110 model, 100V/180A, Rds=4.5m)
S1 1 u gp1 0 Rg=1 Rds=4.5m
S2 1 v gp2 0 Rg=1 Rds=4.5m
S3 1 w gp3 0 Rg=1 Rds=4.5m

* Low-Side MOSFETs
S4 u 0 gp1_inv 0 Rg=1 Rds=4.5m
S5 v 0 gp2_inv 0 Rg=1 Rds=4.5m
S6 w 0 gp3_inv 0 Rg=1 Rds=4.5m

* Inverter dead-time logic (simula hardware)
.subckt deadtime_logic
* Gerar gp1_inv, gp2_inv, gp3_inv com deadtime 200ns
.ends

* Motor Phase Impedances (PMSM equivalent circuit)
Ru u 0 0.001              ; Resistância fase U
Lu u 0 100u IC=0         ; Indutância fase

* Correntes e tensões medidas
.measure tran I_peak MAX I(Vdc)
.measure tran V_ripple PP V(u)
.measure tran Efficiency PARAM avg(P)/avg(P_supply)

.transient 0 0.01 0 1u   ; Simular 10ms
.end
```

**Verificações**:
- Peak current durante comutação (proteger gate driver)
- Voltage ripple em link DC (<5% = 20V @ 400V)
- Ringing em fase U/V/W (EMI source analysis)
- Thermal dissipation profile

---

## 6. LISTA DE MATERIAIS (BOM) - Fase 1 Prototipagem

| Item | Referência | Qtd | Custo/un | Subtotal |
|------|------------|-----|----------|----------|
| MCU | ESP32-WROOM-32E | 1 | $3.50 | $3.50 |
| Gate Driver | TI DRV8302DCA (8-60V) | 1 | $7.72 | $7.72 |
| MOSFET HS | IRFB4110 100V/180A | 3 | $1.50 | $4.50 |
| MOSFET LS | IRFB4110 100V/180A | 3 | $1.50 | $4.50 |
| Capacitor | 470µF 450V (2x) | 2 | $2.50 | $5.00 |
| Shunt resistor | 0.001Ω 2% 3W (3x) | 3 | $1.50 | $4.50 |
| Bootstrap caps | 10µF 50V (3x) | 3 | $0.15 | $0.45 |
| Passivos | gate/damping/discharge resistores, decoupling caps, bootstrap diodes, ferrites, LDO indutor, bulk 5V | - | - | $1.91 |
| TVS diode | SMBJ50CA (2x) | 2 | $0.30 | $0.60 |
| Hall sensors | A3144 (3x) | 3 | $0.10 | $0.30 |
| NTC thermistor | 10k 1% (2x) | 2 | $0.15 | $0.30 |
| Fuse | 50A automotive | 1 | $1.50 | $1.50 |
| Heatsink | alumínio 300x200x10mm | 1 | $8.00 | $8.00 |
| PCB (2oz copper) | 4-layer JLCPCB | 1 | $30.00 | $30.00 |
| Conectores | XT60, M4 studs, JST aux, debug UART | - | - | $1.70 |
| Buck opcional | LM2596HV 60V | 1 | $1.50 | $1.50 |
| Cabos + mecânica + potting | 6mm², parafusos, silicone, pasta térmica, shrink | - | - | $8.80 |
| **TOTAL** | | | | **$84.78** |

**Observação**: Soma $84.78 para placa + componentes (corrigido — antes $240). Adicionado $20 frete + $15 housing/caixa → **~$120 por unidade** (prototipagem). Com volume: ~$102 (10-50) / ~$90 (100+). Detalhe completo e fontes em `bom.csv` e `COTACAO_CHEAPEST.md`.

---

## 7. ROADMAP

| Fase | Período | Milestone | Status |
|------|---------|-----------|--------|
| **1. Proto ESP32** | Semana 1-6 | FOC funcional + BLE API | INICIADO |
| **1.1 Firmware SimpleFOC** | Sem 1-3 | Setup Hall + SVPWM | TODO |
| **1.2 Schematic + PCB** | Sem 2-4 | KiCAD layout | TODO |
| **1.3 App Web Bluetooth** | Sem 3-5 | React dashboard | TODO |
| **1.4 Testes motor** | Sem 5-6 | Validação FOC bancada (48V/30A) | TODO |
| **2. Piloto STM32** | Semana 7-14 | Escalado 210kW | PENDING |
| **2.1 Firmware STM32** | Sem 7-10 | Ported SimpleFOC | PENDING |
| **2.2 Poder stage upgrade** | Sem 8-11 | SiC MOSFETs, better cooling | PENDING |
| **2.3 EMC validation** | Sem 12-13 | FCC/CE testing | PENDING |
| **3. Série NXP SoC** | Sem 15-26 | NRE + validação ASIL D | PENDING |

---

## 8. RISCOS & MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| Desempenho FOC inadequado | Média | Alto | Usar SimpleFOC validada + espiar referências STM32 |
| EMI/EMI acoplamento | Alta | Médio | Layout multi-layer, ferrite beads, star grounding |
| Thermal runaway | Média | Alto | Monitorar temperatura, throttle corrente se T > 80°C |
| Falha gate driver @ 30A | Baixa | Alto | Bootstrap capacitor verification, gate diodes |
| WiFi interference | Média | Baixo | Separar antena Bluetooth de potência, ferrite |
| **Driver 400V (Fase 2)** | Alta | Alto | DRV8302 é 8-60V. Fase 2 exige drivers HV (UCC21520/IR2184) + MOSFETs 600V + cooling ativo — fora da BOM Fase 1 |

---

**Versão**: 1.1  
**Data**: 2026-08-15  
**Próximo passo**: Desenhar schematic KiCAD

**Changelog v1.0 → v1.1 (2026-08-15):**
- Correção de engenharia: Fase 1 agora é protótipo de bancada **12-48V / 30A** (DRV8302 é 8-60V, não suporta 400V).
- MOSFETs corrigidos: IRFB4110 (100V/180A/4.5mΩ) no lugar do IPP65R600P7 (que é 600V/~6A/0.6Ω — incompatível com 50A).
- LM7805 removido (máx 35V). Alimentação via buck integrado do DRV8302 (TPS54160) ou LM2596HV opcional.
- Térmico recalculado para bancada 48V/30A (~25W, passivo OK). Caso BYD Seagull (400V/115kW) deferido para Fase 2.
- BOM total corrigido: **$240 → $84.78** (detalhe em `bom.csv`, fontes em `COTACAO_CHEAPEST.md`).
