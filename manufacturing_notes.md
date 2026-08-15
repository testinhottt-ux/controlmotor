# Manufacturing Notes - Controlador PMSM/BLDC

## Especificações de PCB

- **Tamanho**: 150mm × 100mm (4 camadas, FR-4, 2oz Cu)
- **Espessura**: 1.6mm  
- **Acabamento**: HASL
- **Máscara de solder**: Verde
- **Serigrafia**: Branco
- **Via mínima**: 0.3mm drill / 0.5mm pad
- **Clearance mínimo**: 0.2mm
- **Trilha mínima**: 10mil (0.254mm) para I > 10A

## Componentes Críticos

### MOSFETs Q1-Q6 (TO-247)
- Dissipação: ~170W @ 50A
- Heatsink: Al 300×200×10mm (0.3K/W)
- Vias térmicas: ~200 unidades por MOSFET

### Capacitores Bulk C1-C2 (470µF 450V)
- ESR máximo: 20mΩ (estabilidade)
- Localização: próximo XT60 (<50mm)

### Sensores Hall A/B/C
- Tensão: 5V referenciado
- Fio: ≤1m (minimizar EMI)

## Testes

1. **Continuidade**: Multímetro VCC-GND
2. **Polaridade**: XT60 verificar +400V
3. **Isolamento**: Mega-ohm meter >1MΩ
4. **Funcionamento**: Com firmware (PWM + Hall)

## Reflow

- Temperatura: 240-260°C
- Pico: <260°C  
- Tempo: <60s acima de 217°C

---
**Versão**: 1.0 | **Data**: 2026-08-14 | **Status**: Pronto
