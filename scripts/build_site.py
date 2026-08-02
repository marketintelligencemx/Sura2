#!/usr/bin/env python3
"""Build del sitio del estudio PPR · Aldebaran.
Convierte analisis/*.md al one-page docs/index.html usando el shell de plantilla/index.html
y los componentes de branding/tokens.css (badges conf-a/b/c, gap chips, table-scroll).
Uso: python3 scripts/build_site.py
"""
import re, shutil, html, unicodedata
from pathlib import Path

def slug(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]

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
        wide = " wide-table" if len(cells[0]) >= 7 else ""
        out.append(f'<div class="table-scroll{wide}"><table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>')
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

FUENTES_MOVIDAS = []  # (num, titulo, md del bloque de fuentes) extraídas de 01-05 para el final

def build_section(sid, num, title, fname, white, toc):
    path = ANALISIS / fname
    if not path.exists():
        body, lead = "<p><em>Sección en preparación.</em></p>", ""
    else:
        md = path.read_text(encoding="utf-8")
        md = re.sub(r"^\*\*Corte de datos.*$", "", md, flags=re.M)
        if num in ("01", "02", "03", "04", "05"):
            m = re.search(r"^### Fuentes.*", md, flags=re.S | re.M)
            if m:
                FUENTES_MOVIDAS.append((num, title, re.sub(r"^### Fuentes[^\n]*\n", "", m.group(0))))
                md = md[:m.start()]
        lead = ""
        m = re.search(r"^\*\*El hallazgo en tres líneas:\*\*\s*(.+?)$", md, flags=re.M)
        if m:
            lead = inline(m.group(1)); md = md.replace(m.group(0), "")
        body = md_to_html(md)
        body = re.sub(r"<p>\{\{viz:([\w-]+)\}\}</p>", lambda m: VIZ[m.group(1)](), body)
    if num == "06" and FUENTES_MOVIDAS:
        body += '<h3 id="referencias-por-seccion">E. Referencias por sección</h3>'
        body += '<p>Fuentes citadas en el cuerpo del estudio, con fecha de consulta 28 a 31-jul-2026, agrupadas por capítulo.</p>'
        for fnum, ftitle, fmd in FUENTES_MOVIDAS:
            body += f"<h4>{fnum} · {ftitle}</h4>" + md_to_html(fmd)
    subs = []
    def h3id(m):
        s = slug(m.group(1)) or f"{sid}-sub{len(subs)}"
        subs.append((s, m.group(1)))
        return f'<h3 id="{s}">{m.group(1)}</h3>'
    body = re.sub(r"<h3>(.*?)</h3>", h3id, body)
    toc.append((num, title, sid, subs))
    bg = ' style="background:var(--white)"' if white else ""
    lead_html = f'<p class="section-lead">{lead}</p>' if lead else ""
    return (f'<section id="{sid}"{bg}><div class="section-inner">\n'
            f'<div class="section-num">{num}</div><h2 class="section-title">{title}</h2>\n'
            f'{lead_html}\n{body}\n</div></section>')

def build_toc(toc):
    items = ""
    for num, title, sid, subs in toc:
        subhtml = ""
        if subs and num != "00":
            lis = "".join(f'<li><a href="#{s}">{t}</a></li>' for s, t in subs[:8])
            subhtml = f'<ul class="toc-sub">{lis}</ul>'
        items += f'<div class="toc-item"><a href="#{sid}"><span class="toc-num">{num}</span>{title}</a>{subhtml}</div>'
    return (f'<section id="indice" style="background:var(--white)"><div class="section-inner">\n'
            f'<div class="section-num">··</div><h2 class="section-title">Índice del estudio</h2>\n'
            f'<p class="section-lead">De macro a micro: el terreno, la industria, cada competidor al detalle, el capítulo especial de desempleo y la síntesis accionable. Metodología y referencias completas al final.</p>'
            f'<div class="toc">{items}</div>\n</div></section>')

def _b(l):
    return f'<span class="conf conf-{l.lower()}">{l}</span>'

def _chip(t):
    sym = {"si": "✅", "lim": "⚠️", "no": "❌", "na": "🔍"}
    cls = {"si": "gap-si", "lim": "gap-lim", "no": "gap-no", "na": "gap-ver"}
    return f'<span class="gap {cls[t]}">{sym[t]}</span>'

def _cell(tier, txt):
    return f'<td class="h-{tier}">{_chip(tier if tier in ("si","lim","no","na") else "na")} {txt}</td>'

def _ccell(tier, txt):
    lab = {"c3": "Alto", "c2": "Medio", "c1": "Bajo", "na": "🔍"}[tier]
    return f'<td class="h-{tier}"><strong>{lab}</strong> · {txt}</td>'

