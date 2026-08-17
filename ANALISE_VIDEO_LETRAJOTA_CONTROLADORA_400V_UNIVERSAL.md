# ANÁLISE TÉCNICA E ESPECIFICAÇÃO DE ENGENHARIA: CONTROLADORA TRIFÁSICA 400V UNIVERSAL
> **Referência:** Vídeo *LetraJota — O UNO ELÉTRICO DE 200 CAVALOS SUPER PODEROSO CASEIRO* (`https://www.youtube.com/watch?v=qaykfUKs_mc`)  
> **Objetivo do Documento:** Extrair todas as lições práticas, limitações reveladas e requisitos de engenharia necessários para projetar, construir e parametrizar uma **Controladora / Inversor Trifásico de 400V Universal** (100% funcional para qualquer motor elétrico do mercado automotivo e industrial).

---

## 1. RESUMO EXECUTIVO E CONTEXTO DO VÍDEO DO LETRAJOTA

No projeto do **Uno Elétrico de 200 cv** do canal LetraJota, o criador realizou a conversão de um Fiat Uno utilizando um motor elétrico OEM moderno de tração automotiva retirado de um veículo de linha (**BYD Dolphin**, motor síncrono de ímãs permanentes internos - IPMSM).

### O Dilema Crítico Revelado no Vídeo:
1. **O Motor Original:** O motor elétrico do BYD Dolphin foi projetado por engenharia de fábrica para operar na faixa de alta tensão nominal de **300V a 400V DC**.
2. **A Limitação das Controladoras Genéricas:** No mercado DIY/conversão caseira acessível, a maioria das controladoras comerciais universais de baixo custo operam em baixa tensão (**60V, 72V ou 96V DC** — ex: Kelly, Sabvoton, FarDriver, Votol).
3. **O Conflito Físico da Contra-Eletromotriz (Back-EMF / $K_e$):**
   $$\text{Back-EMF: } V_{bemf} = K_e \cdot \omega_e$$
   Como o motor BYD de fábrica foi enrolado com muitas espiras por polo para gerar alto torque com tensão de 400V, sua constante $K_e$ é elevada. Ao alimentá-lo com apenas 72V–96V, a tensão contra-eletromotriz gerada pela rotação do rotor atinge a tensão da bateria em rotações muito baixas (ex: ~1.500 a 2.000 RPM). A partir desse ponto, a controladora não consegue mais forçar corrente para dentro das fases do motor, cessando a entrega de torque e potência.
4. **A Solução Drástica Adotada no Projeto (Rebobinagem):**
   Para conseguir girar o motor e extrair potência em baixa tensão com controladoras de 72V–96V e altíssima corrente (1500A de pico), a equipe do LetraJota foi forçada a **abrir o motor OEM, cortar todo o enrolamento de fábrica e rebobinar o estator do zero** com menos espiras e fios muito mais grossos em paralelo.
5. **Por que isso é um gargalo para conversões elétricas universais?**
   - Destrói a garantia e integridade mecânica/térmica de fábrica do motor OEM.
   - Risco extremo de curto-circuito entre fases ou fuga para a carcaça (queima do verniz e isolamento).
   - Perda do isolamento de classe H/N original e desbalanceamento de indutância entre fases.
   - Requer correntes absurdas no barramento de baixa tensão (800A a 1500A) para atingir a mesma potência ($P = V \cdot I$), gerando perdas Joule colossais ($I^2 R$), cabos de bitola monstruosa e superaquecimento extremo.

### A Conclusão de Engenharia:
A existência de uma **Controladora 400V Universal nativa** elimina 100% a necessidade de rebobinar motores! Ela permite ligar diretamente qualquer motor de tração OEM (BYD Dolphin, Nissan Leaf EM57, Tesla Model S/3/Y, BMW i3, Toyota Prius/Lexus MG2, QS Motor, Golden Motor, etc.) em seu estado original de fábrica com máxima eficiência, segurança e rendimento.

---

