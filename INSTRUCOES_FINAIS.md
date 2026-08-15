# 🚀 MOTORCONTROL v2.0 — Instruções Finais de Uso

**Data**: 2026-08-13  
**Status**: ✅ Pronto para começar  
**Tempo total**: <5 minutos para setup completo  

---

## ⚡ INÍCIO EM 3 PASSOS

### PASSO 1: Abrir dois Terminais

**Terminal A (Servidor)**:
```bash
cd /home/teste/controlmotor/sim
python3 server.py
```

Esperado: `Server listening on port 8000...`

**Terminal B (Seu computador)**: deixar aberto para testes

---

### PASSO 2: Abrir o Navegador

Escolha **uma** destas opções:

**Opção A** — Chrome/Firefox/Safari:
```
http://localhost:8000/controlmotor-premium.html
```

**Opção B** — Arquivo local:
```
Arrastar arquivo para navegador:
/home/teste/controlmotor/controlmotor-premium.html
```

**Opção C** — Linha de comando:
```bash
# Linux
xdg-open http://localhost:8000/controlmotor-premium.html

# macOS
open http://localhost:8000/controlmotor-premium.html

# Windows (WSL)
start http://localhost:8000/controlmotor-premium.html
```

---

### PASSO 3: Verificar Status

Você verá:

```
⚡ MotorControl        🟢 Conectado
```

✅ **Se verde** → Pronto para usar!  
❌ **Se vermelho** → Aguarde 2 segundos e recarregue (Ctrl+R)

---

## 📊 COMO USAR O DASHBOARD

### 1️⃣ Controlar Acelerador

**Ação**: Mover slider horizontalmente

```
Slider Throttle
│────●════════════│
0%     50%      100%
```

- Esquerda = 0% (parado)
- Meio = 50% (meia velocidade)
- Direita = 100% (máximo)

**Resultado**: Número grande (64px) muda em tempo real

---

### 2️⃣ Iniciar Simulação

**Ação**: Clicar botão "▶ Iniciar"

```
Antes: Status = "Parado"
Depois (1 segundo): Status = "Simulando..."
```

**O que acontece**:
- Telemetry cards começam atualizar (RPM, Corrente, Temp, Tensão)
- Gráfico começa desenhar 3 linhas (azul, rosa, âmbar)
- Progress bars animam
- Atualizações a cada 500ms (2 Hz)

---

### 3️⃣ Monitorar Telemetria

**4 Métricas aparecem**:

```
RPM: 3000-5000 rpm
├─ Mostrador grande (azul)
├─ Progress bar (0-10000 scale)
└─ Linha no gráfico (azul)

Corrente: 20-40 A
├─ Mostrador grande (rosa)
├─ Progress bar (0-150 scale)
└─ Linha no gráfico (rosa)

Temperatura: 30-50 °C
├─ Mostrador grande (âmbar)
├─ Progress bar (0-100 scale)
└─ Linha no gráfico (âmbar)

Tensão: 370-400 V
├─ Mostrador grande (indigo)
├─ Progress bar (300-450 scale)
└─ Série oculta (pode adicionar)
```

---

### 4️⃣ Ajustar Parâmetros PID (Opcional)

Cada slider controla comportamento do motor:

**Kp (Proporcional)** — 0.01 a 5.0
- ⬆️  Aumentar → Motor responde mais rápido
- ⬇️  Diminuir → Motor mais lento, mais estável

**Ki (Integral)** — 0.001 a 1.0
- ⬆️  Aumentar → Elimina erro de estado estacionário
- ⬇️  Diminuir → Pode ter erro

**Kd (Derivativo)** — 0.001 a 0.5
- ⬆️  Aumentar → Reduz overshoot, mais suave
- ⬇️  Diminuir → Mais oscilatório

**Valores padrão** (bom ponto de partida):
```
Kp = 0.50
Ki = 0.10
Kd = 0.05
```

---

### 5️⃣ Ativar Auto-Learn (Tuning Automático)

**Ação 1**: Toggle "Auto-Aprendizado"
```
[🔘] Auto-Aprendizado Astrom-Hagglund ← Click aqui
```

