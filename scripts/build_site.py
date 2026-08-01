#!/usr/bin/env python3
"""Build del sitio del estudio PPR · Aldebaran.
Convierte analisis/*.md al one-page docs/index.html usando el shell de plantilla/index.html
y los componentes de branding/tokens.css (badges conf-a/b/c, gap chips, table-scroll).
Uso: python3 scripts/build_site.py
"""
import re, shutil, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALISIS, DOCS, BRAND = ROOT / "analisis", ROOT / "docs", ROOT / "branding"

FECHA_CORTE = "31 de julio de 2026"
VERSION = "v1.0"

SECTIONS = [
    ("resumen",   "00", "Resumen ejecutivo",                 "00-resumen-ejecutivo.md",   False),
    ("macro",     "01", "Macro · El retiro en México",       "01-macro.md",               True),
    ("meso",      "02", "La industria del PPR",              "02-meso.md",                False),
    ("micro",     "03", "Competidores al detalle",           "03-micro-competidores.md",  True),
    ("desempleo", "04", "Cobertura de desempleo en PPR",     "04-desempleo.md",           False),
    ("sintesis",  "05", "Síntesis · Oportunidades para Sura","05-sintesis-sura.md",       True),
    ("anexos",    "06", "Anexos",                            "06-anexos.md",              False),
]

GAP = {"✅": "gap-si", "⚠️": "gap-lim", "❌": "gap-no", "🔍": "gap-ver"}

def badge(m):
    letter = m.group(2)
    return f'{m.group(1)}<span class="conf conf-{letter.lower()}">{letter}</span>'

def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    # badges de confiabilidad: "· A" / "· B" / "· C" (también A/B, B/C, C→..., etc.: se marca la primera letra)
    text = re.sub(r"(·\s*)([ABC])(?=[\s\],/→;)])", badge, text)
    # citas cortas [A], [B/C], [A/B]: cada letra se convierte en badge
    text = re.sub(r"\[([ABC])(?:/([ABC]))?\]",
                  lambda m: "[" + "/".join(f'<span class="conf conf-{g.lower()}">{g}</span>'
                                           for g in m.groups() if g) + "]", text)
    for chip, cls in GAP.items():
        text = text.replace(chip, f'<span class="gap {cls}">{chip}</span>')
    return text

def md_to_html(md):
    out, para, table, lst = [], [], [], None  # lst: ("ul"|"ol", items)

    def flush_para():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>"); para.clear()

    def flush_table():
        if not table: return
        rows = [r for r in table if not re.match(r"^\|[\s\-:|]+\|$", r)]
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        thead = "".join(f"<th>{inline(c)}</th>" for c in cells[0])
        body = ""
        for row in cells[1:]:
            body += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
        out.append(f'<div class="table-scroll"><table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>')
        table.clear()

    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("|"):
            flush_para(); flush_list(); table.append(line); continue
        flush_table()
        if not line.strip():
            flush_para(); flush_list(); continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush_para(); flush_list()
            level = min(len(m.group(1)) + 1, 5)  # ## -> h3, ### -> h4
            if len(m.group(1)) == 1:  # H1 del archivo: se omite (lo pone el shell)
                continue
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>"); continue
        if re.match(r"^---+$", line.strip()):
            flush_para(); flush_list(); continue
        m = re.match(r"^-\s+(.*)$", line)
        if m:
            flush_para()
            if lst and lst[0] != "ul": flush_list()
            lst = lst or ("ul", [])
            lst[1].append(m.group(1)); continue
        m = re.match(r"^\d+\.\s+(.*)$", line)
        if m:
            flush_para()
            if lst and lst[0] != "ol": flush_list()
            lst = lst or ("ol", [])
            lst[1].append(m.group(1)); continue
        if lst:  # continuación de item multilínea
            lst[1][-1] += " " + line.strip(); continue
        para.append(line.strip())
    flush_para(); flush_table(); flush_list()
    return "\n".join(out)