## 2. COMPARAÇÃO DE ENGENHARIA: BAIXA TENSÃO (72V) VS. ALTA TENSÃO (400V)

| Parâmetro | Sistema 72V Rebobinado (Bancada/LetraJota Inicial) | Sistema 400V Universal (Arquitetura Ideal) | Vantagem do Sistema 400V |
| :--- | :--- | :--- | :--- |
| **Tensão DC de Operação** | 60V – 96V DC | **300V – 450V DC (Suporta picos de 500V)** | Padrão automotivo global |
| **Potência Alvo (200 cv / 150 kW)** | $150.000\text{ W} / 72\text{ V} \approx \mathbf{2.083\text{ A}}$ | $150.000\text{ W} / 400\text{ V} = \mathbf{375\text{ A}}$ | **Redução de 5,5x na corrente!** |
| **Perdas por Efeito Joule ($I^2 R$)** | Proporcional a $(2083)^2 = 4.338.889$ | Proporcional a $(375)^2 = 140.625$ | **Perdas térmicas 30x menores nos cabos** |
| **Bitola dos Cabos de Fase** | $120\text{ mm}^2$ a $180\text{ mm}^2$ (duplos em paralelo) | $35\text{ mm}^2$ a $50\text{ mm}^2$ flexível automotivo | Muito mais leve, fácil de rotear e barato |
| **Necessidade de Rebobinar Motor** | **Sim (Obrigatório para atingir RPM)** | **NÃO (Plug & Play com motor de fábrica)** | Preserva 100% o motor original |
| **RPM Máximo Atingível** | Limitado pela relação $V_{bat} / K_e$ | Ampla faixa com **Field Weakening** (até 16.000 RPM) | Velocidade final e torque contínuo |
| **Eficiência Global do Inversor** | ~85% – 89% (devido a perdas de condução extremas) | **96.5% – 98.5% (com SiC MOSFETs/IGBTs automotivos)** | Maior autonomia e menor aquecimento |

---

## 3. ARQUITETURA DE HARDWARE DE UMA CONTROLADORA 400V UNIVERSAL

Para que uma controladora opere de forma 100% funcional em 400V com qualquer motor, ela deve conter os seguintes 8 blocos indispensáveis:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 BARRAMENTO HV (300V - 450V DC)          │
                  └───────────┬────────────────────────────────┬───────────┘
                              │                                │
                     ┌────────┴────────┐              ┌────────┴────────┐
                     │ Circuito Pré-   │              │ Banco Capacitores│
                     │ Carga + Fusível │              │ DC-Link Baixa L │
                     └────────┬────────┘              └────────┬────────┘
                              │                                │
 ┌────────────────────────────┼────────────────────────────────┼────────────────────────────┐
 │ ESTÁGIO DE POTÊNCIA (3-FASE)│                                │                            │
 │                            ▼                                ▼                            │
 │                   ┌──────────────────┐             ┌──────────────────┐                  │
 │                   │  Módulo SiC /    │             │ Chopper de Freio │                  │
 │                   │  IGBT 650V-1200V │             │ Dinâmico (Brake) │                  │
 │                   └────────┬─────────┘             └──────────────────┘                  │
 │                            │ U, V, W                                                     │
 └────────────────────────────┼─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Saída para Motor (BYD / Leaf / Tesla / Industrial)
                              │
 ┌────────────────────────────┼─────────────────────────────────────────────────────────────┐
 │ ISOLAMENTO GALVÂNICO & SENSORIAMENTO                                                     │
 │   - Gate Drivers Isolados com Proteção DESAT (UCC21710 / ISO5852S)                       │
 │   - Sensores de Corrente Fase Isolados por Efeito Hall (LEM / Shunt + AMC1301)           │
 │   - Divisores de Tensão HV com Isolamento e Detecção de Fuga                             │
 └────────────────────────────┬─────────────────────────────────────────────────────────────┘
                              │
 ┌────────────────────────────┴─────────────────────────────────────────────────────────────┐
 │ BLOCO DE CONTROLE DIGITAL & ALGORITMOS (Baixa Tensão 3.3V / 5V)                          │
 │   - MCU Principal: STM32G474 / STM32H7 / TI C2000 (FOC @ 20kHz, MTPA, Field Weakening)   │
 │   - Interface de Sensores Universal: Resolver (RDC), Hall Sensors, Encoder ABZ/BiSS      │
 │   - MCU Secundário / Telemetria: ESP32-S3 (WiFi, Bluetooth BLE, CAN, Interface Web/App)  │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. DETALHAMENTO DOS BLOCOS CRÍTICOS DE HARDWARE

