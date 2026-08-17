#!/usr/bin/env python3
"""
update_schematic_inline.py
Atualiza controlmotor-dual.html para:
1. Mover o CAD Studio Card para fora de #realMode, tornando-o visível em todos os modos.
2. Embutir o SVG industrial completo (esquema_profissional.svg) inline no cadCanvas.
3. Embutir as 5 folhas SVG diretamente em CAD_INLINE_SVGS no JavaScript para troca instantânea offline.
"""

import json

def main():
    with open('controlmotor-dual.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Ler os 5 SVGs
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

    # Extrair o bloco do cad-studio-card
    cad_start = html.find('<!-- CAD Schematic Studio Interativo -->')
    cad_end = html.find('</div>\n    </div>\n\n    <script>')
    
    if cad_start == -1 or cad_end == -1:
        print("Erro: Marcadores de CAD Studio não encontrados")
        return

    cad_block = html[cad_start:cad_end]

    # Remover o cad_block de dentro de realMode
    html_without_cad = html[:cad_start] + html[cad_end:]

    # Inserir o cad_block antes do fechamento de .container
    # Procurar o fim de realMode
    real_end_tag = '</div>\n    </div>\n\n    <script>'
    # No html_without_cad:
    # </div> fecha realMode, </div> fecha container
    # Vamos reestruturar:
    container_close_idx = html_without_cad.find('    </div>\n\n    <script>')
    
    # Criar o novo CAD Studio Card com SVG embutido inline no cadCanvas
    cad_block_inline = f"""        <!-- CAD Schematic Studio Interativo (Padrão Industrial IEEE) -->
        <div class="cad-studio-card" style="margin-top: 20px;">
            <div class="card-title" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span>⚡ Suíte Esquemática CAD Industrial (Padrão IEEE / Texas Instruments)</span>
                </div>
                <div class="cad-external-links">
                    <a href="cad_schematic_viewer.html" target="_blank" class="cad-ext-link">📑 Visualizador CAD Separado ↗</a>
                    <a href="circuit_interactive_bom.html" target="_blank" class="cad-ext-link">🔍 BOM Interativo Cross-Probe ↗</a>
                </div>
            </div>

            <!-- Navegação entre as 5 Folhas Esquemáticas -->
            <div class="cad-sheet-nav" id="cadSheetNav">
                <button class="cad-sheet-btn active" data-sheet="sheet5">🌟 Esquema Geral Industrial (Visão Panorâmica)</button>
                <button class="cad-sheet-btn" data-sheet="sheet1">1. Inversor Trifásico (6x IRFB4110)</button>
                <button class="cad-sheet-btn" data-sheet="sheet2">2. Gate Driver TI DRV8302</button>
                <button class="cad-sheet-btn" data-sheet="sheet3">3. Entrada DC & Chopper Freio</button>
                <button class="cad-sheet-btn" data-sheet="sheet4">4. MCU ESP32 & Sensores FOC</button>
            </div>

            <!-- CAD Viewport com Pan e Zoom -->
            <div class="cad-viewport-wrap" id="cadViewport" style="background: #ffffff; border-radius: 12px; border: 2px solid #334155; position: relative; overflow: hidden; height: 750px;">
                <div class="cad-canvas-inner" id="cadCanvas" style="width: 100%; height: 100%; transform-origin: 0 0; cursor: grab;">
{svg_prof}
                </div>

                <!-- Floating Zoom & Action Controls -->
                <div class="cad-controls-bar">
                    <button class="cad-tool-btn" id="btnCadZoomIn" title="Zoom In (+)">➕</button>
                    <button class="cad-tool-btn" id="btnCadZoomOut" title="Zoom Out (-)">➖</button>
                    <button class="cad-tool-btn" id="btnCadResetZoom" title="Reset Zoom (100%)">🔄</button>
                    <button class="cad-tool-btn" id="btnCadFullscreen" title="Tela Cheia">⛶</button>
                    <button class="cad-tool-btn" id="btnCadDownloadSvg" title="Baixar SVG da Folha">💾</button>
                </div>
            </div>

            <!-- Sheet Info & Specifications Banner -->
            <div class="cad-info-banner">
                <div class="cad-meta-text">
                    <span id="cadSheetTitle"><strong>Folha 5:</strong> Esquema Geral Industrial Integrado (Visão Panorâmica)</span><br>
                    <span id="cadSheetDesc" style="color: #94a3b8; font-size: 12px;">Diagrama industrial completo interligando todos os 5 estágios: Potência, Driver, Controle MCU, Freio e Alimentação Auxiliar.</span>
                </div>
            </div>
        </div>
"""

    html_new = html_without_cad[:container_close_idx] + cad_block_inline + html_without_cad[container_close_idx:]

    # Agora atualizar o bloco JS do CAD Studio Controller
    # Preparar dicionário JS das 5 folhas
    svg_dict = {
        'sheet1': svg_folha1,
        'sheet2': svg_folha2,
        'sheet3': svg_folha3,
        'sheet4': svg_folha4,
        'sheet5': svg_prof
    }
    svg_json = json.dumps(svg_dict)

    cad_js_old_start = html_new.find('// ==================== CAD SCHEMATIC STUDIO CONTROLLER ====================')
    cad_js_old_end = html_new.find('// ==================== INICIALIZAÇÃO GERAL DOS INTERVALOS ====================')

    if cad_js_old_start != -1 and cad_js_old_end != -1:
        new_cad_js = f"""// ==================== CAD SCHEMATIC STUDIO CONTROLLER ====================
        const CAD_INLINE_SVGS = {svg_json};

        const CAD_SHEETS = {{
            'sheet5': {{
                file: 'esquema_profissional.svg',
                title: 'Folha 5: Esquema Geral Industrial Integrado (Visão Panorâmica)',
                desc: 'Diagrama industrial completo interligando todos os 5 estágios: Potência, Driver, Controle MCU, Freio e Alimentação Auxiliar.'
            }},
            'sheet1': {{
                file: 'esquematico_folha1_inversor.svg',
                title: 'Folha 1: Inversor Trifásico de Alta Eficiência (6x IRFB4110 / 100V 180A)',
                desc: 'Topologia meia-ponte tripla com resistores de gate amortecidos, diodos bootstrap rápidos, snubbers RC e shunts Kelvin de 1mΩ 3W.'
            }},
            'sheet2': {{
                file: 'esquematico_folha2_driver.svg',
                title: 'Folha 2: Gate Driver TI DRV8302 & Condicionamento de Sinais',
                desc: 'Driver trifásico integrado com regulador Buck 5V, amplificadores de corrente shunt SO1/SO2 e proteções de sobrecorrente/subtensão.'
            }},
            'sheet3': {{
                file: 'esquematico_folha3_alimentacao.svg',
                title: 'Folha 3: Entrada DC, Proteção TVS, Pré-Carga & Chopper de Freio Reostático',
                desc: 'Conector XT90, fusível 50A, relé de pré-carga com resistor cerâmico, TVS 58V e chopper com MOSFET + R_brake de 100W.'
            }},
            'sheet4': {{
                file: 'esquematico_folha4_controle.svg',
                title: 'Folha 4: Microcontrolador ESP32-WROOM-32 & Transceiver CAN Isolado (ISO1050)',
                desc: 'Unidade central de processamento com 6 canais PWM de alta resolução, leituras ADC de corrente/tensão e barramento CAN isolado.'
            }}
        }};

        let cadScale = 1.0;
        let cadPanX = 0, cadPanY = 0;
        let cadIsDragging = false;
        let cadStartX = 0, cadStartY = 0;
        let activeSheet = 'sheet5';

        function loadCadSheet(sheetKey) {{
            activeSheet = sheetKey;
            const sheet = CAD_SHEETS[sheetKey] || CAD_SHEETS['sheet5'];
            
            const titleEl = document.getElementById('cadSheetTitle');
            if (titleEl) titleEl.innerHTML = `<strong>Folha ${{sheetKey.replace('sheet','')}}:</strong> ${{sheet.title}}`;
            const descEl = document.getElementById('cadSheetDesc');
            if (descEl) descEl.textContent = sheet.desc;

            document.querySelectorAll('#cadSheetNav .cad-sheet-btn').forEach(btn => {{
                if (btn.getAttribute('data-sheet') === sheetKey) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});

            const canvas = document.getElementById('cadCanvas');
            if (!canvas) return;

            // Carregamento instantâneo via memória interna (100% offline e sem restrição CORS)
            if (CAD_INLINE_SVGS[sheetKey]) {{
                canvas.innerHTML = CAD_INLINE_SVGS[sheetKey];
                applyCadTransform();
            }} else {{
                fetch(sheet.file)
                    .then(res => res.text())
                    .then(svgText => {{
                        canvas.innerHTML = svgText;
                        applyCadTransform();
                    }})
                    .catch(() => {{
                        canvas.innerHTML = `<img src="${{sheet.file}}" alt="${{sheet.title}}" style="width: 100%; height: auto; display: block;" />`;
                        applyCadTransform();
                    }});
            }}
        }}

        function applyCadTransform() {{
            const canvas = document.getElementById('cadCanvas');
            if (canvas) {{
                canvas.style.transform = `translate(${{cadPanX}}px, ${{cadPanY}}px) scale(${{cadScale}})`;
            }}
        }}

        document.querySelectorAll('#cadSheetNav .cad-sheet-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                loadCadSheet(btn.getAttribute('data-sheet'));
            }});
        }});

        const viewport = document.getElementById('cadViewport');
        if (viewport) {{
            viewport.addEventListener('mousedown', (e) => {{
                if (e.target.closest('.cad-controls-bar')) return;
                cadIsDragging = true;
                cadStartX = e.clientX - cadPanX;
                cadStartY = e.clientY - cadPanY;
                viewport.style.cursor = 'grabbing';
            }});

            window.addEventListener('mousemove', (e) => {{
                if (!cadIsDragging) return;
                cadPanX = e.clientX - cadStartX;
                cadPanY = e.clientY - cadStartY;
                applyCadTransform();
            }});

            window.addEventListener('mouseup', () => {{
                cadIsDragging = false;
                if (viewport) viewport.style.cursor = 'grab';
            }});

            viewport.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const delta = e.deltaY > 0 ? -0.1 : 0.1;
                cadScale = Math.min(4.0, Math.max(0.4, cadScale + delta));
                applyCadTransform();
            }});
        }}

        const btnZoomIn = document.getElementById('btnCadZoomIn');
        if (btnZoomIn) {{
            btnZoomIn.addEventListener('click', () => {{
                cadScale = Math.min(4.0, cadScale + 0.2);
                applyCadTransform();
            }});
        }}

        const btnZoomOut = document.getElementById('btnCadZoomOut');
        if (btnZoomOut) {{
            btnZoomOut.addEventListener('click', () => {{
                cadScale = Math.max(0.4, cadScale - 0.2);
                applyCadTransform();
            }});
        }}

        const btnResetZoom = document.getElementById('btnCadResetZoom');
        if (btnResetZoom) {{
            btnResetZoom.addEventListener('click', () => {{
                cadScale = 1.0;
                cadPanX = 0;
                cadPanY = 0;
                applyCadTransform();
            }});
        }}

        const btnFullscreen = document.getElementById('btnCadFullscreen');
        if (btnFullscreen && viewport) {{
            btnFullscreen.addEventListener('click', () => {{
                if (!document.fullscreenElement) {{
                    viewport.requestFullscreen().catch(err => {{
                        alert(`Erro ao entrar em tela cheia: ${{err.message}}`);
                    }});
                }} else {{
                    document.exitFullscreen();
                }}
            }});
        }}

        const btnDownloadSvg = document.getElementById('btnCadDownloadSvg');
        if (btnDownloadSvg) {{
            btnDownloadSvg.addEventListener('click', () => {{
                const sheet = CAD_SHEETS[activeSheet];
                const link = document.createElement('a');
                link.href = sheet.file;
                link.download = sheet.file;
                link.click();
            }});
        }}

        // Inicializar Folha 5 (Geral Industrial) por padrão
        loadCadSheet('sheet5');\n\n        """
        html_new = html_new[:cad_js_old_start] + new_cad_js + html_new[cad_js_old_end:]

    with open('controlmotor-dual.html', 'w', encoding='utf-8') as f:
        f.write(html_new)

    print("✅ controlmotor-dual.html atualizado com sucesso com todos os SVGs embutidos inline e visíveis em todos os modos!")

if __name__ == '__main__':
    main()