# (jugador, arquetipo, sura?, costo, transparencia, mínimo, salida, protección, digital, inversión, canal)
HEAT_ROWS = [
 ("Allianz", "híbrido", 0, ("no","1.53-2.65% + cargos "+_b("B")), ("lim","costo total solo en deck de agentes "+_b("B")), ("lim","$2-3 mil/mes "+_b("B")), ("no","candado 18 m; castigo hasta año 10 "+_b("B")), ("lim","mínima (~$500 único) "+_b("B")), ("no","solo vía agente "+_b("B")), ("si","19 alternativas, 3 monedas "+_b("B")), ("c3","2.7% del plan, 70% anticipado "+_b("C")+"✓")),
 ("Skandia", "híbrido", 0, ("no","~2.0% + 10 UMA (baja a 0.8%) "+_b("A")), ("lim","cargos en CG públicas; canal opaco "+_b("A")), ("lim","$1.5-3 mil/mes "+_b("A")), ("no","recuperas 10% en año 1 "+_b("B")), ("si","vida + invalidez "+_b("A")), ("lim","app de consulta; papel en trámites "+_b("A")), ("si","arquitectura abierta + S&P 500 "+_b("A")), ("c2","25-35% año 1 "+_b("C")+" 🔍")),
 ("GNP", "seguro", 0, ("na","embebido; tabla solo en póliza "+_b("A")), ("no","no pública "+_b("A")), ("lim","~$2-2.5 mil/mes "+_b("C")), ("no","rescate ~$0 años 1-3 "+_b("B")), ("si","completa + exención invalidez "+_b("A")), ("no","solo agente "+_b("B")), ("no","sin elección; UDIs/USD "+_b("A")), ("c3","40-50% año 1 + bonos "+_b("C")+"✓")),
 ("Seguros Monterrey NYL", "seguro", 0, ("na","embebido "+_b("A")), ("no","no pública "+_b("A")), ("na","por cotización"), ("no","castigado (tabla en póliza) "+_b("A")), ("si","completa + renta vitalicia "+_b("A")), ("no","sin cotizador público "+_b("C")), ("lim","garantía 2% USD / 1% real UDI "+_b("A")), ("c3","35-45% año 1 + bonos "+_b("C")+"✓")),
 ("MetLife", "seguro", 0, ("lim","nota técnica; única tabla pública "+_b("A")), ("lim","tabla de castigo abierta "+_b("A")), ("na","no pública"), ("no","100% años 1-2 → 0% año 10 "+_b("A")), ("si","completa "+_b("A")), ("no","vía promotorías "+_b("B")), ("lim","deuda+RV; 2% garantizado "+_b("A")), ("c3","30-50% (señal 100-140%) "+_b("C"))),
 ("AXA", "seguro", 0, ("na","no público "+_b("A")), ("no","no pública "+_b("A")), ("lim","🔍; Mi Proyecto R $100/mes "+_b("C")), ("lim","valores garantizados en póliza "+_b("A")), ("lim","anticipos; invalidez opcional "+_b("A")), ("no","agentes "+_b("A")), ("no","sin portafolios elegibles "+_b("A")), ("na","sin indicios")),
 ("Sura", "fondo", 1, ("no","2.46% BFE / 2.11% BFS "+_b("A")), ("no","solo en DICI, no comercial "+_b("A")), ("na","no publicado "+_b("A")), ("si","diaria, sin castigo propio "+_b("A")), ("no","ninguna "+_b("A")), ("lim","app de consulta; sin autoservicio "+_b("B")), ("si","target-date completa (única) "+_b("B")), ("c1","trail embebido; sin frontal "+_b("A"))),
 ("Actinver", "fondo", 0, ("si","1.00% clase E + cuota de cuenta "+_b("A")), ("lim","prospecto claro; página floja "+_b("A")), ("lim","$10,000 "+_b("B")), ("si","diaria "+_b("A")), ("lim","opcionales con costo "+_b("B")), ("lim","banco + app "+_b("B")), ("lim","ciclos de vida sin escala "+_b("B")), ("na","split intragrupo 🔍")),
 ("Principal", "fondo", 0, ("lim","1.87% XF1 "+_b("A")), ("si","desglosa distribución (1.20%) "+_b("A")), ("si","~$1,000 "+_b("C")), ("si","diaria "+_b("A")), ("no","ninguna"), ("si","app Afore+fondos "+_b("B")), ("si","target-date LifeCycle "+_b("A")), ("c2","1.20% recurrente al canal "+_b("A"))),
 ("Fintual", "digital", 0, ("si","1% + IVA "+_b("B")), ("si","precio en portada "+_b("B")), ("si","$0 "+_b("B")), ("si","sin castigos "+_b("B")), ("no","ninguna"), ("si","100% autoservicio "+_b("B")), ("lim","2 portafolios "+_b("A")), ("c1","sin agentes; referidos 1% "+_b("B"))),
 ("GBM", "digital", 0, ("lim","cuotas de fondos 1-2.75% "+_b("B")), ("lim","sin % único visible "+_b("B")), ("lim","$10,000 "+_b("B")), ("si","sin plazo forzoso "+_b("B")), ("no","ninguna"), ("si","app; 24 M cuentas "+_b("A")), ("si","perfilado + universo GBM "+_b("B")), ("c2","payout 40% a afiliados "+_b("B"))),
 ("Vector", "fuera del mercado", 0, ("na","revocada dic-2025 "+_b("A")), ("na",""), ("na",""), ("na",""), ("na",""), ("na",""), ("na","clientes migrados a Finamex "+_b("B")), ("na","")),
 ("Banco Inbursa (CT Retiro Plus)", "bancario", 0, ("si","$0 comisiones "+_b("B")), ("si","publicado "+_b("B")), ("si","$1,000 "+_b("B")), ("lim","bancaria "+_b("B")), ("no","ninguna"), ("lim","banca en línea "+_b("B")), ("no","solo CETES (100%/80%) "+_b("B")), ("na","n/a")),
 ("Seguros Inbursa (Retiro Activo)", "seguro", 0, ("na","no pública "+_b("A")), ("no","no pública "+_b("A")), ("na","no público"), ("lim","valores garantizados "+_b("A")), ("si","vida + adicionales "+_b("A")), ("no","agentes"), ("lim","dividendos no garantizados "+_b("A")), ("na","🔍")),
 ("Afore XXI Banorte (voluntario)", "afore", 0, ("si","0.54% "+_b("B")), ("si","publicado "+_b("B")), ("si","$50 "+_b("B")), ("lim","reglas SAR "+_b("B")), ("no","ninguna"), ("si","AforeMóvil "+_b("B")), ("lim","3 perfiles "+_b("B")), ("na","n/a")),
 ("Kuspit", "digital", 0, ("si","0.99% "+_b("C")+"✓"), ("lim","visible, poco promovido "+_b("C")), ("si","$100 "+_b("C")+"✓"), ("si","sin plazos "+_b("C")), ("no","ninguna"), ("si","plataforma digital "+_b("C")), ("lim","a elección del cliente "+_b("C")), ("na","n/a")),
 ("HSBC Seguros (Retiro Protegido)", "seguro", 0, ("na","no pública "+_b("B")), ("no","no pública"), ("na","señal: desde $100 mil "+_b("A")), ("na","🔍"), ("si","vida "+_b("B")), ("no","ejecutivo/Premier "+_b("B")), ("lim","fondos con rebalanceo "+_b("B")), ("na","🔍")),
 ("Seguros Banamex", "seguro", 0, ("na","no pública "+_b("B")), ("no","no pública"), ("na","🔍"), ("na","🔍"), ("si","vida "+_b("A")), ("no","canal banco"), ("lim","reservas sin garantía "+_b("A")), ("na","🔍")),
 ("Prudential", "seguro", 0, ("na","no pública "+_b("A")), ("no","no pública"), ("lim","~$2,500/mes "+_b("C")), ("na","🔍"), ("si","vida + invalidez "+_b("A")), ("no","promotorías "+_b("C")), ("na","🔍"), ("na","🔍")),
 ("Monex", "banca privada", 0, ("na","no pública "+_b("B")), ("no","no pública"), ("no","segmento alto (~$300 mil) "+_b("B")), ("na","🔍"), ("no","ninguna"), ("no","vía asesor BP"), ("lim","divisas y estructurados "+_b("B")), ("na","🔍")),
 ("Valmex", "empresarial", 0, ("na","retail ~1% sin confirmar "+_b("C")), ("no","no pública"), ("lim","nómina: 1-10% del sueldo "+_b("A")), ("na","🔍"), ("no","ninguna"), ("lim","app ValmexSi "+_b("A")), ("na","🔍"), ("na","🔍")),
 ("Insignia Life", "seguro", 0, ("na","no pública "+_b("B")), ("no","no pública"), ("na","🔍"), ("na","🔍"), ("si","vida "+_b("B")), ("no","agentes "+_b("C")), ("na","🔍"), ("na","🔍")),
 ("SAM (Santander)", "operadora", 0, ("na","no pública "+_b("B")), ("no","sin página retail "+_b("B")), ("na","🔍"), ("na","🔍"), ("no","ninguna"), ("no","vía asesor"), ("lim","cartera modelo "+_b("B")), ("na","🔍")),
 ("Fondika", "distribuidora", 0, ("na","página rota al corte "+_b("C")), ("na",""), ("na",""), ("na",""), ("na",""), ("na",""), ("na",""), ("na","")),
 ("Ve por Más · Intercam · Azimut", "licencias dormidas", 0, ("na","sin oferta visible "+_b("C")), ("na",""), ("na",""), ("na",""), ("na",""), ("na",""), ("na",""), ("na","")),
]