### 4.1 Semicondutores de Potência (Chaveamento 400V)
- **Tensão Reversa Mínima:** 650V (para margem de transientes indutivos em barramento 400V); idealmente **1200V** para permitir SiC em alta velocidade de chaveamento.
- **Topologias Recomendadas:**
  1. **Opção Módulo Integrado (Padrão Automotivo):** Infineon HybridPACK 1 / HybridPACK Drive ou Semikron SKiiP (600V–1200V, 400A–800A).
  2. **Opção Componentes Discretos (Custo-Benefício Customizado):** 6x a 12x SiC MOSFETs em encapsulamento TO-247-4L (ex: Wolfspeed C3M0015065D ou STMicroelectronics SCT3030KL), $R_{ds(on)} \le 15\text{ m}\Omega$, permitindo frequências de PWM de 20 kHz a 40 kHz sem perdas térmicas excessivas.

### 4.2 Gate Drivers Isolados com Proteção de Hardware
- **Chips Recomendados:** TI `UCC21710`, TI `ISO5852S`, ou Infineon `1ED3122`.
- **Recursos Obrigatórios:**
  - **Isolamento Galvânico Reforçado:** Mínimo de 3.000 $V_{RMS}$ entre lado de alta tensão e baixa tensão do MCU.
  - **Proteção DESAT (Desaturação):** Detecta curto-circuito na fase em menos de **1.5 µs** e desliga o gate em rampa suave (Soft Turn-Off) para não estourar os transistores por sobretensão inductiva ($V = L \cdot di/dt$).
  - **Active Miller Clamp:** Evita auto-ligamento parasitário do transistor causado pelo elevado $dv/dt$ da fase oposta.
  - **UVLO (Under-Voltage Lockout):** Garante que o gate só comute se a tensão de acionamento estiver perfeita (+15V / -4V para SiC ou +15V / 0V para IGBT).

### 4.3 Barramento DC-Link de Baixa Indutância & Capacitores Film
- **Problema em 400V:** Indutância parasita no barramento gera picos de tensão destrutivos no chaveamento rápido ($V_{spike} = L_{bus} \cdot \frac{di}{dt}$).
- **Solução:**
  - Placa de barramento laminada (Laminated Busbar) ou PCB de 4 a 6 camadas com planos de $V_{DC+}$ e $V_{DC-}$ sobrepostos para cancelamento mútuo de campo magnético ($L_{bus} < 15\text{ nH}$).
  - Capacitores de filme de polipropileno de alta corrente de ripple (ex: 2x a 4x 470µF / 500V Epcos/TDK ou KEMET) em paralelo com capacitores cerâmicos SMD C0G/X7R de desacoplamento rápido de alta frequência.

### 4.4 Circuito de Pré-Carga (Pre-Charge) e Chopper de Freio
- **Pré-Carga:** Banco de capacitores descarregado a 400V age como um curto-circuito direto na bateria.
  - *Circuito:* Resistor de cerâmica bobinado (50 $\Omega$ a 100 $\Omega$ / 100W) alimentado por um contator auxiliar de pré-carga. O MCU monitora a tensão do DC-Link; quando atinge 95% da tensão da bateria, o contator principal HV (Gigavac/TE EV200) fecha e o de pré-carga desliga.
- **Brake Chopper (Freio Dinâmico):** Transistor de potência e resistor de dissipação de 400V acionados caso a bateria atinja o limite máximo de tensão durante frenagem regenerativa.

