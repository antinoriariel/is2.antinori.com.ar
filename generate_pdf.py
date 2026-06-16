#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera public/downloads/zero_trust_paper.pdf
desde zero_trust_arquitectura_confianza_cero.md usando reportlab.

Requiere: pip install reportlab

Uso: python generate_pdf.py
"""

import re
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, Preformatted
)

# ── Rutas ──────────────────────────────────────────────────────────────────
INPUT_FILE = Path("zero_trust_arquitectura_confianza_cero.md")
OUTPUT_PDF = Path("public/downloads/zero_trust_paper.pdf")

# ── Colores ────────────────────────────────────────────────────────────────
NAVY     = colors.Color(0/255, 70/255, 127/255)
DKGRAY   = colors.Color(0.35, 0.35, 0.35)
MDGRAY   = colors.Color(0.55, 0.55, 0.55)
LGRAY_BG = colors.Color(0.96, 0.96, 0.96)

# ── Contenidos fijos ───────────────────────────────────────────────────────
ABSTRACT = (
    "La Arquitectura de Confianza Cero (Zero Trust Architecture, ZTA) representa "
    "un cambio paradigmático en el diseño de sistemas de seguridad para aplicaciones distribuidas. "
    "Bajo la premisa de que ninguna entidad—usuario, servicio o dispositivo—debe recibir confianza "
    "implícita por su ubicación de red, ZTA impone verificación explícita, mínimo privilegio y "
    "monitoreo continuo en cada capa del sistema. Este documento analiza sistemáticamente los "
    "fundamentos teóricos, los componentes técnicos y los patrones de implementación de ZTA en "
    "arquitecturas de microservicios, abordando tecnologías clave como SPIFFE/SPIRE, mTLS, "
    "OAuth 2.0, OpenID Connect, Open Policy Agent (OPA) y service meshes. Se discuten los desafíos "
    "operativos, casos de adopción industrial y tendencias emergentes incluyendo la integración con "
    "inteligencia artificial, entornos multi-nube y criptografía post-cuántica."
)

KEYWORDS = (
    "<b>Palabras clave:</b> Zero Trust Architecture (ZTA), microservicios, mTLS, SPIFFE/SPIRE, "
    "OAuth 2.0, OpenID Connect, Open Policy Agent, service mesh, microsegmentación, "
    "autenticación continua, DevSecOps."
)


# ── Estilos ────────────────────────────────────────────────────────────────
def build_styles():
    B = 11  # base font size
    return dict(
        normal=ParagraphStyle(
            'Normal', fontName='Times-Roman', fontSize=B, leading=B * 1.5,
            alignment=TA_JUSTIFY, spaceAfter=5, textColor=colors.black),
        h2=ParagraphStyle(
            'H2', fontName='Times-Bold', fontSize=14, leading=18,
            textColor=NAVY, spaceBefore=22, spaceAfter=4),
        h3=ParagraphStyle(
            'H3', fontName='Times-Bold', fontSize=12, leading=16,
            textColor=colors.black, spaceBefore=12, spaceAfter=2),
        h4=ParagraphStyle(
            'H4', fontName='Times-BoldItalic', fontSize=11, leading=15,
            textColor=DKGRAY, spaceBefore=8, spaceAfter=2),
        bullet=ParagraphStyle(
            'Bullet', fontName='Times-Roman', fontSize=B, leading=B * 1.4,
            alignment=TA_JUSTIFY, leftIndent=16, spaceAfter=2,
            textColor=colors.black),
        enum_item=ParagraphStyle(
            'EnumItem', fontName='Times-Roman', fontSize=B, leading=B * 1.4,
            alignment=TA_JUSTIFY, leftIndent=22, spaceAfter=2,
            textColor=colors.black),
        blockquote=ParagraphStyle(
            'Blockquote', fontName='Times-Italic', fontSize=10, leading=14,
            alignment=TA_JUSTIFY, leftIndent=18, rightIndent=18,
            spaceAfter=4, spaceBefore=4, textColor=DKGRAY),
        code=ParagraphStyle(
            'Code', fontName='Courier', fontSize=8.5, leading=11,
            leftIndent=16, spaceAfter=6, spaceBefore=6,
            backColor=LGRAY_BG, textColor=colors.black),
        cover_inst=ParagraphStyle(
            'CovInst', fontName='Times-Roman', fontSize=10, leading=14,
            alignment=TA_CENTER, textColor=MDGRAY, spaceAfter=3),
        cover_title=ParagraphStyle(
            'CovTitle', fontName='Times-Bold', fontSize=22, leading=27,
            alignment=TA_CENTER, textColor=NAVY, spaceBefore=18, spaceAfter=10),
        cover_subtitle=ParagraphStyle(
            'CovSub', fontName='Times-Italic', fontSize=13, leading=18,
            alignment=TA_CENTER, textColor=DKGRAY, spaceAfter=24),
        cover_author=ParagraphStyle(
            'CovAuth', fontName='Times-Bold', fontSize=12, leading=16,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=3),
        cover_meta=ParagraphStyle(
            'CovMeta', fontName='Times-Roman', fontSize=10, leading=14,
            alignment=TA_CENTER, textColor=MDGRAY, spaceAfter=2),
        abs_title=ParagraphStyle(
            'AbsTitle', fontName='Times-Bold', fontSize=11, leading=15,
            alignment=TA_CENTER, spaceAfter=5),
        abs_body=ParagraphStyle(
            'AbsBody', fontName='Times-Italic', fontSize=10, leading=14,
            alignment=TA_JUSTIFY, leftIndent=1 * cm, rightIndent=1 * cm,
            spaceAfter=4),
        keywords=ParagraphStyle(
            'Keywords', fontName='Times-Roman', fontSize=10, leading=14,
            alignment=TA_JUSTIFY, leftIndent=1 * cm, rightIndent=1 * cm,
            spaceAfter=4),
    )


# ── Conversión markdown inline → XML de reportlab ─────────────────────────
def _xml_esc(text: str) -> str:
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


_INLINE_RE = re.compile(
    r'`([^`]+)`'                     # grupo 1: código inline
    r'|\*\*\*(.+?)\*\*\*'            # grupo 2: bold+italic
    r'|\*\*(.+?)\*\*'                # grupo 3: bold
    r'|\*([^*\n]+?)\*'               # grupo 4: italic *
    r'|_([^_\n]+?)_'                 # grupo 5: italic _
    r'|\[([^\]]*)\]\(([^)]*)\)',     # grupo 6+7: link
)


def md_inline(text: str) -> str:
    """Convierte formato inline markdown a XML de reportlab."""
    result = []
    last = 0
    for m in _INLINE_RE.finditer(text):
        result.append(_xml_esc(text[last:m.start()]))
        last = m.end()
        if m.group(1) is not None:
            result.append(f'<font name="Courier" size="9">{_xml_esc(m.group(1))}</font>')
        elif m.group(2) is not None:
            result.append(f'<b><i>{_xml_esc(m.group(2))}</i></b>')
        elif m.group(3) is not None:
            result.append(f'<b>{_xml_esc(m.group(3))}</b>')
        elif m.group(4) is not None:
            result.append(f'<i>{_xml_esc(m.group(4))}</i>')
        elif m.group(5) is not None:
            result.append(f'<i>{_xml_esc(m.group(5))}</i>')
        else:  # link — mostrar solo el texto
            result.append(_xml_esc(m.group(6)))
    result.append(_xml_esc(text[last:]))
    return ''.join(result)


# ── Cabecera / pie de página ───────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    ml, mr = doc.leftMargin, doc.rightMargin

    canvas.setFont('Times-Italic', 7.5)
    canvas.setFillColor(MDGRAY)
    canvas.drawString(ml, h - 1.25 * cm,
                      'Zero Trust Architecture — Confianza Cero en Microservicios')
    canvas.drawRightString(w - mr, h - 1.25 * cm, 'Ariel Antinori · UNNE')

    canvas.setStrokeColor(colors.Color(0.75, 0.75, 0.75))
    canvas.setLineWidth(0.3)
    canvas.line(ml, h - 1.5 * cm, w - mr, h - 1.5 * cm)

    canvas.setFont('Times-Roman', 8)
    canvas.setFillColor(MDGRAY)
    canvas.drawCentredString(w / 2, 1.1 * cm, str(doc.page))
    canvas.restoreState()


def _first_page(canvas, doc):
    pass  # portada sin cabecera/pie


# ── Análisis del markdown y construcción de flowables ─────────────────────
def parse_md(md_text: str, S: dict) -> list:
    """Devuelve la lista de flowables a partir del markdown."""
    lines = md_text.split('\n')
    flow = []
    i = 0
    in_list = None          # None | 'bullet' | 'enum'
    in_blockquote = False
    in_code = False
    code_buf = []
    skip_toc = False
    enum_counter = 0

    def close_list():
        nonlocal in_list, enum_counter
        in_list = None
        enum_counter = 0

    def flush_code():
        nonlocal code_buf
        if code_buf:
            text = '\n'.join(code_buf)
            flow.append(Preformatted(text, S['code']))
            code_buf = []

    def close_blockquote():
        nonlocal in_blockquote
        in_blockquote = False

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1

        # ── Bloque de código ─────────────────────────────────────
        if stripped.startswith('```'):
            close_list()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_buf.append(raw)
            continue

        # ── Separador horizontal ─────────────────────────────────
        if stripped in ('---', '***', '___'):
            close_list()
            close_blockquote()
            flow.append(HRFlowable(
                width='100%', thickness=0.5,
                color=colors.Color(0.8, 0.8, 0.8),
                spaceAfter=8, spaceBefore=8))
            continue

        # ── Encabezados ──────────────────────────────────────────
        hdr = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if hdr:
            close_list()
            close_blockquote()
            level = len(hdr.group(1))
            title_raw = hdr.group(2)
            # Quitar links markdown del título
            title_raw = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', title_raw)
            title = md_inline(title_raw)

            if level == 1:
                pass  # El H1 ya está en la portada; omitir
            elif level == 2:
                # Detectar y saltar sección Tabla de Contenidos
                skip_toc = 'Tabla de Contenidos' in title_raw or 'tabla de contenidos' in title_raw.lower()
                if not skip_toc:
                    flow.append(Paragraph(title, S['h2']))
                    flow.append(HRFlowable(
                        width='100%', thickness=0.5, color=NAVY,
                        spaceAfter=4, spaceBefore=0))
            elif level == 3:
                if not skip_toc:
                    flow.append(Paragraph(title, S['h3']))
            elif level == 4:
                if not skip_toc:
                    flow.append(Paragraph(title, S['h4']))
            else:
                if not skip_toc:
                    flow.append(Paragraph(f'<b>{title}</b>', S['normal']))
            continue

        # Si llegamos a un H2 real después del TOC, ya no saltamos
        # (lo maneja el bloque de encabezados arriba)

        # ── Saltar entradas del TOC (líneas con links de ancla) ──
        if skip_toc:
            if re.match(r'^\s*\d+\.\s+\[', stripped) or re.match(r'^\s+-\s+\d+\.\d', stripped):
                continue
            # Fin del TOC si encontramos línea vacía tras él (handled by flow)
            if not stripped:
                continue
            # Si es texto normal, ya salimos del TOC
            skip_toc = False

        # ── Línea vacía ──────────────────────────────────────────
        if not stripped:
            close_list()
            close_blockquote()
            continue

        # ── Cita en bloque ───────────────────────────────────────
        if stripped.startswith('>'):
            close_list()
            content = stripped.lstrip('> ').strip()
            if content:
                flow.append(Paragraph(md_inline(content), S['blockquote']))
            continue
        else:
            close_blockquote()

        # ── Lista con viñeta ─────────────────────────────────────
        bullet_m = re.match(r'^[-*+]\s+(.+)$', stripped)
        if bullet_m:
            if in_list != 'bullet':
                close_list()
                in_list = 'bullet'
            content = md_inline(bullet_m.group(1))
            flow.append(Paragraph(f'• {content}', S['bullet']))
            continue

        # ── Lista numerada ───────────────────────────────────────
        enum_m = re.match(r'^\d+\.\s+(.+)$', stripped)
        if enum_m:
            if in_list != 'enum':
                close_list()
                in_list = 'enum'
                enum_counter = 0
            enum_counter += 1
            content = md_inline(enum_m.group(1))
            flow.append(Paragraph(f'{enum_counter}. {content}', S['enum_item']))
            continue

        # Si salimos de listas
        if in_list:
            close_list()

        # ── Párrafo normal ───────────────────────────────────────
        flow.append(Paragraph(md_inline(stripped), S['normal']))

    flush_code()
    return flow


# ── Portada ────────────────────────────────────────────────────────────────
def cover_page(S: dict) -> list:
    return [
        Spacer(1, 2 * cm),
        Paragraph('Universidad Nacional del Nordeste', S['cover_inst']),
        Paragraph('Facultad de Ciencias Exactas, Naturales y Agrimensura', S['cover_inst']),
        Paragraph('Ingeniería del Software II', S['cover_inst']),
        Spacer(1, 0.8 * cm),
        HRFlowable(width='100%', thickness=1.2, color=NAVY,
                   spaceAfter=0, spaceBefore=0),
        Spacer(1, 0.5 * cm),
        Paragraph('Arquitectura de Confianza Cero', S['cover_title']),
        Paragraph('Zero Trust Architecture (ZTA)', S['cover_subtitle']),
        Spacer(1, 0.3 * cm),
        HRFlowable(width='100%', thickness=1.2, color=NAVY,
                   spaceAfter=0, spaceBefore=0),
        Spacer(1, 1.5 * cm),
        Paragraph('Ariel Antinori', S['cover_author']),
        Paragraph('ariel.antinori@comunidad.unne.edu.ar', S['cover_meta']),
        Spacer(1, 0.4 * cm),
        Paragraph('Junio 2026', S['cover_meta']),
        PageBreak(),
    ]


# ── Resumen / palabras clave ───────────────────────────────────────────────
def abstract_page(S: dict) -> list:
    return [
        Spacer(1, 0.5 * cm),
        Paragraph('Resumen', S['abs_title']),
        Paragraph(ABSTRACT, S['abs_body']),
        Spacer(1, 0.3 * cm),
        Paragraph(KEYWORDS, S['keywords']),
        HRFlowable(width='100%', thickness=0.5,
                   color=colors.Color(0.8, 0.8, 0.8),
                   spaceAfter=6, spaceBefore=12),
    ]


# ── Punto de entrada ───────────────────────────────────────────────────────
def main():
    if not INPUT_FILE.exists():
        print(f'Error: no se encontro "{INPUT_FILE}"')
        print('Ejecute el script desde el directorio raiz del proyecto.')
        sys.exit(1)

    print(f'Leyendo {INPUT_FILE} ...')
    md_text = INPUT_FILE.read_text(encoding='utf-8')

    S = build_styles()

    print('Construyendo documento ...')
    story = []
    story += cover_page(S)
    story += abstract_page(S)
    story += parse_md(md_text, S)

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title='Arquitectura de Confianza Cero (ZTA)',
        author='Ariel Antinori',
        subject='Zero Trust Architecture — UNNE Ingeniería del Software II',
    )

    doc.build(story, onFirstPage=_first_page, onLaterPages=_header_footer)
    print(f'[OK] PDF generado: {OUTPUT_PDF}')
    print(f'     Tamanio: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