def viz_heatmap():
    head = "".join(f"<th>{h}</th>" for h in
        ["Jugador · arquetipo", "Costo al cliente", "Transparencia de precio", "Mínimo de entrada",
         "Castigo de salida", "Protección incluida", "Experiencia digital", "Inversión", "Pago al canal"])
    rows = ""
    for (nom, arq, sura, costo, transp, mini, sal, prot, dig, inv, canal) in HEAT_ROWS:
        cls = ' class="sura"' if sura else ""
        rows += (f'<tr{cls}><td class="jug">{nom}<br><span style="font-weight:500;color:var(--gray);font-size:0.68rem">{arq}</span></td>'
                 + _cell(*costo) + _cell(*transp) + _cell(*mini) + _cell(*sal) + _cell(*prot)
                 + _cell(*dig) + _cell(*inv) + _ccell(*canal) + "</tr>")
    return f'''<div class="viz viz-wide"><div class="viz-title">Mapa de calor · Los 25 emisores del mercado PPR en 8 dimensiones</div>
<div class="viz-sub">El color resume el dato documentado en cada celda desde la perspectiva del CLIENTE; el chip repite el veredicto para lectura sin color. La columna "Pago al canal" mide otra cosa (cuánto gana el asesor) y por eso usa azul. Fila de Sura enmarcada en rojo. Fuentes: fichas 3.1-3.11 y Gran Matriz de la sección 02.</div>
<div class="table-scroll"><table class="heat"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>
<div class="viz-legend"><span><span class="lg" style="background:rgba(5,150,105,0.14)"></span>✅ favorable</span>
<span><span class="lg" style="background:rgba(180,83,9,0.13)"></span>⚠️ intermedio</span>
<span><span class="lg" style="background:rgba(230,51,41,0.12)"></span>❌ desfavorable</span>
<span><span class="lg" style="background:#ECEAE6"></span>🔍 no público / no aplica</span>
<span><span class="lg" style="background:rgba(37,99,235,0.22)"></span>Azul: intensidad = pago al canal (Alto/Medio/Bajo)</span></div></div>'''