---

## 5. INTERFACE UNIVERSAL DE SENSORES DE ROTOR (COMPATIBILIDADE 100% MERCADO)

Um dos maiores erros de controladoras comuns é suportar apenas sensores Hall. Motores de ponta utilizam outras tecnologias:

```
                            MOTOR A SER CONTROLADO
                                       │
      ┌────────────────┬───────────────┴───────────────┬────────────────┐
      ▼                ▼                               ▼                ▼
   RESOLVER        SENSORES HALL                 ENCODER ÓPTICO/    SENSORLESS
 (BYD, Leaf,     (E-Bikes, Karts,               MAGNÉTICO (ABZ,    (Bombas, Fans,
  Tesla, Prius)   QS Motor, Bafang)              BiSS-C, SSI)       Fallback Seguro)
      │                │                               │                │
      ▼                ▼                               ▼                ▼
Chip Decodificador  GPIOs com Filtro RC +          Entrada QEP /      Algoritmo SMO /
RDC (AD2S1210 /    Optoacopladores Rápidos        SPI Isolada        Flux Observer
PGA411-Q1)                                                           no Firmware
      │                │                               │                │
      └────────────────┴───────────────┬───────────────┴────────────────┘
                                       ▼
                       ÂNGULO ELÉTRICO PRECISO ($\theta_e$)
                                       ▼
                   ALGORITMO FOC / PARKE & CLARKE TRANSFORM
```

1. **Resolver Automotivo (Indispensável para BYD, Leaf, BMW, Toyota):**
   - Transdutor rotativo eletromagnético com 1 enrolamento de excitação (senoidal ~10kHz) e 2 enrolamentos de saída (Seno e Cosseno).
   - Chip de interface: **Analog Devices AD2S1210** ou **TI PGA411-Q1**, convertendo sinais de seno/cosseno para ângulo absoluto de 10 a 16 bits de resolução.
2. **Sensores Hall Digitais (120° / 60°):**
   - Usado em motores de menor custo (QS Motor, Golden Motor). Entradas digitais com circuito de proteção, filtragem e debounce por hardware.
3. **Encoders Incrementais (Quadrature ABZ) e Absolutos (BiSS-C / SSI):**
   - Usado em servomotores industriais de precisão.
4. **Sensorless FOC (Sliding Mode Observer & Flux Observer):**
   - Estimação de $\theta_e$ por contra-eletromotriz e fluxo do estator para operação em caso de falha de sensor de posição.

---

## 6. CONTROLE E FIRMWARE: OS 4 PILARES DO CONTROLE UNIVERSAL

Para extrair 200 cv com eficiência máxima em qualquer tipo de motor:

### 6.1 FOC (Field Oriented Control / Controle Vetorial)
- Amostragem síncrona das correntes de fase nos shunts/sensores Hall de corrente.
- Transformada de Clarke: conversão de $I_a, I_b, I_c \rightarrow I_\alpha, I_\beta$.
- Transformada de Park: conversão para o referencial síncrono do rotor $\rightarrow I_d$ (eixo direto - fluxo) e $I_q$ (eixo em quadratura - torque).
- Dois controladores PI independentes regulando $I_d$ e $I_q$ em malha rápida (20 kHz / 50 µs).
- Modulação **SVPWM (Space Vector PWM)**: aproveitamento 15,5% superior do barramento DC em relação ao PWM senoidal tradicional.

### 6.2 MTPA (Maximum Torque Per Ampere)
- Em motores de ímãs internos (IPMSM como o BYD Dolphin), a indutância do eixo q é maior que a do eixo d ($L_q > L_d$), gerando **torque de relutância**:
  $$T_e = \frac{3}{2} p \left( \lambda_{pm} \cdot I_q + (L_d - L_q) \cdot I_d \cdot I_q \right)$$
- O algoritmo MTPA injeta uma corrente $I_d < 0$ calculada para maximizar o torque total para a menor corrente de fase possível, reduzindo o aquecimento em até 25%.