**Ação 2**: Clicar "🤖 Auto-Learn"

**O que acontece** (30-40 segundos):
- Status muda para "Auto-Tuning..."
- Motor simula acelerações/desacelerações
- Gráfico mostra padrão oscilatório
- Sliders Kp/Ki/Kd mudam automaticamente
- **Resultado**: Valores otimizados!

**Antes vs Depois**:
```
ANTES:  Kp=0.50 | Ki=0.10 | Kd=0.05
DEPOIS: Kp=?    | Ki=?    | Kd=?    (calculados automaticamente)
```

---

### 6️⃣ Parar Simulação

**Ação**: Clicar "⊘ Parar"

**Resultado**:
- Dados param de atualizar
- Status volta para "Parado"
- Throttle volta para 0%
- Gráfico congela (ainda visível)

---

## 🧪 TESTES RECOMENDADOS

### Teste 1: Conexão (30 segundos)

```bash
✅ Abrir interface
✅ Verificar badge verde "Conectado"
✅ Abrir DevTools (F12) — ver console sem erros
✅ Recarregar (Ctrl+R) — badge volta ao verde
```

**Resultado esperado**: ✅ API conectando corretamente

---

### Teste 2: Throttle Manual (1 minuto)

```bash
✅ Mover slider de 0% para 100%
✅ Observe o número grande (64px) mudar
✅ Slider retorna suavemente
✅ Valor atualiza instantaneamente
```

**Resultado esperado**: ✅ Controle responsivo

---

### Teste 3: Simulação Básica (2 minutos)

```bash
✅ Mover slider para 50%
✅ Clicar "▶ Iniciar"
✅ Aguardar 2 segundos
✅ Verificar telemetry cards atualizando
✅ Verificar gráfico desenhando linhas
✅ Clicar "⊘ Parar"
```

**Resultado esperado**:
```
RPM: 3000-5000
Corrente: 20-40A
Temperatura: 30-50°C
Gráfico: 3 linhas suaves
```

---

### Teste 4: Ajuste PID (3 minutos)

```bash
✅ Iniciar simulação (throttle 50%)
✅ Mover Kp para 0.8 (mais responsivo)
✅ Observar RPM mudança no gráfico
✅ Mover Ki para 0.2 (mais integração)
✅ Observar comportamento estabilizar
✅ Mover Kd para 0.1 (mais amortecimento)
✅ Observar overshoot reduzir
```

**Resultado esperado**: ✅ Mudanças visíveis em tempo real no gráfico

---

### Teste 5: Auto-Learn (40 segundos)

```bash
✅ Iniciar simulação (throttle 50%)
✅ Ativar toggle "Auto-Aprendizado"
✅ Clicar "🤖 Auto-Learn"
✅ Aguardar ~30 segundos
✅ Observar sliders Kp/Ki/Kd mudarem
✅ Auto-Learn completa
```

**Resultado esperado**: 
```
✅ Valores Kp/Ki/Kd otimizados automaticamente
✅ Motor com resposta melhorada
✅ Gráfico mais estável
```

---

## 🎯 CHECKLIST DE VALIDAÇÃO

Marque conforme testar:

```
SISTEMA
[ ] Python 3 instalado
[ ] Servidor.py encontrado
[ ] Interface Premium encontrada

SERVIDOR
[ ] Porta 8000 disponível
[ ] Servidor inicia sem erros
[ ] API responde (curl localhost:8000)

INTERFACE
[ ] Carrega em <1 segundo
[ ] Layout correto (cards visíveis)
[ ] Sem erros no console (F12)

CONEXÃO
[ ] Badge fica verde "Conectado"
[ ] Atualização indica "2 Hz"
[ ] Sem lag na interface

CONTROLE
[ ] Slider Throttle funciona
[ ] Valor exibido atualiza
[ ] Botões clicáveis (3 botões)

TELEMETRIA
[ ] RPM exibido (0-10000)
[ ] Corrente exibida (0-150A)
[ ] Temperatura exibida (0-100°C)
[ ] Tensão exibida (300-450V)
[ ] Progress bars animadas

SIMULAÇÃO
[ ] "▶ Iniciar" começa dados
[ ] Status muda para "Simulando"
[ ] Dados atualizam a cada 500ms
[ ] "⊘ Parar" para simulação

GRÁFICO
[ ] Chart.js carrega
[ ] 3 linhas desenhadas (azul, rosa, âmbar)
[ ] Atualiza suavemente (não choppy)
[ ] Eixos corretos

PID
[ ] Sliders funcionam
[ ] Valores atualizam instantaneamente
[ ] Auto-Learn toggle funciona
[ ] Auto-Learn muda valores

RESPONSIVIDADE
[ ] Desktop OK (2 colunas)
[ ] Tablet OK (1 coluna)
[ ] Mobile OK (touch)
[ ] Sem scroll horizontal
```

