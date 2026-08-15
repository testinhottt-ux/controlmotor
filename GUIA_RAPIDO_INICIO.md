# MotorControl — Guia Rápido de Início

**Status**: 🟢 Pronto para usar  
**Data**: 2026-08-13  
**Tempo de setup**: <2 minutos  

---

## 🚀 INÍCIO RÁPIDO (5 passos)

### 1. Abrir Terminal

```bash
cd /home/teste/controlmotor
```

### 2. Iniciar Servidor

```bash
cd sim && python3 server.py
# Esperado: "Server listening on port 8000..."
```

### 3. Abrir Navegador (Nova Aba/Janela)

```bash
# Opção A: Chrome
google-chrome http://localhost:8000/controlmotor-premium.html

# Opção B: Firefox
firefox http://localhost:8000/controlmotor-premium.html

# Opção C: Safari
open -a Safari http://localhost:8000/controlmotor-premium.html

# Opção D: Arquivo local
open /home/teste/controlmotor/controlmotor-premium.html
```

### 4. Verificar Status

Badge no topo deve ficar **verde** "Conectado" em 1-2 segundos

### 5. Começar a Testar

Mover slider throttle → Clicar "▶ Iniciar" → Ver dados em tempo real

---

## 📊 DASHBOARD EXPLICADO

### Header (Topo)
```
⚡ MotorControl          🟢 Conectado (2 Hz)
Logo (gradient)          Status badge (pulse animation)
```

**O que significa**:
- 🟢 Verde = API respondendo
- 🔴 Vermelho = Erro de conexão
- ⚪ Branco = Aguardando conexão

---

### Painel 1: Controle (Esquerda)

```
🎮 CONTROLE
┌─────────────────────────┐
│                         │
│    64                   │  ← Valor throttle (0-100)
│                         │
├─────────────────────────┤
│ [════════════════════]  │  ← Slider (arraste para esquerda/direita)
│ 0%        50%      100% │
├─────────────────────────┤
│ ▶ Iniciar  | 🤖 Auto-Learn  | ⊘ Parar  │
├─────────────────────────┤
│ 💡 Dica: Use o controle deslizante... │
└─────────────────────────┘
```

**Como usar**:
1. Mover slider para 0-100% (esquerda para direita)
2. Clicar "▶ Iniciar" para começar simulação
3. Monitorar telemetria (painel direita)
4. Ajustar parâmetros PID (painel inferior)
5. Clicar "⊘ Parar" para parar

---

### Painel 2: Telemetria (Direita)

```
📊 TELEMETRIA
┌──────┬──────────┐
│ RPM  │ Corrente │
│5000  │   42 A   │
│[███] │  [███]   │
├──────┼──────────┤
│ Temp │ Tensão   │
│ 48°C │  382 V   │
│[███] │  [███]   │
└──────┴──────────┘
```

**Métricas em tempo real** (atualizam a cada 500ms):
- **RPM**: Rotações por minuto (0-10000)
- **Corrente**: Amperes (0-150A)
- **Temperatura**: Celsius (0-100°C)
- **Tensão**: Volts DC (300-450V)

As barras mostram progresso visual (preenchimento proporcional ao máximo)

---

### Painel 3: Histórico (Gráfico)

```
📈 HISTÓRICO (últimos 60s)
┌─────────────────────────────────┐
│                                 │
│  ████  ↗ Série 1: RPM (azul)   │
│  ░░░░  ↗ Série 2: Corrente      │
│  ▓▓▓▓  ↗ Série 3: Temperatura   │
│                                 │
│ 10:00  10:15  10:30  10:45 10:60│
└─────────────────────────────────┘
```

**O que vê**:
- **Linha azul**: RPM (eixo Y esquerda, 0-10000)
- **Linha rosa**: Corrente (eixo Y meio, 0-150A)
- **Linha âmbar**: Temperatura (eixo Y direita, 0-100°C)
- **X**: Tempo (últimos 60 segundos)

Atualiza **suavemente** a cada 500ms

---

### Painel 4: Parâmetros PID (Inferior)

