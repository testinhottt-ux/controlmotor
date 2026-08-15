# CONTROLADORA BLDC UNIVERSAL — Manual do Usuário

**Versão**: 1.0  
**Data**: 2026-08-13  
**Firmware**: FOC v1.0.0  
**Compatibilidade**: Motor BLDC/PMSM 50-120 kW  

---

## SUMÁRIO

1. [Visão Geral](#1-visão-geral)
2. [Ferramentas Necessárias](#2-ferramentas-necessárias)
3. [Instalação de Hardware](#3-instalação-de-hardware)
4. [Procedimento de Auto-Aprendizado](#4-procedimento-de-auto-aprendizado)
5. [Ajustes de Superfície e Parâmetros](#5-ajustes-de-superfície-e-parâmetros)
6. [Calibração de Sensores](#6-calibração-de-sensores)
7. [Proteções e Limites](#7-proteções-e-limites)
8. [Indicadores de Alarme](#8-indicadores-de-alarme)
9. [Troubleshooting](#9-troubleshooting)
10. [Especificações Técnicas](#10-especificações-técnicas)

---

## 1. VISÃO GERAL

A Controladora BLDC Universal é um sistema de controle vetorial (FOC) para motores síncronos de imã permanente (PMSM) e motores sem escovas de comutação eletrônica (BLDC). O sistema oferece:

- **Controle Vetorial Orientado ao Fluxo (FOC)**: Algoritmo de controle 10 kHz
- **Auto-Aprendizado Astrom-Hagglund**: Tuning automático de ganhos PID
- **Proteções Integradas**: Overcurrent, thermal, voltage
- **Telemetria em Tempo Real**: RPM, corrente, temperatura, tensão
- **Interface Web Bluetooth**: Controle e monitoramento via dispositivos móveis

### Características Principais

| Parâmetro | Valor |
|-----------|-------|
| **Tensão de Entrada** | 300 - 450V DC |
| **Potência Máxima** | 120 kW (150 A contínua) |
| **Frequência PWM** | 20 kHz |
| **Frequência de Controle** | 10 kHz (100 µs) |
| **Resolução ADC** | 12 bits |
| **Sensores Hall** | 3x (comutação + feedback) |
| **Precisão Shunt** | 0.1 mΩ ±2% |
| **Dissipação Térmica** | Heatsink 0.3 K/W |
| **Interfaces** | Bluetooth LE 5.0, CAN bus (futuro) |

---

## 2. FERRAMENTAS NECESSÁRIAS

### Hardware

```
✓ 1x Computador com Windows 10+ ou macOS
✓ 1x Controladora BLDC (com ESP32-WROOM-32E)
✓ 1x Bateria/Fonte DC 300-450V
✓ 1x Motor BLDC/PMSM (com sensores Hall)
✓ 1x Acelerador (0-5V throttle pedal)
✓ 1x Chave de Ignição (12V ativa)
✓ 1x Osciloscópio (opcional, para debug)
✓ 1x Multímetro Digital
```

### Software

```
✓ Interface Web: controlmotor-ui.html (navegador moderno)
  ou
✓ Aplicativo Desktop: Bluetooth Low Energy client
```

### Cabos e Conectores

```
✓ 3x Cabos trifásicos (motor U, V, W) — 4 AWG mínimo
✓ 1x Conector Hall 6 pinos (2.54 mm pitch)
✓ 1x Conector Shunt de Corrente (banana 4 mm)
✓ 1x Fiação sensores temperatura (2x NTC 10k)
✓ Malha de Blindagem (EMI/RFI protection)
```

---

## 3. INSTALAÇÃO DE HARDWARE

### 3.1 Montagem Física

#### Passo 1: Verificação Inicial
```
1. Inspeção visual da PCB (sem componentes danificados)
2. Verificação de soldagem (sem bolhas, cold joints)
3. Teste de continuidade GND em toda placa (multímetro)
4. Teste de curto entre +400V e GND (deve ler ∞)
```

#### Passo 2: Montagem do Radiador
```
1. Limpar superfície MOSFET com álcool isopropílico
2. Aplicar pasta térmica (TIM) uniformemente
3. Apertar parafusos em sequência X (não socar)
4. Torque recomendado: 2-3 Nm
5. Verificar temperatura radiador ≤ 50°C sem potência
```

#### Passo 3: Fiação do Motor

**Conexões 3-Fase:**
```
Controladora         Motor
─────────────────────────────
U (fase 1)    ──→   Bobina U
V (fase 2)    ──→   Bobina V
W (fase 3)    ──→   Bobina W
```

⚠️ **Ordem crítica**: Trocar fase inverte rotação. Testar com baixa potência.

**Sensores Hall (6 pinos):**
```
Pino 1 (VCC 5V)    ──→   Hall +5V
Pino 2 (GND)       ──→   Hall GND
Pino 3 (HALL_A)    ──→   Sensor 1 (U)
Pino 4 (HALL_B)    ──→   Sensor 2 (V)
Pino 5 (HALL_C)    ──→   Sensor 3 (W)
Pino 6 (NC)        ──→   Não conectado
```

**Sensores de Corrente (Shunt):**
```
Controladora              Shunt (0.1 mΩ)
─────────────────────────────────────────
Saída Fase 1 ──→ Shunt ──→ Motor Fase 1
ADC_ISENSE (pin 32) ──→ Tensão Shunt (max 1V)
```

**Sensores de Temperatura (NTC 10k):**
```
Posição 1: No dissipador (heatsink)
Posição 2: Na bobina do motor (se possível)

Conexão: +3.3V ──[10k] ──┬── GND
                        ADC_TEMP
```

#### Passo 4: Tensão de Alimentação

```
Conexão DC:
  B+ (300-450V) ──→ Capacitor Bank (2x470µF 450V)
  B- (GND)      ──→ Ground Plane

Proteção de Descarga:
  Conectar resistor de descarga 10k 10W entre B+ e GND
  Aguardar 2 minutos antes de toque
```

**Segurança Crítica**: Sempre desligar bateria antes de trabalho de manutenção.

### 3.2 Conexão de Controle

**Acelerador (Throttle):**
```
Entrada:  0-5V DC (linear)
Mapeamento:
  0.0V  → 0% throttle (parado)
  2.5V  → 50% throttle (meio)
  5.0V  → 100% throttle (máximo)
```

**Chave de Ignição:**
```
Entrada: 12V ativa
Função: Enable/Disable controller
  12V  → Controlador ativo
  0V   → Controlador em standby
```

**Comunicação Bluetooth:**
```
Módulo: BLE 5.0 (integrado ESP32)
Características expostas:
  RPM, Corrente, Temperatura, Tensão (read-only)
  Kp, Ki, Kd, Throttle (read-write)
```

---

## 4. PROCEDIMENTO DE AUTO-APRENDIZADO

O **Auto-Aprendizado** usa o método de sintonia Astrom-Hagglund (relay tuning) para calibrar automaticamente os ganhos PID (Kp, Ki, Kd).

### 4.1 Preparação

```
1. Motor montado e fiado corretamente
2. Sensor Hall funcionando (verificar com osciloscópio)
3. Acelerador zerado (throttle = 0)
4. Bateria conectada e indicadores vermelhos ausentes
5. Sem carga mecânica no motor (roda livre)
```

### 4.2 Procedimento Passo-a-Passo

**Via Interface Web:**

```
1. Abrir: http://localhost:8000/controlmotor-ui.html
2. Aguardar conexão (status "Conectado" em verde)
3. Aba "Parâmetros PID" → toggle "Auto-Aprendizado"
4. Clicar botão "🤖 Auto-Learn"
5. Aguardar ~30 segundos
   - Motor fará série de acelerações/desacelerações
   - Medição de overshoot e tempo de resposta
   - Cálculo de Kp, Ki, Kd automaticamente
6. Valores atualizados em tempo real
7. Motor volta ao repouso automaticamente
```

**Via Bluetooth (App Móvel):**

```
1. Conectar app ao controlador via BLE
2. Navegar para "Auto-Tuning" menu
3. Ativar toggle "Auto-Learn"
4. Iniciar medição
5. Aguardar conclusão
6. Confirmar novos ganhos
```

### 4.3 Verificação de Resultado

Após auto-aprendizado, verificar:

```
✓ Kp deve estar entre 0.5 - 3.0
✓ Ki deve estar entre 0.05 - 0.2
✓ Kd deve estar entre 0.01 - 0.1
✓ Resposta em malha fechada: tempo resposta 50-100 ms
✓ Overshoot < 10% em degrau de velocidade
```

Se valores fora de range → reforçar sensores ou testar novamente.

---

## 5. AJUSTES DE SUPERFÍCIE E PARÂMETROS

### 5.1 Visualização (View)

**Painel de Telemetria — Informações Básicas**

```
┌─────────────────────────────────────┐
│ RPM:        5000 rpm                │
│ Corrente:   45 A                    │
│ Temperatura: 52 °C                  │
│ Tensão:     380 V                   │
│ Potência:   17.1 kW                 │
└─────────────────────────────────────┘

Cálculo: P = U × I × √3 × cosφ
         P ≈ 380 × 45 × 1.732 × 0.95 ≈ 17.1 kW
```

**Gráficos de Aquisição (Curvas)**

```
Modo histórico (últimos 60 segundos):
- RPM vs Tempo
- Corrente vs Tempo
- Temperatura vs Tempo
- Tensão vs Tempo

Atualização: ~2 Hz
Escala: Auto-zoom ou manual
```

### 5.2 Ajuste Manual de Parâmetros

#### Ganhos PID

| Parâmetro | Min | Nominal | Max | Efeito |
|-----------|-----|---------|-----|--------|
| **Kp** | 0.01 | 0.50 | 5.00 | Resposta rápida |
| **Ki** | 0.001 | 0.10 | 1.00 | Erro estado estacionário |
| **Kd** | 0.001 | 0.05 | 0.50 | Amortecimento |

**Procedimento de Tuning Manual**

```
1. Aumentar Kp gradualmente até oscilar
2. Reduzir Kp até 80% do valor crítico
3. Aumentar Ki lentamente até sumir erro dc
4. Aumentar Kd para reduzir overshoot
5. Testar em ramp (aceleração progressiva)
```

#### Limitadores

```
Corrente Máxima:   150 A (proteção MOSFET)
RPM Máximo:        12000 rpm (limitador software)
Temperatura Limite: 85 °C (shutdown automático)
Tensão Mínima:     300V DC
Tensão Máxima:     450V DC
```

### 5.3 Calibração

#### Calibração de Sensores Hall

```
Procedimento:
1. Desligar motor completamente
2. Menu "Calibração" → "Hall Sensor Calibration"
3. Rodar motor manualmente 10 rotações
4. Clicar "Auto-Detect Hall Phases"
5. Sistema mapeia eletronicamente as fases
```

#### Calibração de Shunt de Corrente

```
1. Menu "Calibração" → "Current Offset"
2. Desligar motor (I = 0)
3. Clicar "Zero Current"
4. Ler ADC offset (deve ser ≈2048 em 12-bit)
5. Salvar em EEPROM
```

---

## 6. CALIBRAÇÃO DE SENSORES

### 6.1 Verificação de Sensores Hall

**Teste com Osciloscópio:**

```
Expectativa de sinal:
  Frequência: f_hall = (RPM / 60) × 3  (3 impulsos/rotação)
  Amplitude: 0 → 5V (CMOS)
  Duty Cycle: ~50% (simétrico)
  Exemplo: 6000 RPM → 300 Hz
```

**Teste Manual:**

```
1. Conectar multímetro em modo frequência ao pino HALL_A
2. Rodar motor via acelerador
3. Ler frequência
4. Comparar com fórmula: f = (RPM/60) × 3
   Tolerance: ±5%
```

### 6.2 Verificação de Temperatura

```
Ambiente:     20 °C
Sem potência: NTC ≈ 20 °C (OK)
Com potência: NTC sobe ~1 °C/min até estabilização
Máximo operacional: 85 °C (firmware shutdown)
```

**Teste de Sensor:**

```
1. Desligar controladora
2. Desconectar NTC do ADC
3. Medir resistência com multímetro: ~4.7k Ω @ 25°C
4. Reconectar e verificar leitura ADC
```

### 6.3 Verificação de Shunt de Corrente

```
Sem carga:    I ≈ 0-2 A (marcha-lenta)
25% throttle: I ≈ 15-25 A
50% throttle: I ≈ 40-60 A
100% throttle: I ≈ 100-150 A
```

**Comparação Multímetro:**

```
1. Conectar amperímetro em série com negativo motor
2. Ligar controladora
3. Throttle progressivo
4. Comparar leitura com display (tolerance ±5%)
```

---

## 7. PROTEÇÕES E LIMITES

### 7.1 Proteção de Overcurrent

```
Limite Absoluto: 160 A (com margem de 10% acima máximo nominal)
Ação: Desabilitar PWM → motor coast (roda livre)
Recuperação: Automática quando I < 120 A
Histérese: 40 A (evita chatter)
```

### 7.2 Proteção Térmica

```
Aviso (Amarelo):   70 °C (reduz throttle max para 80%)
Limite Crítico:    85 °C (shutdown completo)
Recuperação:       Automática quando T < 75 °C
Monitoramento:     Dual sensor (heatsink + bobina)
```

### 7.3 Proteção de Tensão

```
Sob-tensão:  < 300V  → Desabilita drive
Sobre-tensão: > 450V → Ativa freio regenerativo (se disponível)
Recuperação:  Automática quando 300V < V < 450V
```

### 7.4 Limite de Corrente (Current Limit)

**Modo Soft-Limit (Recomendado):**

```
Limite Programável: 0 - 150 A
Ação: Reduzir velocidade proporcional (não desligar bruscamente)
Transição: Suave (não causa pico de corrente)
Uso: Proteção de componentes + conforto do veículo
```

---

## 8. INDICADORES DE ALARME

### 8.1 Semáforo de Status

| Cor | Estado | Significado | Ação |
|-----|--------|-------------|------|
| 🟢 Verde | NORMAL | Sistema OK, pronto | Operação normal |
| 🟡 Amarelo | AVISO | Temperatura elevada (70°C+) | Reduzir carga |
| 🔴 Vermelho | FALHA | Erro crítico (sensor, corrente) | Desligar imediatamente |
| ⚪ Branco | STANDBY | Controladora ativa, motor parado | Normal (sem ignição) |

### 8.2 Códigos de Erro

| Código | Erro | Causa Provável | Solução |
|--------|------|-----------------|---------|
| E001 | Hall Sensor Fault | Sensor desconectado/defeituoso | Verificar fiação Hall |
| E002 | Overcurrent | Corrente > 160 A | Reduzir carga |
| E003 | Overvoltage | Tensão > 450 V | Verificar fonte/regeneração |
| E004 | Undervoltage | Tensão < 300 V | Verificar bateria |
| E005 | Overtemperature | Temperatura > 85 °C | Aguardar resfriamento |
| E006 | Encoder Fault | CAN/comunicação perdida | Verificar conexão CAN |

---

## 9. TROUBLESHOOTING

### 9.1 Motor Não Inicia

```
Sintoma: Acelerador 100%, motor parado

Verificação:
□ Bateria conectada? (verificar voltage display)
□ Sensor Hall detectado? (verificar status verde)
□ Acelerador calibrado? (testar leitura ADC 0-5V)
□ Proteções ativadas? (verificar codes de erro)
□ Fiação trifásica correta? (medir continuidade)

Solução comum: Trocar ordem fase (U, V, W)
               Aguardar reset automático (~5s)
```

### 9.2 Motor Oscila / Instável

```
Sintoma: Vibração ou ruído audível (20-50 Hz)

Causa: Ganhos PID inadequados

Solução:
1. Reduzir Kp em 20%
2. Aumentar Kd em 50%
3. Verificar sensores Hall (ruído?)
4. Executar Auto-Aprendizado novamente
```

### 9.3 Corrente Muito Alta

```
Sintoma: I > 150 A mesmo em idle

Verificação:
□ Carga mecânica? (rodas travadas?)
□ Sensor Hall invertido? (causa saturação)
□ Bobinas com curto? (medir resistência U-V-W)
□ Gate driver defeituoso? (verificar PWM com osciloscópio)

Solução: Desligar imediatamente, revisar hardware
```

### 9.4 Temperatura Elevada

```
Sintoma: T > 70 °C sem carga pesada

Verificação:
□ Radiador limpo? (sem poeira/bloqueio)
□ Pasta térmica aplicada? (remover e reaplicar)
□ Fan de resfriamento (se presente)?
□ Ambiente quente (>35 °C)?

Solução: Limpeza + repaste térmica
         Aguardar 30 min resfriamento
```

### 9.5 Conexão Bluetooth Perdida

```
Sintoma: "API Indisponível" no app

Verificação:
□ Servidor HTTP rodando? (http://localhost:8000)
□ Firewall bloqueando? (liberar porta 8000)
□ WiFi conectada? (verificar SSID)

Solução:
1. Reiniciar servidor: python sim/server.py
2. Aguardar ~2 segundos
3. Reconectar app
4. Carregar URL em navegador
```

---

## 10. ESPECIFICAÇÕES TÉCNICAS

### 10.1 Especificações Elétricas

```
ENTRADA DC
  Tensão Nominal:        380 V DC
  Faixa Operacional:     300 - 450 V DC
  Corrente Máxima:       150 A contínua (200 A pico 10s)
  Potência Máxima:       120 kW

SAÍDA TRIFÁSICA (PWM)
  Freqência PWM:         20 kHz
  Tensão Fase-Fase:      0 - Vin
  Corrente Máxima/Fase:  150 A RMS
  Proteção Fase:         Fuse 175 A + MOSFET N-channel

ENTRADA SENSORES
  Sensores Hall (3x):    5V CMOS (50 ns pulso)
  Shunt de Corrente:     0.1 mΩ ±2% (1V max @ 150A)
  Sensores Temp (2x):    NTC 10k 3950K (±3°C)
  Throttle (0-5V):       12-bit ADC ±5mV
```

### 10.2 Especificações de Desempenho

```
CONTROLE
  Algoritmo:            FOC (Field Oriented Control)
  Frequência Loop:      10 kHz (100 µs)
  Tempo Latência:       <2 ms (sensor → PWM)
  Precisão RPM:         ±2% (uma vez calibrado)

PID (Padrão)
  Kp (Proporcional):    0.50 (ajustável 0.01 - 5.0)
  Ki (Integral):        0.10 (ajustável 0.001 - 1.0)
  Kd (Derivativo):      0.05 (ajustável 0.001 - 0.5)

AUTO-APRENDIZADO
  Método:               Astrom-Hagglund (relay tuning)
  Duração:              ~30 segundos
  Tolerância resultado: ±5% do calculado
```

### 10.3 Especificações de Proteção

```
TÉRMICO
  Dissipação Máxima:    170 W (heatsink 0.3 K/W)
  Limite Absoluto:      85 °C (semiconductor junction)
  Sensor Duplo:         Heatsink + bobina motor

ELÉTRICO
  Fuse DC+:             175 A
  TVS Clamp:            600 V bidirecional
  Discharge Resistor:   10k 10W

EMI/RFI
  Bootstrap Cap:        10 µF 50V per fase
  Gate Resistor:        10 Ω (reduz ringing)
  GND Plane:            Sólido em Layer 2 (4-layer PCB)
```

### 10.4 Especificações de Comunicação

```
BLUETOOTH LE 5.0
  MAC Address:          Inscrito EEPROM
  Características GATT:
    - RPM (read-only)      [0x0001]
    - Corrente (read-only)  [0x0002]
    - Temperatura (r/o)     [0x0003]
    - Tensão (read-only)    [0x0004]
    - Throttle (r/w)        [0x0005]
    - Kp, Ki, Kd (r/w)      [0x0006-0x0008]
    
  Período Notificação:  500 ms

HTTP (Simulador)
  URL Base:            http://localhost:8000
  Endpoint:            POST /api/simulate
  Formato:             JSON
  Timeout:             5 segundos
```

---

## APÊNDICE A: Wiring Diagram

```
                    ┌─────────────────────────────────┐
                    │    Controladora BLDC (ESP32)    │
                    │   ┌──────────────────────────┐  │
        B+ (400V) ──┤ J1                         │  │
        B- (GND) ──┤ J1                         │  │
    Throttle(0-5V)─┤ J2    ┌─────────────┐     │  │
  Ignition(12V) ──┤ J2    │ DRV8302     │     │  │
      Hall(5V) ───┤ J3    │ Gate Driver │ ───┤ P1│
      Hall(GND)───┤ J3    └─────────────┘     │  │
      HALL_A ────┤ J3      ↓     ↓     ↓      │  │
      HALL_B ────┤ J3      U     V     W      │  │
      HALL_C ────┤ J3    ┌──────────────────┐ │  │
    Shunt GND ───┤ J4    │  6x MOSFET       │ │  │
  Shunt Signal──┤ J4    │  IPP65R600P7    │ │  │
    Temp 1 ────┤ J4    │  Bridge 3-phase  │ │  │
    Temp 2 ────┤ J4    └──────────────────┘ │  │
    CAN_H ─────┤ J5      Heatsink 0.3K/W  │  │
    CAN_L ─────┤ J5                         │  │
                    └──────────────────────────┘  
                              ↓
                    ┌──────────────────┐
                    │  3x Phase Cables │
                    │  U, V, W @ 50A   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   Motor BLDC     │
                    │   120 kW, 6000   │
                    │   rpm nominal    │
                    └──────────────────┘
```

---

## APÊNDICE B: Parâmetros Padrão (Default)

```json
{
  "firmware_version": "FOC_v1.0.0",
  "control_frequency_hz": 10000,
  "pwm_frequency_hz": 20000,
  
  "pid_gains": {
    "kp": 0.50,
    "ki": 0.10,
    "kd": 0.05
  },
  
  "current_limits": {
    "max_continuous_a": 150,
    "max_peak_a": 200,
    "protection_threshold_a": 160
  },
  
  "temperature_limits": {
    "warning_c": 70,
    "critical_c": 85,
    "sensor_count": 2
  },
  
  "voltage_limits": {
    "min_v": 300,
    "nominal_v": 380,
    "max_v": 450
  },
  
  "sensors": {
    "hall_sensors": 3,
    "temperature_sensors": 2,
    "current_shunt_mohm": 0.1,
    "adc_bits": 12,
    "adc_sample_rate_khz": 100
  },
  
  "autolearn": {
    "method": "astrom_hagglund",
    "duration_seconds": 30,
    "enabled": true
  }
}
```

---

## APÊNDICE C: Contato e Suporte

```
Documentação:     https://github.com/controlmotor/wiki
Forum:            https://github.com/controlmotor/discussions
Issues:           https://github.com/controlmotor/issues
Versão Manual:    1.0 (2026-08-13)
Última Atualização: 2026-08-13
```

---

**Aviso de Segurança**: Este equipamento trabalha com 400V DC de alta potência. Sempre desligar bateria antes de manutenção. Contato inadequado pode resultar em choque elétrico, queimadura ou morte. Qualifique-se em alta tensão antes de operação.