def _bars(title, sub, rows, maxv, unit, note, fmt=lambda a, b: ""):
    out = ""
    for (label, lo, hi, acc, badge) in rows:
        left = lo / maxv * 100; width = max((hi - lo) / maxv * 100, 1.2)
        val = fmt(lo, hi) + " " + badge
        out += (f'<div class="bar-row"><div class="bar-label">{label}</div>'
                f'<div class="bar-track"><div class="bar-fill{" acc" if acc else ""}" style="left:{left:.1f}%;width:{width:.1f}%">'
                f'<span class="bar-val">{val}</span></div></div></div>')
    tick = (lambda v: f"${v:,.0f}") if unit == "$" else (lambda v: f"{v:g}%")
    scale = (f'<div class="bar-scale"><div></div><div class="bar-scale-track">'
             f'<span>{tick(0)}</span><span>{tick(maxv/4)}</span><span>{tick(maxv/2)}</span>'
             f'<span>{tick(3*maxv/4)}</span><span>{tick(maxv)}</span></div></div>')
    return (f'<div class="viz"><div class="viz-title">{title}</div><div class="viz-sub">{sub}</div>'
            f'<div class="bars">{out}</div>{scale}<div class="bar-note">{note}</div></div>')

def viz_costos():
    f = lambda lo, hi: (f"{lo:.2f}%" if lo == hi else f"{lo:.2f}-{hi:.2f}%")
    rows = [
        ("Inbursa CT Retiro Plus", 0.0, 0.0, 0, _b("B")), ("XXI Banorte (voluntario)", 0.54, 0.54, 0, _b("B")),
        ("Kuspit", 0.99, 0.99, 0, _b("C") + "✓"), ("Actinver (clase E)", 1.00, 1.00, 0, _b("A")),
        ("Fintual (con IVA)", 1.16, 1.16, 0, _b("B")), ("Skandia (según etapa)", 0.8, 2.0, 0, _b("A")),
        ("Allianz (según monto/plazo)", 1.53, 2.65, 0, _b("B")), ("Principal (XF1)", 1.87, 1.87, 0, _b("A")),
        ("GBM (cuotas de fondos)", 1.0, 2.75, 0, _b("B")), ("Sura (BFS-BFE)", 2.11, 2.46, 1, _b("A")),
    ]
    return _bars("Comisión total anual al cliente, emisores con precio verificable",
        "Rango publicado o documentado en prospectos, DICI y condiciones registradas. Barra roja: Sura, el cliente de este estudio.",
        rows, 3.0, "%",
        "No graficables por costo no público: GNP, Seguros Monterrey NYL, AXA, Seguros Inbursa, HSBC, Banamex, Prudential, Monex, Insignia (embebido en prima o sin tarifario) 🔍. Actinver suma cuota de cuenta de $1,890-2,500 + IVA al año. Escala 0-3%.", f)

def viz_asesor():
    f = lambda lo, hi: (f"${lo:,.0f}" if lo == hi else f"${lo:,.0f}-{hi:,.0f}")
    rows = [
        ("PPR-seguro (GNP / SMNYL)", 47000, 60000, 0, _b("C") + "✓"),
        ("Allianz (70/30 del 2.7% total)", 54000, 54000, 0, _b("C") + "✓"),
        ("Skandia", 29000, 39000, 0, _b("C") + " 🔍"),
        ("PPR-fondo (trail 0.4-0.6% AUM)", 1200, 1800, 1, _b("C")),
    ]
    return _bars("Lo que gana el asesor en los primeros 24 meses por cada $100,000 anuales del cliente",
        "Cálculo Aldebaran sobre los rangos del deep dive 3.12. La barra del arquetipo fondo casi no se ve: esa es exactamente la explicación del mercado.",
        rows, 60000, "$", "La brecha es de 25 a 50 veces. En el horizonte a 20 años el trail puede superar al frontal en pesos nominales, pero cargado a los años 8-20 (ver 3.12).", f)