```
⚙️ PARÂMETROS PID
┌────────────────────────────────────────────┐
│ Proporcional (Kp)     [████████░░] 0.50   │
│ Min: 0.01 | Max: 5.00                     │
│                                            │
│ Integral (Ki)         [███░░░░░░░░] 0.10  │
│ Min: 0.001 | Max: 1.00                    │
│                                            │
│ Derivativo (Kd)       [██░░░░░░░░░] 0.05  │
│ Min: 0.001 | Max: 0.50                    │
│                                            │
│ [🔘 Auto-Aprendizado Astrom-Hagglund]    │
│                                            │
│ 📋 Tuning: Kp controla resposta...        │
└────────────────────────────────────────────┘
```

**Como ajustar**:
1. Arrastar slider Kp (resposta rápida)
2. Arrastar slider Ki (elimina erro)
3. Arrastar slider Kd (reduz overshoot)
4. Clicar toggle "Auto-Aprendizado" para tuning automático
5. Valores atualizam instantaneamente

---

## 🧪 TESTES (5 Cenários)

### Teste 1: Conexão Básica

```
✅ Esperado: Badge fica verde "Conectado"
⏱️  Tempo: <2 segundos
🔍 Verificar: F12 → Console (sem erros)
```

**Passos**:
1. Abrir página
2. Aguardar 2 segundos
3. Verificar badge no topo

---

### Teste 2: Throttle Manual

```
✅ Esperado: 
   - Slider move suavemente (0-100%)
   - Valor exibido atualiza
   - Display grande muda em tempo real
⏱️  Tempo: imediato
```

**Passos**:
1. Mover slider lentamente (esquerda → direita)
2. Ver valor mudar de 0 → 100
3. Display grande (64px) atualiza

**Resultado**: Slider responde instantaneamente

---

### Teste 3: Iniciar Simulação

```
✅ Esperado:
   - Status muda para "Simulando..."
   - Métricas começam atualizar
   - Gráfico começa desenhar linha
   - Animação suave
⏱️  Tempo: <1 segundo
```

**Passos**:
1. Mover throttle para 50%
2. Clicar "▶ Iniciar"
3. Observar telemetry cards
4. Observar gráfico (Chart.js)

**Resultado esperado**:
```
RPM: ~3000-5000
Corrente: ~20-40A
Temperatura: ~30-50°C
Tensão: ~370-400V
```

---

### Teste 4: Ajustar PID

```
✅ Esperado:
   - Sliders respondem instantaneamente
   - Valores exibidos atualizam
   - Gráfico mostra mudança de comportamento
⏱️  Tempo: imediato + 2-3 segundos para ver efeito
```

**Passos**:
1. Com simulação rodando, clicar "▶ Iniciar" (já rodando)
2. Mover slider Kp para 0.8 (mais responsivo)
3. Observar RPM mudar no gráfico
4. Mover slider Ki para 0.2 (mais integração)
5. Observar erro de estado estacionário reduzir
6. Mover slider Kd para 0.1 (mais amortecimento)
7. Observar overshoot reduzir

**Resultado**: Gráfico muda comportamento em <1s

---

### Teste 5: Auto-Learn

```
✅ Esperado:
   - Toggle ativa
   - Status muda para "Auto-Tuning..."
   - Sliders Kp, Ki, Kd mudam automaticamente
   - Motor simula acelerações/desacelerações
⏱️  Tempo: 30-40 segundos
```

**Passos**:
1. Com simulação rodando, clicar "🤖 Auto-Learn"
2. Ou: clicar toggle "Auto-Aprendizado" + "▶ Iniciar"
3. Aguardar ~30 segundos
4. Observar valores Kp, Ki, Kd mudarem
5. Gráfico mostra padrão de teste (oscilatório)
6. Auto-Learn completa, valores estabilizam

**Resultado**: 
```
Antes:  Kp=0.50 | Ki=0.10 | Kd=0.05
Depois: Kp=? | Ki=? | Kd=?  (valores otimizados)
```

---

## 🔧 TROUBLESHOOTING

### Problema 1: "API Offline"

**Sintoma**: Badge vermelho "Erro de Conexão"

**Solução**:
```bash
# 1. Verificar se servidor está rodando
ps aux | grep "python3 server.py" | grep -v grep

# 2. Se não estiver, iniciar
cd /home/teste/controlmotor/sim
python3 server.py

# 3. Testar conexão
curl http://localhost:8000/

# 4. Recarregar página (Ctrl+R / Cmd+R)
```

---

### Problema 2: Gráfico não atualiza

**Sintoma**: Chart vazio, sem linhas

**Solução**:
```bash
# 1. Clicar "▶ Iniciar"
# 2. Esperar 2-3 segundos
# 3. Verificar console (F12)
# 4. Se erro, recarregar página
# 5. Tentar novamente
```