def build_section(sid, num, title, fname, white):
    path = ANALISIS / fname
    if not path.exists():
        body, lead = "<p><em>Sección en preparación.</em></p>", ""
    else:
        md = path.read_text(encoding="utf-8")
        md = re.sub(r"^\*\*Corte de datos.*$", "", md, flags=re.M)
        lead = ""
        m = re.search(r"^\*\*El hallazgo en tres líneas:\*\*\s*(.+?)$", md, flags=re.M)
        if m:
            lead = inline(m.group(1)); md = md.replace(m.group(0), "")
        body = md_to_html(md)
    bg = ' style="background:var(--white)"' if white else ""
    lead_html = f'<p class="section-lead">{lead}</p>' if lead else ""
    return (f'<section id="{sid}"{bg}><div class="section-inner">\n'
            f'<div class="section-num">{num}</div><h2 class="section-title">{title}</h2>\n'
            f'{lead_html}\n{body}\n</div></section>')

KPIS = """<div class="kpi-inner">
  <div><div class="kpi-num"><em>$213,973</em></div><div class="kpi-label">Deducible por persona en 2026 (5 UMA) <span class="conf conf-a">A</span></div></div>
  <div><div class="kpi-num">39</div><div class="kpi-label">Instituciones autorizadas por SAT <span class="conf conf-a">A</span></div></div>
  <div><div class="kpi-num">25-50×</div><div class="kpi-label">Lo que gana el asesor con un PPR-seguro vs. fondo (24 meses) <span class="conf conf-c">C</span></div></div>
  <div><div class="kpi-num"><em>$39 mil M</em></div><div class="kpi-label">Drenados de Afores por desempleo en 2025 <span class="conf conf-b">B</span></div></div>
  <div><div class="kpi-num">0</div><div class="kpi-label">PPR con cobertura de desempleo en México (veredicto Alcance B) <span class="conf conf-a">A</span></div></div>
</div>"""

EXTRA_CSS = """/* Complementos de contenido · no modifica tokens */
.section-inner h3 { font-weight: 800; font-size: 1.18rem; color: var(--black); margin: 2.6rem 0 0.8rem; }
.section-inner h4 { font-weight: 700; font-size: 1rem; color: var(--black); margin: 2rem 0 0.6rem; }
.section-inner h5 { font-weight: 700; font-size: 0.9rem; color: var(--gray); margin: 1.4rem 0 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; }
.section-inner p { margin: 0.9rem 0; max-width: 100ch; }
.section-inner ul, .section-inner ol { margin: 0.9rem 0 0.9rem 1.4rem; max-width: 100ch; }
.section-inner li { margin: 0.45rem 0; }
.section-inner strong { color: var(--black); }
.section-inner table { font-size: 0.82rem; }
"""

def main():
    DOCS.mkdir(exist_ok=True)
    assets = DOCS / "assets"; assets.mkdir(exist_ok=True)
    shutil.copy(BRAND / "tokens.css", assets / "tokens.css")
    shutil.copy(BRAND / "aldebaran-logo.svg", assets / "aldebaran-logo.svg")
    shutil.copy(BRAND / "sura-logo.svg", assets / "sura-logo.svg")
    (assets / "estudio.css").write_text(EXTRA_CSS, encoding="utf-8")

    shell = (ROOT / "plantilla" / "index.html").read_text(encoding="utf-8")
    shell = re.sub(r"\s*<!-- Shell del estudio.*?-->", "", shell, flags=re.S)
    shell = shell.replace('<link rel="stylesheet" href="assets/tokens.css">',
                          '<link rel="stylesheet" href="assets/tokens.css">\n  <link rel="stylesheet" href="assets/estudio.css">')
    shell = shell.replace("<strong>Fecha de corte</strong><!--TODO fecha-->",
                          f"<strong>Fecha de corte</strong>{FECHA_CORTE}")
    shell = shell.replace("<strong>Versión</strong>v0.1 borrador", f"<strong>Versión</strong>{VERSION}")
    shell = shell.replace("Corte de datos: <!--TODO-->", f"Corte de datos: {FECHA_CORTE}")
    start = shell.index('<div class="kpi-strip">')
    end = shell.index('<section id="resumen">')
    shell = shell[:start] + f'<div class="kpi-strip">{KPIS}</div>\n\n' + shell[end:]

    sections_html = "\n\n".join(build_section(*s) for s in SECTIONS)
    start = shell.index('<section id="resumen">')
    end = shell.index("<footer>")
    shell = shell[:start] + sections_html + "\n\n" + shell[end:]

    (DOCS / "index.html").write_text(shell, encoding="utf-8")
    size = (DOCS / "index.html").stat().st_size
    print(f"OK -> docs/index.html ({size/1024:.0f} KB)")

if __name__ == "__main__":
    main()