def viz_duracion():
    f = lambda lo, hi: f"{hi:.1f}%"
    rows = [
        ("Hasta 1 mes", 0, 43.5, 0, _b("A")), ("1 a 3 meses", 0, 30.3, 0, _b("A")),
        ("3 a 6 meses", 0, 15.5, 0, _b("A")), ("6 meses a 1 año", 0, 3.4, 0, _b("A")),
        ("Más de 1 año", 0, 3.5, 0, _b("A")),
    ]
    return _bars("¿Cuánto dura el desempleo en México? Distribución de la población desocupada",
        "INEGI, ENOE junio 2026. El 73.8% de los desempleos dura 3 meses o menos: un beneficio de 3 a 6 meses cubre la gran mayoría de los siniestros.",
        rows, 50, "%", "Duración promedio estimada: ~2.4 meses (estimación Aldebaran por marcas de clase; sensible al tramo abierto). Escala 0-50%.", f)

def viz_brecha():
    f = lambda lo, hi: f"{hi:.1f}%"
    rows = [("Lo que repone la Afore (promedio OCDE)", 0, 55.5, 1, _b("A")),
            ("Nivel deseable según OCDE", 0, 70.0, 0, _b("A")),
            ("Con Fondo de Pensiones Bienestar (solo hasta $17,885/mes)", 0, 96.1, 0, _b("A"))]
    return _bars("La brecha de pensión: % del último sueldo que repone el sistema",
        "Tasa de reemplazo esperada. El complemento estatal cierra la brecha solo por debajo de $17,885.85 mensuales: arriba de ese ingreso vive el cliente del PPR.",
        rows, 100, "%", "Fuentes: OCDE Pensions at a Glance 2023; IMSS 2026. Escala 0-100%.", f)

def viz_envejecimiento():
    f = lambda lo, hi: f"{hi:.1f}%"
    rows = [("2026", 0, 13.2, 0, _b("A")), ("2030 (supera a los niños de 0-14)", 0, 15.0, 0, _b("A")),
            ("2070", 0, 34.2, 1, _b("A"))]
    return _bars("México envejece: población de 60 años y más",
        "Porcentaje de la población total. Cada generación vivirá más años de retiro que la anterior (esperanza de vida 2026: 75.85 años).",
        rows, 40, "%", "Fuente: CONAPO, proyecciones. Escala 0-40%.", f)

def viz_canales():
    f = lambda lo, hi: f"{lo:.0f}-{hi:.0f}%"
    rows = [("Agentes y promotorías", 60, 70, 0, _b("C") + "✓"),
            ("Banca seguros", 15, 20, 0, _b("C") + " 🔍"),
            ("Digital y fintech (el que más crece)", 10, 17, 1, _b("C"))]
    return _bars("¿Por dónde se vende el PPR? Peso estimado de cada canal",
        "Rangos triangulados (borrador + McKinsey LATAM 2025). La venta sigue anclada al asesor humano; el digital fija el precio de referencia público.",
        rows, 80, "%", "Estimación Aldebaran en rangos; el canal agencial está triangulado con dos fuentes, banca y digital son indicio único 🔍. Escala 0-80%.", f)

def viz_stats_desempleo():
    tiles = [("$39,000 M", "retirados de las Afores por desempleo solo en 2025, máximo histórico (+26.5%) " + _b("B")),
             ("1.94 M", "trámites de retiro por desempleo en 2025 (+13% anual) " + _b("B")),
             ("$162,320 M", "acumulados 2020-2025: el desempleo ya drena el retiro a gran escala " + _b("B")),
             ("~$20,000", "promedio por retiro (cálculo Aldebaran) " + _b("C"))]
    body = "".join(f'<div class="stat"><div class="stat-num">{n}</div><div class="stat-label">{l}</div></div>' for n, l in tiles)
    return (f'<div class="viz"><div class="viz-title">El costo del desempleo para el retiro mexicano, en cifras</div>'
            f'<div class="viz-sub">Retiros parciales por desempleo del sistema Afore (CONSAR vía prensa, 2026). Cada retiro descuenta además semanas cotizadas.</div>'
            f'<div class="viz-stats">{body}</div></div>')

