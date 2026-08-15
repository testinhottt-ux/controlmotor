# JLCPCB Submission Checklist

## Arquivos Gerber Necessários

- [ ] layout-F.Cu.gbr (cobre superior)
- [ ] layout-B.Cu.gbr (cobre inferior)
- [ ] layout-F.Mask.gbr (máscara solder superior)
- [ ] layout-B.Mask.gbr (máscara solder inferior)
- [ ] layout-F.Silks.gbr (serigrafia superior)
- [ ] layout-B.Silks.gbr (serigrafia inferior)
- [ ] layout-Edge.Cut.gbr (contorno)

## Arquivo de Furação

- [ ] layout.drl (ou .xln)

## BOM

- [ ] BOM.csv revisado
- [ ] Colunas: Reference, Value, Footprint, Qty, Supplier, Supplier SKU

## Pick & Place

- [ ] pos_file.csv (coordenadas X/Y/Rotação)

## Configurações JLCPCB

Recomendado:
- Tipo: FR-4 2-layer (ou 4-layer)
- Espessura: 1.6mm
- Cobre: 1oz (padrão)
- Máscara: Verde
- Serigrafia: Branco
- Acabamento: HASL
- QA: Habilitado

## Teste de Upload

Após gerar todos os arquivos:

```bash
# Compactar
zip -r controlador_pmsm_gerbers.zip gerbers/ BOM.csv pos_file.csv

# Upload em https://jlcpcb.com
# - Click "Quote"
# - Selecionar arquivo ZIP
# - Verificar preview (cores, camadas)
# - Aceitar e pagar
```

## Timeline

- Fabricação: 7-10 dias
- Envio: 3-7 dias (depende do frete)
- Recebimento: Testar com firmware

---
**Preparado por**: OpenCode AG3  
**Data**: 2026-08-14
