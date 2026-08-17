#!/usr/bin/env python3
"""
sync_all_schematics.py
Sincroniza todos os 5 arquivos SVG no controlmotor-dual.html, garantindo que o SVG inline inicial
e o dicionário CAD_INLINE_SVGS contenham a versão mais recente com todas as conexões completas.
"""

import json
import re

def sync():
    with open('esquema_profissional.svg', 'r', encoding='utf-8') as f:
        svg_prof = f.read()
    with open('esquematico_folha1_inversor.svg', 'r', encoding='utf-8') as f:
        svg_folha1 = f.read()
    with open('esquematico_folha2_driver.svg', 'r', encoding='utf-8') as f:
        svg_folha2 = f.read()
    with open('esquematico_folha3_alimentacao.svg', 'r', encoding='utf-8') as f:
        svg_folha3 = f.read()
    with open('esquematico_folha4_controle.svg', 'r', encoding='utf-8') as f:
        svg_folha4 = f.read()

    with open('controlmotor-dual.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Substituir o SVG inline no cadCanvas
    canvas_start = html.find('<div class="cad-canvas-inner" id="cadCanvas"')
    if canvas_start != -1:
        canvas_open_end = html.find('>', canvas_start) + 1
        canvas_close = html.find('</div>\n\n                <!-- Floating Zoom', canvas_open_end)
        if canvas_close != -1:
            html = html[:canvas_open_end] + "\n" + svg_prof + "\n                " + html[canvas_close:]

    # 2. Substituir o dicionário CAD_INLINE_SVGS no JavaScript
    svg_dict = {
        'sheet1': svg_folha1,
        'sheet2': svg_folha2,
        'sheet3': svg_folha3,
        'sheet4': svg_folha4,
        'sheet5': svg_prof
    }
    svg_json = json.dumps(svg_dict)

    js_marker = 'const CAD_INLINE_SVGS = '
    js_start = html.find(js_marker)
    if js_start != -1:
        js_end = html.find(';\n\n        const CAD_SHEETS =', js_start)
        if js_end != -1:
            html = html[:js_start + len(js_marker)] + svg_json + html[js_end:]

    with open('controlmotor-dual.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ controlmotor-dual.html sincronizado com os 5 esquemáticos atualizados!")

if __name__ == '__main__':
    sync()