def viz_oportunidades():
    # (etiqueta, x factibilidad 0-100, y impacto 0-100)
    pts = [("O1 · Reprecio + transparencia", 82, 84), ("O2 · Trail adelantado al canal", 55, 86),
           ("O3 · Modo desempleo (90 días)", 94, 58), ("O4 · Cobertura desempleo asegurada", 34, 92),
           ("O5 · Contratación digital", 55, 56)]
    dots = "".join(f'<div class="dot" style="left:{x}%;bottom:{y}%"></div>'
                   f'<div class="dot-label" style="left:{x}%;bottom:{y}%">{n}</div>' for n, x, y in pts)
    return (f'<div class="viz"><div class="viz-title">Las 5 oportunidades para Sura: impacto × factibilidad</div>'
            f'<div class="viz-sub">Posiciones cualitativas derivadas de la sección 5.3 (estimación Aldebaran). Arriba a la derecha = hacer ya; arriba a la izquierda = construir.</div>'
            f'<div class="scatter">{dots}'
            f'<div class="ax" style="bottom:-1.8rem;right:0">Factibilidad →</div>'
            f'<div class="ax" style="top:0;left:0.5rem;writing-mode:vertical-rl;transform:rotate(180deg)">Impacto →</div>'
            f'</div><div class="bar-note" style="margin-top:2.2rem">Secuencia recomendada: O3 inmediata, O1 en paralelo, O2 con la ventana Vector abierta, O5 habilitador, O4 el diferenciador de fondo.</div></div>')

def viz_versus():
    left = ('<div class="vs-col"><div class="vs-title">PPR-seguro (y el híbrido)</div>'
            '<div class="vs-row"><span class="vs-big">40-50%</span><br>de la prima del año 1 gana el asesor ' + _b("C") + '✓</div>'
            '<div class="vs-row"><b>Qué compra el cliente:</b> protección (vida, invalidez) + disciplina forzada + garantías en UDIs/USD</div>'
            '<div class="vs-row"><b>Costo:</b> embebido en la prima, opaco por diseño ' + _b("A") + '</div>'
            '<div class="vs-row"><b>Si cancela pronto:</b> valor de rescate cercano a $0 los primeros 3 años ' + _b("A") + '</div>'
            '<div class="vs-row"><b>Quién lo empuja:</b> 40,000+ agentes y promotorías</div></div>')
    right = ('<div class="vs-col"><div class="vs-title">PPR-fondo (y el digital)</div>'
             '<div class="vs-row"><span class="vs-big">0.4-1.2%</span><br>anual sobre saldo gana el canal, recurrente ' + _b("A") + '/' + _b("B") + '</div>'
             '<div class="vs-row"><b>Qué compra el cliente:</b> inversión pura, portafolios transparentes, liquidez diaria</div>'
             '<div class="vs-row"><b>Costo:</b> 1% a 2.5% anual visible en documentos ' + _b("A") + '</div>'
             '<div class="vs-row"><b>Si cancela pronto:</b> sin castigo contractual (solo el fiscal del SAT) ' + _b("A") + '</div>'
             '<div class="vs-row"><b>Quién lo empuja:</b> apps, referidos y asesores patrimoniales</div></div>')
    return ('<div class="viz"><div class="viz-title">Un mercado, dos negocios: la tensión que explica todo el estudio</div>'
            '<div class="viz-sub">Mismo beneficio fiscal (Art. 151), economías opuestas. Nadie combina lo mejor de ambos: esa es la grieta estructural y la oportunidad.</div>'
            f'<div class="versus">{left}<div class="vs-mid">VS</div>{right}</div></div>')

def viz_donut():
    return ('<div class="viz"><div class="viz-title">El mercado está casi virgen</div>'
            '<div class="viz-flex"><div class="donut" style="--p:8%"><div class="donut-center"><b>8%</b><small>ahorra<br>voluntario</small></div></div>'
            '<div class="donut-side">De los ~70 millones de cuentahabientes del sistema Afore, solo <b>8% hace algún ahorro voluntario</b> '
            + _b("B") + '. El 92% restante es mercado direccionable sin activar, en un sistema que ya administra $8.95 billones (25% del PIB) '
            + _b("B") + '. El PPR compite por convertir ese flujo dormido, con el subsidio fiscal más alto de la historia como gancho ($213,973 deducibles en 2026 '
            + _b("A") + ').</div></div></div>')

VIZ = {"heatmap-jugadores": viz_heatmap, "barras-costo-cliente": viz_costos,
       "versus-arquetipos": viz_versus, "donut-voluntario": viz_donut,
       "barras-asesor": viz_asesor, "barras-duracion": viz_duracion,
       "barras-brecha": viz_brecha, "barras-envejecimiento": viz_envejecimiento,
       "barras-canales": viz_canales, "stats-desempleo": viz_stats_desempleo,
       "scatter-oportunidades": viz_oportunidades}

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
.section-inner p { margin: 0.9rem 0; max-width: none; }
.section-inner ul, .section-inner ol { margin: 0.9rem 0 0.9rem 1.4rem; max-width: none; }
.section-inner li { margin: 0.45rem 0; }
.section-inner strong { color: var(--black); }
.section-inner table { font-size: 0.85rem; }