### 6.3 Field Weakening (Enfraquecimento de Campo para Alta Rotação)
- Quando a rotação atinge a velocidade base e o Back-EMF se iguala à tensão do barramento ($V_{max} \approx 400\text{V}$), o algoritmo de Field Weakening injeta uma corrente negativa profunda no eixo direto ($I_d \ll 0$) para desmagnetizar parcialmente o fluxo do estator.
- **Resultado:** Permite ao motor ultrapassar a rotação nominal e atingir rotações de 10.000 a 16.000 RPM sem corte brusco de potência.

### 6.4 Auto-Tuning & Identificação Automática de Parâmetros do Motor
- Rotina de calibração automática integrada no firmware para qualquer novo motor conectado:
  1. Medição de resistência de fase ($R_s$) por injeção de corrente DC.
  2. Medição de indutâncias $L_d$ e $L_q$ por pulsos de alta frequência.
  3. Medição do fluxo magnético dos ímãs ($\lambda_{pm}$) ou constante $K_v$ em rotação livre.
  4. Identificação do offset de montagem do sensor de posição (Resolver / Hall Zero Offset).

---

## 7. ESPECIFICAÇÃO COMPLETA DA CONTROLADORA 400V UNIVERSAL

### 7.1 Especificações Elétricas
- **Faixa de Tensão de Operação:** 150V a 450V DC (Nominal: 360V–400V DC).
- **Tensão Máxima Suportada (Chaves de Potência):** 650V / 1200V.
- **Corrente Contínua de Fase:** 250 $A_{RMS}$ (com arrefecimento líquido a 65°C).
- **Corrente de Pico de Fase (10 segundos):** **450A a 600A**.
- **Potência Contínua:** 100 kW (~136 cv).
- **Potência de Pico:** **160 kW a 200 kW (~217 cv a 270 cv)**.
- **Frequência de Chaveamento PWM:** 10 kHz a 30 kHz (configurável).
- **Frequência de Loop FOC:** 20 kHz (50 µs de tempo de ciclo).

### 7.2 Tipos de Motores Suportados
1. **IPMSM (Interior Permanent Magnet):** BYD Dolphin/Seal/Song, Nissan Leaf EM57/EM61, Tesla Model 3/Y PMSRM, Toyota Prius MG1/MG2, BMW i3.
2. **SPMSM (Surface Permanent Magnet):** QS Motor, Golden Motor, Motenergy, EMRAX.
3. **BLDC Trifásico:** E-bikes, karts e drones pesados.
4. **ACIM (Motor de Indução CA Trifásico):** Motores industriais e Tesla Model S/X dianteiros (indução).

### 7.3 Entradas, Saídas e Conectividade
- **CAN Bus:** 2x canais CAN isolados (CAN 2.0B / CAN-FD) para comunicação veicular, BMS e telemetria.
- **Entradas Analógicas:** 2x entradas de acelerador (0-5V com redundância e checagem de plausibilidade), 1x entrada de freio regenerativo variável.
- **Entradas de Temperatura:** 2x NTC/PT100/KTY84 (temperatura do motor e temperatura do inversor).
- **Conectividade Sem Fio:** Interface Web/App via Wi-Fi e Bluetooth BLE (ESP32-S3) para configuração gráfica em tempo real, telemetria e calibração.

---

## 8. PLANO DE AÇÃO E PRÓXIMOS PASSOS NO REPOSITÓRIO

1. **Schematic & PCB:**
   - Adicionar o esquemático em KiCad com os blocos de potência HV (SiC/IGBT), gate drivers isolados (UCC21710/ISO5852S) e chip RDC (AD2S1210).
2. **Firmware:**
   - Implementar os módulos de leitura de Resolver RDC e as equações de MTPA e Field Weakening no repositório de firmware (`firmware/src/`).
3. **Validação & Simulação:**
   - Criar bancada de testes e simulação SPICE para barramento de 400V com transitórios de chaveamento de alta velocidade.