---

## 🚨 TROUBLESHOOTING RÁPIDO

| Problema | Solução |
|----------|---------|
| "API Offline" | `ps aux \| grep server.py` → reiniciar se não rodar |
| Sem dados | Clicar "▶ Iniciar" e aguardar 2s |
| Gráfico vazio | Recarregar página (Ctrl+R) |
| Sliders não funcionam | Recarregar página |
| Lento/travado | Fechar abas, usar Chrome, reduzir zoom |
| Badge vermelho | Aguardar 2s, recarregar página |

**Comando de debug rápido**:
```bash
# Ver se servidor roda
ps aux | grep server.py | grep -v grep

# Testar conexão
curl http://localhost:8000/

# Ver logs
tail -20 /tmp/motor_server.log

# Console browser (F12)
# → Console tab
# → Ver se há erros em vermelho
```

---

## 📊 DADOS ESPERADOS

### Em Repouso (Throttle 0%, Parado)
```
RPM:          0
Corrente:     0-2 A
Temperatura:  25-30 °C
Tensão:       370-400 V
```

### Com Throttle 50%, Simulando
```
RPM:          3000-5000
Corrente:     20-40 A
Temperatura:  40-55 °C
Tensão:       350-390 V
```

### Com Throttle 100%, Simulando
```
RPM:          7000-9000
Corrente:     80-120 A
Temperatura:  60-80 °C
Tensão:       320-370 V
```

### Com Auto-Learn (após 30s)
```
Kp:           0.01-1.0 (otimizado)
Ki:           0.001-0.3 (otimizado)
Kd:           0.001-0.1 (otimizado)
Resposta:     Mais suave e estável
```

---

## 💡 DICAS DE USO

1. **Começar simples**: 50% throttle, valores padrão Kp/Ki/Kd
2. **Observar gráfico**: Mudanças PID são visuais no Chart.js
3. **Auto-Learn ajuda**: Se não sabe como tunar, ativar auto-learn
4. **Testar extremos**: Throttle 0%, 50%, 100% para ver diferenças
5. **Responsividade**: Slider throttle muda instantaneamente
6. **Gráfico lag**: Se Chart.js lento, reduzir zoom do navegador
7. **Dark mode**: Sistema detecta preferência do SO (preto/branco)

---

## 🔗 ARQUIVOS DE REFERÊNCIA

```
Interface:     /home/teste/controlmotor/controlmotor-premium.html
Guia rápido:   /home/teste/controlmotor/GUIA_RAPIDO_INICIO.md
Manual:        /home/teste/controlmotor/MANUAL_USUARIO.md
Documentação:  /home/teste/controlmotor/INTERFACE_PREMIUM.md
Servidor:      /home/teste/controlmotor/sim/server.py
Simulador:     /home/teste/controlmotor/sim/bldc_full_simulator.py
```

---

## ✅ VOCÊ ESTÁ PRONTO!

1. ✅ Terminal A: `python3 server.py` (rodando)
2. ✅ Navegador: Abrir `http://localhost:8000/controlmotor-premium.html`
3. ✅ Badge: Verde "Conectado"
4. ✅ Mover slider e clicar "▶ Iniciar"
5. ✅ Observar dados em tempo real!

**🎉 Aproveite o MotorControl v2.0 Premium!**