/* ── Visualizaciones (CSS puro, sin JS) ── */
.viz { background: var(--white); border: 1px solid var(--gray-border); border-radius: 6px;
  padding: 1.4rem 1.6rem; margin: 1.6rem 0; }
.viz-title { font-weight: 800; font-size: 0.95rem; color: var(--black); }
.viz-sub { font-size: 0.78rem; color: var(--gray); margin: 0.2rem 0 1rem; }
.viz-legend { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.72rem; font-weight: 600;
  color: var(--gray); margin: 0.8rem 0 0; }
.viz-legend span { display: inline-flex; align-items: center; gap: 0.35rem; }
.lg { display: inline-block; width: 12px; height: 12px; border-radius: 3px; border: 1px solid var(--gray-border); }

/* Tipografía global más grande (todo lo definido en rem escala junto) */
html { font-size: 17.5px; }

/* Márgenes reducidos: contenedores más anchos que el shell original */
.section-inner, .nav-inner, .hero-inner, .kpi-inner, .footer-inner { max-width: min(1520px, 96vw); }
section { padding-left: 1.6rem; padding-right: 1.6rem; }
.hero { padding-left: 1.6rem; padding-right: 1.6rem; }
.section-lead { max-width: none; font-size: 1.02rem; }

/* Contenedor ancho centrado con MÁRGENES (nunca transform: las animaciones lo pisarían) */
.viz-wide, .wide-table { width: min(96vw, 1780px); margin-left: calc(50% - min(48vw, 890px)); }

