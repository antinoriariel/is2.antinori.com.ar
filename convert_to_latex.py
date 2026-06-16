#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte zero_trust_arquitectura_confianza_cero.md a un paper académico en LaTeX.

Uso:
    python convert_to_latex.py           → genera zero_trust_paper.tex
    python convert_to_latex.py --pdf     → genera .tex y compila a PDF con pdflatex

Requisitos para --pdf: pdflatex instalado (TeX Live, MiKTeX o similar).
"""

import re
import sys
import subprocess
from pathlib import Path

INPUT_FILE  = Path("zero_trust_arquitectura_confianza_cero.md")
OUTPUT_TEX  = Path("public/downloads/zero_trust_paper.tex")

# ──────────────────────────────────────────────
# PREÁMBULO LaTeX
# ──────────────────────────────────────────────
PREAMBLE = r"""\documentclass[12pt,a4paper]{article}

%% Codificación e idioma
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-tabla,es-nodecimaldot]{babel}

%% Geometría de página
\usepackage[top=2.5cm,bottom=2.5cm,left=3cm,right=2.5cm]{geometry}

%% Tipografía y microajustes
\usepackage{microtype}
\usepackage{setspace}
\setstretch{1.25}

%% Colores
\usepackage{xcolor}
\definecolor{NavyBlue}{RGB}{0,70,127}
\definecolor{LightGray}{RGB}{248,248,248}
\definecolor{BorderBlue}{RGB}{30,80,180}
\definecolor{CodeBg}{RGB}{15,32,53}
\definecolor{CodeFg}{RGB}{125,211,252}

%% Hipervínculos
\usepackage[colorlinks=true,
            linkcolor=NavyBlue,
            urlcolor=NavyBlue,
            citecolor=NavyBlue,
            pdftitle={Arquitectura de Confianza Cero (ZTA)},
            pdfauthor={Ariel Antinori},
            pdfkeywords={Zero Trust, microservicios, mTLS, SPIFFE, OPA, Istio}]{hyperref}

%% Encabezados y pie de página
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textit{Zero Trust Architecture --- Confianza Cero en Microservicios}}
\fancyhead[R]{\small\textit{Ariel Antinori · UNNE}}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

%% Formato de secciones
\usepackage{titlesec}
\titleformat{\section}[hang]
  {\large\bfseries\color{NavyBlue}}{\thesection.}{0.75em}{}
  [\vspace{-0.4em}\rule{\textwidth}{0.5pt}\vspace{0.2em}]
\titleformat{\subsection}[hang]
  {\normalsize\bfseries}{\thesubsection.}{0.5em}{}
\titleformat{\subsubsection}[hang]
  {\normalsize\itshape\bfseries}{\thesubsubsection.}{0.5em}{}

%% Listas
\usepackage{enumitem}
\setlist[itemize]{leftmargin=1.5em, itemsep=2pt, parsep=0pt, topsep=4pt}
\setlist[enumerate]{leftmargin=1.5em, itemsep=2pt, parsep=0pt, topsep=4pt}

%% Bloques de cita con línea lateral
\usepackage[framemethod=default]{mdframed}
\mdfdefinestyle{quoteStyle}{
  backgroundcolor=LightGray,
  linecolor=BorderBlue,
  linewidth=3pt,
  topline=false,
  rightline=false,
  bottomline=false,
  innerleftmargin=12pt,
  innerrightmargin=8pt,
  innertopmargin=8pt,
  innerbottommargin=8pt,
  skipabove=8pt,
  skipbelow=8pt
}

%% Código fuente
\usepackage{listings}
\lstset{
  backgroundcolor=\color{CodeBg},
  basicstyle=\ttfamily\small\color{CodeFg},
  breaklines=true,
  frame=single,
  rulecolor=\color{BorderBlue},
  xleftmargin=8pt, xrightmargin=8pt,
  aboveskip=8pt, belowskip=8pt
}

%% Otros
\usepackage{parskip}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{abstract}