---

### Problema 3: Sliders não funcionam

**Sintoma**: Mover slider não faz nada

**Solução**:
```bash
# 1. Recarregar página (Ctrl+R)
# 2. Limpar cache (Ctrl+Shift+Del)
# 3. Testar em outro navegador
# 4. Verificar console (F12) para erros
```

---

### Problema 4: Interface lenta/travada

**Sintoma**: Animações não suaves, interface congela

**Solução**:
```bash
# 1. Fechar abas desnecessárias
# 2. Aumentar zoom (Ctrl+Menos) para reduzir overhead
# 3. Usar Chrome (melhor performance)
# 4. Reiniciar navegador
# 5. Testar em máquina menos carregada
```

---

## 📱 TESTAR EM MOBILE

### iOS (iPhone/iPad)

```bash
1. Na mesma rede WiFi
2. Encontrar IP do servidor:
   ifconfig | grep "inet "
   # Exemplo: 192.168.1.100

3. No Safari do iPhone:
   http://192.168.1.100:8000/controlmotor-premium.html

4. Verificar responsividade
   - Landscape vs Portrait
   - Touch funciona?
   - Gráfico redimensiona?
```

### Android (Chrome Mobile)

```bash
1. Na mesma rede WiFi
2. No Chrome do Android:
   http://192.168.1.100:8000/controlmotor-premium.html

3. Verificar:
   - Sliders funcionam ao toque?
   - Botões apertam corretamente?
   - Gráfico responsivo?
```

---

## 🎯 CHECKLIST DE VALIDAÇÃO

Marque conforme testar:

```
CONEXÃO
[ ] Badge mostra "Conectado" (verde)
[ ] Console sem erros (F12)
[ ] API responde (curl localhost:8000)

CONTROLE
[ ] Slider throttle move (0-100%)
[ ] Valor exibido atualiza
[ ] Botões clicáveis

SIMULAÇÃO
[ ] "▶ Iniciar" começa dados
[ ] Status muda para "Simulando"
[ ] Métricas atualizam a cada 500ms
[ ] Gráfico desenha linhas

TELEMETRIA
[ ] RPM exibido (0-10000)
[ ] Corrente exibida (0-150A)
[ ] Temperatura exibida (0-100°C)
[ ] Tensão exibida (300-450V)
[ ] Progress bars animadas

GRÁFICO
[ ] Chart.js carrega
[ ] 3 linhas visíveis (azul, rosa, âmbar)
[ ] Atualiza suavemente
[ ] Eixos corretos

PID TUNING
[ ] Sliders Kp/Ki/Kd funcionam
[ ] Valores atualizam
[ ] Auto-Learn toggle funciona
[ ] Info box exibida

RESPONSIVIDADE
[ ] Desktop: 2 colunas OK
[ ] Tablet: 1 coluna OK
[ ] Mobile: touch-friendly OK
[ ] Sem scroll horizontal

PERFORMANCE
[ ] Load time <1s
[ ] 60fps animações
[ ] Sem lag ao mover sliders
[ ] Memory ~50MB
```

---

## 📞 SUPORTE RÁPIDO

| Problema | Solução |
|----------|---------|
| API offline | `ps aux \| grep server.py` → reiniciar |
| Sem dados | Clicar "▶ Iniciar" |
| Gráfico vazio | Recarregar (Ctrl+R) |
| Lento | Fechar abas, usar Chrome |
| Mobile | Usar WiFi, IP local |

---

## 🔗 LINKS ÚTEIS

```
Interface:  http://localhost:8000/controlmotor-premium.html
Arquivo:    /home/teste/controlmotor/controlmotor-premium.html
Docs:       INTERFACE_PREMIUM.md
Manual:     MANUAL_USUARIO.md
API:        http://localhost:8000/ (GET para docs)
Servidor:   /home/teste/controlmotor/sim/server.py
Simulador:  /home/teste/controlmotor/sim/bldc_full_simulator.py
```

---

## ⏱️ TEMPOS ESPERADOS

```
Inicialização servidor: <1s
Primeira conexão:       <2s
Atualização dados:      500ms (2 Hz)
Gráfico update:         300ms smooth
Slider response:        imediato
Auto-Learn:             30-40s
```

---

**🎉 Pronto! Agora abra a interface e comece a testar!**