/* ── Animaciones de entrada al hacer scroll (CSS puro, con degradado elegante) ── */
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .viz, .section-inner .table-scroll, .card {
      animation: rise 1ms linear both; animation-timeline: view(); animation-range: entry 0% entry 45%; }
    .bar-fill { animation: reveal 1ms linear both; animation-timeline: view(); animation-range: entry 0% entry 70%; }
    .dot, .dot-label { animation: pop 1ms linear both; animation-timeline: view(); animation-range: entry 0% entry 60%; }
    .stat-num, .donut { animation: rise 1ms linear both; animation-timeline: view(); animation-range: entry 0% entry 50%; }
  }
}
@keyframes rise { from { opacity: 0; transform: translateY(22px); } to { opacity: 1; transform: none; } }
@keyframes reveal { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
@keyframes pop { from { opacity: 0; transform: translate(-50%, 50%) scale(0.3); } to { opacity: 1; transform: translate(-50%, 50%) scale(1); } }
.viz-wide.viz { animation-name: rise; }

/* Dona (conic-gradient) */
.viz-flex { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; margin-top: 1rem; }
.donut { width: 168px; height: 168px; border-radius: 50%; position: relative; flex-shrink: 0;
  background: conic-gradient(var(--red) 0 var(--p), #E8E5E0 var(--p) 100%); }
.donut::before { content: ""; position: absolute; inset: 22px; background: var(--white); border-radius: 50%; }
.donut-center { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; }
.donut-center b { font-family: 'Anton', sans-serif; font-size: 2rem; color: var(--red); display: block; }
.donut-center small { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--gray); }
.donut-side { flex: 1; min-width: 240px; font-size: 0.9rem; color: var(--dark); }

/* Tarjeta versus de arquetipos */
.versus { display: grid; grid-template-columns: 1fr auto 1fr; gap: 0; margin-top: 1rem;
  border: 1px solid var(--gray-border); border-radius: 8px; overflow: hidden; }
.vs-col { padding: 1.4rem 1.5rem; }
.vs-col:first-child { background: var(--red-light); }
.vs-col:last-child { background: rgba(37,99,235,0.05); }
.vs-mid { display: grid; place-content: center; padding: 0 0.8rem; font-family: 'Anton', sans-serif;
  color: var(--gray-light); font-size: 1.2rem; background: var(--white); border-left: 1px solid var(--gray-border); border-right: 1px solid var(--gray-border); }
.vs-title { font-weight: 800; font-size: 1rem; color: var(--black); margin-bottom: 0.9rem; }
.vs-row { font-size: 0.8rem; margin: 0.55rem 0; color: var(--dark); }
.vs-row b { color: var(--black); }
.vs-big { font-family: 'Anton', sans-serif; font-size: 1.5rem; color: var(--red-dark); }
.vs-col:last-child .vs-big { color: var(--blue); }
@media (max-width: 700px) { .versus { grid-template-columns: 1fr; } .vs-mid { border: none; border-top: 1px solid var(--gray-border); border-bottom: 1px solid var(--gray-border); padding: 0.4rem; } }

/* Índice */
.toc { columns: 2; column-gap: 3rem; }
.toc-item { break-inside: avoid; margin-bottom: 1.1rem; }
.toc-item > a { font-weight: 800; color: var(--black); text-decoration: none; font-size: 0.95rem; }
.toc-item > a:hover { color: var(--red); }
.toc-num { font-family: 'Anton', sans-serif; color: var(--red); margin-right: 0.5rem; }
.toc-sub { list-style: none; margin: 0.35rem 0 0 1.6rem !important; }
.toc-sub li { margin: 0.15rem 0 !important; }
.toc-sub a { color: var(--gray); text-decoration: none; font-size: 0.78rem; font-weight: 500; }
.toc-sub a:hover { color: var(--red); }
@media (max-width: 720px) { .toc { columns: 1; } }

/* Tiles de cifras */
.viz-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem; }
.stat { border: 1px solid var(--gray-border); border-radius: 6px; padding: 1rem 1.2rem; background: #FBFAF8; }
.stat-num { font-family: 'Anton', sans-serif; font-size: 1.9rem; color: var(--red); line-height: 1.1; }
.stat-label { font-size: 0.74rem; color: var(--gray); font-weight: 600; margin-top: 0.4rem; }

/* Dispersión impacto × factibilidad */
.scatter { position: relative; height: 340px; margin: 1rem 0 0.4rem; border-left: 2px solid var(--gray-border);
  border-bottom: 2px solid var(--gray-border); background:
  linear-gradient(to right, transparent calc(50% - 1px), var(--gray-border) 50%, transparent calc(50% + 1px)),
  linear-gradient(to top, transparent calc(50% - 1px), var(--gray-border) 50%, transparent calc(50% + 1px)); }
.dot { position: absolute; width: 14px; height: 14px; border-radius: 50%; background: var(--red);
  border: 2px solid var(--white); box-shadow: 0 0 0 1px var(--red-dark); transform: translate(-50%, 50%); }
.dot-label { position: absolute; transform: translate(-50%, 50%); margin-bottom: 14px; font-size: 0.72rem;
  font-weight: 700; color: var(--black); white-space: nowrap; padding-bottom: 16px; }
.ax { position: absolute; font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--gray-light); }

/* Mapa de calor */
.heat th { position: sticky; top: 0; }
.heat td { font-size: 0.72rem; line-height: 1.45; min-width: 112px; padding: 0.5rem 0.6rem; }
.heat td.jug { font-weight: 700; color: var(--black); min-width: 150px; background: var(--white); font-size: 0.76rem; }
.heat tr.sura td { border-top: 2px solid var(--red); border-bottom: 2px solid var(--red); }
.heat tr.sura td.jug { color: var(--red-dark); }
td.h-si  { background: rgba(5,150,105,0.14); }
td.h-lim { background: rgba(180,83,9,0.13); }
td.h-no  { background: rgba(230,51,41,0.12); }
td.h-na  { background: #ECEAE6; color: var(--gray); }
td.h-c3  { background: rgba(37,99,235,0.22); }
td.h-c2  { background: rgba(37,99,235,0.12); }
td.h-c1  { background: rgba(37,99,235,0.05); }

/* Barras horizontales */
.bars { display: grid; gap: 0.55rem; margin-top: 1rem; }
.bar-row { display: grid; grid-template-columns: 210px 1fr; align-items: center; gap: 0.8rem; }
.bar-label { font-size: 0.76rem; font-weight: 600; color: var(--dark); text-align: right; }
.bar-track { position: relative; height: 18px; background: #EFEDE9; border-radius: 4px; margin-right: 96px; }
.bar-fill { position: absolute; top: 0; bottom: 0; background: var(--dark); border-radius: 4px; }
.bar-fill.acc { background: var(--red); }
.bar-val { position: absolute; left: calc(100% + 8px); top: 50%; transform: translateY(-50%);
  font-size: 0.72rem; font-weight: 700; color: var(--black); white-space: nowrap; }
.bar-note { font-size: 0.78rem; color: var(--gray); margin-top: 0.9rem; }
.bar-scale { display: grid; grid-template-columns: 210px 1fr; gap: 0.8rem; margin-top: 0.5rem; }
.bar-scale-track { position: relative; display: flex; justify-content: space-between; margin-right: 96px;
  font-size: 0.7rem; font-weight: 600; color: var(--gray-light); padding-top: 0.35rem;
  border-top: 1px dashed var(--gray-border); }
@media (max-width: 640px) { .bar-row, .bar-scale { grid-template-columns: 120px 1fr; } .bar-label { font-size: 0.7rem; } }
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

    toc = []
    built = [build_section(*s, toc) for s in SECTIONS]
    built.insert(1, build_toc(toc))  # índice después del resumen ejecutivo
    sections_html = "\n\n".join(built)
    start = shell.index('<section id="resumen">')
    end = shell.index("<footer>")
    shell = shell[:start] + sections_html + "\n\n" + shell[end:]

    (DOCS / "index.html").write_text(shell, encoding="utf-8")
    size = (DOCS / "index.html").stat().st_size
    # Espejo en la raíz del repo: GitHub Pages del proyecto está configurado en main:/ (root)
    (ROOT / "index.html").write_text(shell, encoding="utf-8")
    root_assets = ROOT / "assets"
    if root_assets.exists(): shutil.rmtree(root_assets)
    shutil.copytree(assets, root_assets)
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"OK -> docs/index.html y ./index.html ({size/1024:.0f} KB)")

if __name__ == "__main__":
    main()