%% ── Portada ──────────────────────────────────
\title{%
  \vspace{-0.5cm}
  {\large\textsc{Universidad Nacional del Nordeste}}\\[0.2em]
  {\normalsize Facultad de Ciencias Exactas, Naturales y Agrimensura}\\
  {\normalsize Ingeniería del Software II}\\[1.5em]
  \rule{\linewidth}{1pt}\\[0.7em]
  {\LARGE\bfseries\color{NavyBlue} Arquitectura de Confianza Cero}\\[0.3em]
  {\Large\textit{Zero Trust Architecture (ZTA)}}\\[0.3em]
  {\large en el Desarrollo de Aplicaciones}\\[0.5em]
  \rule{\linewidth}{1pt}\\[0.5em]
  {\small\textit{Diseño de software bajo la premisa de red comprometida:\\
  autenticación y autorización granular en microservicios}}%
}

\author{%
  \textbf{Ariel Antinori}\\[0.4em]
  \href{mailto:ariel.antinori@comunidad.unne.edu.ar}%
       {\texttt{ariel.antinori@comunidad.unne.edu.ar}}\\[0.3em]
  Universidad Nacional del Nordeste%
}

\date{Junio 2026}
"""

ABSTRACT_BODY = r"""La Arquitectura de Confianza Cero (\textit{Zero Trust Architecture}, ZTA) representa
un cambio paradigmático en el diseño de sistemas de seguridad para aplicaciones distribuidas. Bajo la
premisa de que ninguna entidad---usuario, servicio o dispositivo---debe recibir confianza implícita por
su ubicación de red, ZTA impone verificación explícita, mínimo privilegio y monitoreo continuo en cada
capa del sistema. Este documento analiza sistemáticamente los fundamentos teóricos, los componentes
técnicos y los patrones de implementación de ZTA en arquitecturas de microservicios, abordando
tecnologías clave como SPIFFE/SPIRE, \textit{mTLS}, OAuth~2.0, OpenID Connect, Open Policy Agent (OPA)
y \textit{service meshes}. Se discuten los desafíos operativos, casos de adopción industrial y tendencias
emergentes incluyendo la integración con inteligencia artificial, entornos multi-nube y criptografía
post-cuántica."""

KEYWORDS_BODY = r"""\noindent\textbf{Palabras clave:} Zero Trust Architecture (ZTA), microservicios,
\textit{mTLS}, SPIFFE/SPIRE, OAuth~2.0, OpenID Connect, Open Policy Agent, \textit{service mesh},
microsegmentación, autenticación continua, DevSecOps."""


# ──────────────────────────────────────────────
# CONVERSIÓN MARKDOWN → LATEX
# ──────────────────────────────────────────────

def _escape_plain(text: str) -> str:
    """Escapa caracteres especiales LaTeX en texto plano (no dentro de comandos)."""
    # Backslash primero para no doble-escapar
    text = text.replace('\\', r'\textbackslash{}')
    text = text.replace('&',  r'\&')
    text = text.replace('%',  r'\%')
    text = text.replace('$',  r'\$')
    text = text.replace('#',  r'\#')
    text = text.replace('^',  r'\^{}')
    text = text.replace('~',  r'\~{}')
    text = text.replace('_',  r'\_')
    return text


def _escape_url(url: str) -> str:
    """Escapa lo mínimo necesario en una URL para LaTeX."""
    return url.replace('%', r'\%').replace('#', r'\#').replace('_', r'\_')


_inline_counter = [0]
_inline_store: dict[str, str] = {}


def _protect(latex_fragment: str) -> str:
    key = f'ZPROTECT{_inline_counter[0]}Z'
    _inline_store[key] = latex_fragment
    _inline_counter[0] += 1
    return key


def _restore(text: str) -> str:
    for key, val in _inline_store.items():
        text = text.replace(key, val)
    return text


def inline_to_latex(text: str) -> str:
    """Convierte formato inline markdown a comandos LaTeX."""
    # Limpiar estado global por llamada de alto nivel
    _inline_store.clear()
    _inline_counter[0] = 0
    return _inline_to_latex_inner(text)


def _inline_to_latex_inner(text: str) -> str:
    """Conversión recursiva de inline markdown."""

    # 1. Proteger links [texto](url)
    def replace_link(m):
        link_text = _inline_to_latex_inner(m.group(1))
        url = _escape_url(m.group(2))
        return _protect(f'\\href{{{url}}}{{{link_text}}}')
    text = re.sub(r'\[([^\]]*)\]\(([^)]*)\)', replace_link, text)

    # 2. Proteger código inline `code`
    def replace_code(m):
        code = m.group(1)
        code = code.replace('\\', r'\textbackslash{}')
        code = code.replace('_', r'\_')
        code = code.replace('$', r'\$')
        code = code.replace('#', r'\#')
        code = code.replace('%', r'\%')
        code = code.replace('&', r'\&')
        code = code.replace('^', r'\^{}')
        code = code.replace('~', r'\~{}')
        return _protect(f'\\texttt{{{code}}}')
    text = re.sub(r'`([^`]+)`', replace_code, text)

    # 3. Negrita + cursiva ***texto***
    def replace_bi(m):
        inner = _inline_to_latex_inner(m.group(1))
        return _protect(f'\\textbf{{\\textit{{{inner}}}}}')
    text = re.sub(r'\*\*\*(.+?)\*\*\*', replace_bi, text)

    # 4. Negrita **texto**
    def replace_bold(m):
        inner = _inline_to_latex_inner(m.group(1))
        return _protect(f'\\textbf{{{inner}}}')
    text = re.sub(r'\*\*(.+?)\*\*', replace_bold, text)

    # 5. Cursiva *texto* o _texto_
    def replace_italic(m):
        inner = _inline_to_latex_inner(m.group(1))
        return _protect(f'\\textit{{{inner}}}')
    text = re.sub(r'\*([^*\n]+?)\*', replace_italic, text)
    text = re.sub(r'_([^_\n]+?)_', replace_italic, text)

    # 6. Escapar texto plano (no los marcadores ZPROTECTZ)
    parts = re.split(r'(ZPROTECT\d+Z)', text)
    result_parts = []
    for part in parts:
        if re.fullmatch(r'ZPROTECT\d+Z', part):
            result_parts.append(_inline_store.get(part, part))
        else:
            result_parts.append(_escape_plain(part))
    return ''.join(result_parts)


def convert_body(md_text: str) -> str:
    """Convierte el cuerpo del markdown a LaTeX."""
    lines = md_text.split('\n')
    out: list[str] = []
    i = 0
    in_list: str | None = None   # None, 'itemize' o 'enumerate'
    in_blockquote = False
    in_code_block = False
    code_lines: list[str] = []
    h1_seen = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f'\\end{{{in_list}}}')
            in_list = None

    def close_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            out.append(r'\end{mdframed}')
            in_blockquote = False

    def flush_code():
        nonlocal code_lines
        if code_lines:
            body = '\n'.join(code_lines)
            out.append(r'\begin{lstlisting}')
            out.append(body)
            out.append(r'\end{lstlisting}')
            code_lines = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # ── Bloque de código ```
        if stripped.startswith('```'):
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                close_list()
                close_blockquote()
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(raw)
            i += 1
            continue

        # ── Separadores horizontales ---
        if stripped == '---':
            close_list()
            close_blockquote()
            out.append('')
            i += 1
            continue

        # ── Entradas de la Tabla de Contenidos (saltar)
        if re.match(r'^\s*\d+\.\s+\[.+?\]\(#.+?\)\s*$', stripped):
            i += 1
            continue
        if re.match(r'^\s+-\s+\d+\.\d', stripped):
            i += 1
            continue

        # ── Encabezados
        hdr = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if hdr:
            close_list()
            close_blockquote()
            level = len(hdr.group(1))
            title_raw = hdr.group(2)
            # Eliminar links tipo [texto](url) del título
            title_raw = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title_raw)
            title = inline_to_latex(title_raw)

            if level == 1:
                if not h1_seen:
                    h1_seen = True  # Omitir — está en \maketitle
                else:
                    out.append(f'\\section{{{title}}}')
            elif level == 2:
                out.append(f'\\section{{{title}}}')
            elif level == 3:
                out.append(f'\\subsection{{{title}}}')
            elif level == 4:
                out.append(f'\\subsubsection{{{title}}}')
            else:
                out.append(f'\\paragraph{{{title}}}')
            i += 1
            continue

        # ── Citas en bloque > texto
        if stripped.startswith('>'):
            close_list()
            if not in_blockquote:
                out.append(r'\begin{mdframed}[style=quoteStyle]')
                in_blockquote = True
            content = stripped.lstrip('> ').strip()
            if content:
                out.append(r'\textit{' + inline_to_latex(content) + r'}')
            else:
                out.append('')
            i += 1
            continue
        else:
            close_blockquote()

        # ── Listas con viñeta
        bullet = re.match(r'^[-*+]\s+(.+)$', stripped)
        if bullet:
            if in_list != 'itemize':
                close_list()
                out.append(r'\begin{itemize}')
                in_list = 'itemize'
            content = inline_to_latex(bullet.group(1))
            out.append(f'  \\item {content}')
            i += 1
            continue

        # ── Listas numeradas
        enum_m = re.match(r'^\d+\.\s+(.+)$', stripped)
        if enum_m:
            if in_list != 'enumerate':
                close_list()
                out.append(r'\begin{enumerate}')
                in_list = 'enumerate'
            content = inline_to_latex(enum_m.group(1))
            out.append(f'  \\item {content}')
            i += 1
            continue

        # Si salimos de una lista
        if in_list and not (bullet or enum_m):
            close_list()

        # ── Línea vacía
        if not stripped:
            out.append('')
            i += 1
            continue

        # ── Párrafo normal
        out.append(inline_to_latex(stripped))
        i += 1

    close_list()
    close_blockquote()
    flush_code()

    return '\n'.join(out)


def build_document(body: str) -> str:
    return (
        PREAMBLE
        + '\n\\begin{document}\n\n'
        + '\\maketitle\n\\thispagestyle{empty}\n\n'
        + '\\begin{abstract}\n'
        + ABSTRACT_BODY
        + '\n\\end{abstract}\n\n'
        + KEYWORDS_BODY + '\n\n'
        + '\\vspace{1em}\n'
        + '\\tableofcontents\n\\newpage\n\n'
        + body
        + '\n\n\\end{document}\n'
    )


# ──────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────

def main() -> None:
    generate_pdf = '--pdf' in sys.argv

    if not INPUT_FILE.exists():
        print(f'Error: no se encontró el archivo "{INPUT_FILE}"')
        print('Asegúrese de ejecutar el script desde el mismo directorio que el .md')
        sys.exit(1)

    print(f'Leyendo {INPUT_FILE} ...')
    md_text = INPUT_FILE.read_text(encoding='utf-8')

    print('Convirtiendo a LaTeX ...')
    body = convert_body(md_text)
    document = build_document(body)

    OUTPUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_TEX.write_text(document, encoding='utf-8')
    print(f'[OK] Archivo generado: {OUTPUT_TEX}')

    if generate_pdf:
        for run in range(1, 3):
            print(f'  Compilando con pdflatex (pasada {run}/2)...')
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', str(OUTPUT_TEX)],
                capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            if result.returncode != 0:
                print('  Error durante la compilacion:')
                print(result.stdout[-3000:])
                print('\n  Sugerencia: revise el archivo .tex generado para identificar el error.')
                sys.exit(1)

        pdf_path = OUTPUT_TEX.with_suffix('.pdf')
        print(f'[OK] PDF generado: {pdf_path}')

        # Limpiar archivos auxiliares
        for ext in ['.aux', '.log', '.toc', '.out']:
            aux = OUTPUT_TEX.with_suffix(ext)
            if aux.exists():
                aux.unlink()
        print('  Archivos auxiliares eliminados.')
    else:
        print()
        print('Para compilar el PDF ejecute:')
        print(f'  pdflatex {OUTPUT_TEX}')
        print(f'  pdflatex {OUTPUT_TEX}   (segunda pasada para TOC y referencias cruzadas)')
        print()
        print('Requisito: TeX Live, MiKTeX o MacTeX instalado y pdflatex en el PATH.')


if __name__ == '__main__':
    main()
