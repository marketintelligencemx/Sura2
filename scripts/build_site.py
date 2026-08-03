#!/usr/bin/env python3
"""Build del sitio del estudio PPR · Aldebaran.
Convierte analisis/*.md al one-page docs/index.html usando el shell de plantilla/index.html
y los componentes de branding/tokens.css (badges conf-a/b/c, gap chips, table-scroll).
Uso: python3 scripts/build_site.py
"""
import re, shutil, html, unicodedata
import html as html_mod  # alias: en las funciones de fase 3 el parámetro se llama html
from pathlib import Path

def slug(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]

ROOT = Path(__file__).resolve().parent.parent
ANALISIS, DOCS, BRAND = ROOT / "analisis", ROOT / "docs", ROOT / "branding"

FECHA_CORTE = "31 de julio de 2026"
VERSION = "v1.0"

# Acceso del equipo: SHA-256 de "usuario|contraseña". Para cambiar credenciales:
# python3 -c "import hashlib; print(hashlib.sha256('usuario|contraseña'.encode()).hexdigest())"
AUTH_HASH = "ac5a8e7f36a8a097dd08705fc310e2605a807f022327055eab383aed9ad58783"
SESION_HORAS = 8

GUARD_JS = f"""<script>(function(){{try{{
  var a=sessionStorage.getItem('aldebaran_auth');
  var t=parseInt(sessionStorage.getItem('aldebaran_ts')||'0');
  if(a!=='ok'||!t||(Date.now()-t)>{SESION_HORAS}*60*60*1000){{
    sessionStorage.removeItem('aldebaran_auth');sessionStorage.removeItem('aldebaran_ts');
    location.replace('index.html');
  }}
}}catch(e){{location.replace('index.html');}}}})();</script>"""

def login_html():
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <title>Acceso — Estudio PPR | Aldebaran Consulting</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700;800&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/tokens.css">
  <style>
    body {{ min-height: 100vh; display: grid; place-items: center; padding: 1.5rem; }}
    .login-card {{ background: var(--white); border: 1px solid var(--gray-border); border-radius: 10px;
      padding: 3rem 2.8rem; width: min(430px, 94vw); box-shadow: 0 20px 60px rgba(26,26,26,0.08); }}
    .login-logos {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.2rem; }}
    .login-logos img {{ height: 30px; }} .login-logos img:last-child {{ height: 24px; opacity: 0.9; }}
    .login-eyebrow {{ font-weight: 700; font-size: 0.68rem; text-transform: uppercase;
      letter-spacing: 0.18em; color: var(--red); margin-bottom: 0.8rem; }}
    h1 {{ font-family: 'Anton', sans-serif; font-weight: 400; text-transform: uppercase;
      font-size: 1.9rem; color: var(--black); line-height: 1.1; margin-bottom: 0.6rem; }}
    .login-sub {{ color: var(--gray); font-size: 0.85rem; margin-bottom: 2rem; }}
    label {{ display: block; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.08em; color: var(--gray); margin: 1.1rem 0 0.35rem; }}
    input {{ width: 100%; padding: 0.75rem 0.9rem; border: 1px solid var(--gray-border); border-radius: 6px;
      font-family: 'Montserrat', sans-serif; font-size: 0.95rem; background: #FBFAF8; }}
    input:focus {{ outline: 2px solid var(--red); outline-offset: 0; border-color: var(--red); }}
    button {{ width: 100%; margin-top: 1.6rem; padding: 0.85rem; background: var(--red); color: var(--white);
      border: none; border-radius: 6px; font-family: 'Montserrat', sans-serif; font-weight: 800;
      font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; cursor: pointer; }}
    button:hover {{ background: var(--red-dark); }}
    .login-error {{ display: none; margin-top: 1rem; padding: 0.7rem 0.9rem; border-radius: 6px;
      background: var(--red-light); color: var(--red-dark); font-size: 0.8rem; font-weight: 600; }}
    .login-foot {{ margin-top: 2rem; padding-top: 1.2rem; border-top: 1px solid var(--gray-border);
      font-size: 0.68rem; color: var(--gray-light); }}
  </style>
</head>
<body>
  <form class="login-card" id="f">
    <div class="login-logos">
      <img src="assets/aldebaran-logo.svg" alt="Aldebaran">
      <img src="assets/sura-logo.svg" alt="Sura">
    </div>
    <div class="login-eyebrow">Aldebaran Consulting · Acceso restringido</div>
    <h1>Estudio de mercado<br>Plan Personal de Retiro</h1>
    <p class="login-sub">Documento confidencial preparado para Sura. Ingresa las credenciales proporcionadas por el equipo.</p>
    <label for="u">Usuario</label>
    <input id="u" type="text" autocomplete="username" autocapitalize="none" required>
    <label for="p">Contraseña</label>
    <input id="p" type="password" autocomplete="current-password" required>
    <button type="submit">Entrar al estudio</button>
    <div class="login-error" id="err">Credenciales incorrectas. Verifica con el equipo Aldebaran.</div>
    <div class="login-foot">Sesión válida por {SESION_HORAS} horas · Uso exclusivo del equipo autorizado · © 2026 Aldebaran Consulting</div>
  </form>
  <script>
    const HASH = "{AUTH_HASH}";
    document.getElementById('f').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const u = document.getElementById('u').value.trim().toLowerCase();
      const p = document.getElementById('p').value;
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(u + '|' + p));
      const hex = [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
      if (hex === HASH) {{
        sessionStorage.setItem('aldebaran_auth', 'ok');
        sessionStorage.setItem('aldebaran_ts', String(Date.now()));
        location.replace('estudio.html');
      }} else {{
        document.getElementById('err').style.display = 'block';
        document.getElementById('p').value = '';
      }}
    }});
    try {{
      const a = sessionStorage.getItem('aldebaran_auth');
      const t = parseInt(sessionStorage.getItem('aldebaran_ts') || '0');
      if (a === 'ok' && t && (Date.now() - t) < {SESION_HORAS}*60*60*1000) location.replace('estudio.html');
    }} catch (e) {{}}
  </script>
</body>
</html>"""

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

# (num, título corto, ancla, la pregunta de negocio que responde, escala del capítulo)
MAPA = [
    ("01", "Macro", "macro", "¿De qué tamaño es el terreno y por qué existe este mercado?",
     "El sistema de retiro, la brecha de pensión y el subsidio fiscal que paga el Estado"),
    ("02", "Industria", "meso", "¿Quién juega, cómo fabrica el producto y qué cobra?",
     "Arquetipos, matriz de 24 jugadores, canales y anatomía del costo"),
    ("03", "Competidores", "micro", "¿Cómo es cada jugador por dentro y cuánto le paga a quien vende?",
     "11 fichas al detalle y la tabla maestra de comisiones y bonos al canal"),
    ("04", "Desempleo", "desempleo", "¿Existe cobertura de desempleo en un PPR, aquí o en el mundo?",
     "El veredicto del Alcance B, la evidencia mexicana y el benchmark internacional"),
    ("05", "Sura", "sintesis", "¿Qué debe hacer Sura, en qué orden y con qué riesgos?",
     "Brechas contra el mercado, espacios en blanco y cinco oportunidades priorizadas"),
]

# (etiqueta, minutos, para quién, [(ancla, qué leer)])
RUTAS = [
    ("Directivo", "15 min", "Necesitas la conclusión y la decisión, no el sustento.",
     [("resumen", "Resumen ejecutivo"),
      ("5-2-espacios-en-blanco-del-mercado-y-el-derecho-a-ganar-de-s", "5.2 Espacios en blanco"),
      ("5-3-las-cinco-oportunidades-priorizadas-por-impacto-factibil", "5.3 Las cinco oportunidades")]),
    ("Comercial y producto", "40 min", "Vas a discutir precio, canal o diseño de producto.",
     [("resumen", "Resumen ejecutivo"),
      ("2-1-los-tres-arquetipos-de-producto-esto-ordena-todo-el-estu", "2.1 Los tres arquetipos"),
      ("2-6-la-familia-extendida-el-ppr-es-un-regimen-fiscal-montado", "2.6 La familia extendida"),
      ("3-12-deep-dive-comisiones-y-bonos-al-canal-la-tabla-maestra", "3.12 Comisiones al canal"),
      ("4-1-el-veredicto-primero", "4.1 Veredicto de desempleo"),
      ("sintesis", "05 Síntesis completa")]),
    ("Análisis y verificación", "2.5 hrs", "Vas a auditar las cifras o a construir sobre ellas.",
     [("macro", "Todo el estudio, de 01 a 05"),
      ("anexos", "06 Anexos: metodología y limitaciones"),
      ("referencias-por-seccion", "Referencias por sección")]),
]

def build_mapa():
    pasos = ""
    for i, (num, corto, sid, pregunta, escala) in enumerate(MAPA):
        flecha = '<div class="mapa-arrow" aria-hidden="true"></div>' if i else ""
        pasos += (f'{flecha}<a class="mapa-step" href="#{sid}">'
                  f'<span class="mapa-num">{num}</span>'
                  f'<span class="mapa-name">{corto}</span>'
                  f'<span class="mapa-q">{pregunta}</span>'
                  f'<span class="mapa-scope">{escala}</span></a>')
    return (f'<div class="viz mapa-wrap"><div class="viz-title nav-aid">Cómo está construido el estudio</div>'
            f'<div class="viz-sub">De lo general a lo particular. Cada capítulo responde una pregunta de negocio '
            f'y se apoya en el anterior: el terreno primero, la decisión al final.</div>'
            f'<div class="mapa">{pasos}</div>'
            f'<div class="bar-note">Los anexos (06) no forman parte de la secuencia: guardan la metodología, '
            f'las limitaciones declaradas, el glosario y todas las referencias por sección.</div></div>')

def build_rutas():
    cards = ""
    for label, mins, quien, pasos in RUTAS:
        lis = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in pasos)
        cards += (f'<div class="ruta"><div class="ruta-top"><span class="ruta-label">{label}</span>'
                  f'<span class="ruta-time">{mins}</span></div>'
                  f'<p class="ruta-who">{quien}</p><ol class="ruta-list">{lis}</ol></div>')
    return (f'<div class="viz"><div class="viz-title nav-aid">Tres rutas de lectura: elige la tuya</div>'
            f'<div class="viz-sub">El estudio completo son 31,500 palabras. No hace falta leerlo entero para usarlo. '
            f'Cada ruta lleva a las mismas conclusiones con distinto nivel de sustento debajo.</div>'
            f'<div class="rutas">{cards}</div></div>')

# ═══ FASE 3 · Figuras numeradas, glosario emergente y tablas plegables ═══

def numerar_figuras(html):
    """Prefija cada visual con 'Figura N' y devuelve el índice para los anexos."""
    figs = []
    def rep(m):
        figs.append(m.group(1))
        n = len(figs)
        return (f'<div class="viz-title" id="figura-{n}">'
                f'<span class="fig-n">Figura {n}</span>{m.group(1)}</div>')
    html = re.sub(r'<div class="viz-title">(.*?)</div>', rep, html, flags=re.S)
    filas = "".join(f'<li><a href="#figura-{i}"><span class="fig-n">Figura {i}</span>{t}</a></li>'
                    for i, t in enumerate(figs, 1))
    return html, f'<ol class="figlist">{filas}</ol>'

def leer_glosario():
    """Lee el glosario de los anexos: es la única fuente de las definiciones emergentes."""
    md = (ANALISIS / "06-anexos.md").read_text(encoding="utf-8")
    m = re.search(r"^## D\. Glosario\s*(.*?)(?=^## |\Z)", md, flags=re.S | re.M)
    entradas = {}
    if m:
        for lab, defi in re.findall(r"^- \*\*(.+?):?\*\*\s*(.+?)$", m.group(1), flags=re.M):
            entradas[lab.strip()] = re.sub(r"\*\*(.+?)\*\*", r"\1", defi.strip())
    return entradas

# (patrón que se busca en el texto, etiqueta con la que empieza la entrada del glosario)
TERMINOS = [
    (r"valor de rescate", "Valor de rescate"), (r"valor en efectivo", "Valor en efectivo"),
    (r"seguro prorrogado", "Seguro prorrogado"), (r"suma asegurada", "Suma asegurada"),
    (r"dotal(?:es)?", "Dotal"), (r"tasa de reemplazo", "Tasa de reemplazo"),
    (r"trail", "Trail"), (r"clawback", "Clawback"), (r"persistencia", "Persistencia"),
    (r"glide path", "Glide path"), (r"DICI", "DICI"), (r"UMA", "UMA"), (r"MDRT", "MDRT"),
    (r"PPI", "PPI"), (r"RECAS", "RECAS"), (r"deducibilidad", "Deducibilidad"),
    (r"bono de producción", "Bono de producción"),
    (r"comisión de distribución", "Comisión de distribución"),
    (r"waiver of (?:premium|contribution)", "Waiver of premium"),
]

# Etiquetas dentro de las cuales NO se anota: rompería enlaces, títulos o el layout de tablas
_NO_ANOTAR = {"a", "h1", "h2", "h3", "h4", "h5", "abbr", "table", "script", "style"}

def anotar_glosario(html, gloss):
    """Marca la PRIMERA aparición de cada término con su definición emergente."""
    pares = []
    for pat, lab in TERMINOS:
        d = next((v for k, v in gloss.items() if k.startswith(lab)), None)
        if d:
            pares.append((re.compile(rf"(?<![\w-]){pat}(?![\w-])", re.I), html_mod.escape(d, quote=True)))
    pendientes = list(pares)
    partes = re.split(r"(<[^>]+>)", html)
    pila = []
    for i, parte in enumerate(partes):
        if parte.startswith("<"):
            m = re.match(r"</?([a-zA-Z0-9]+)", parte)
            if m:
                tag = m.group(1).lower()
                if parte.startswith("</"):
                    if pila and pila[-1] == tag: pila.pop()
                elif not parte.endswith("/>") and tag in _NO_ANOTAR:
                    pila.append(tag)
            continue
        if pila or not parte.strip() or not pendientes:
            continue
        for rx, d in list(pendientes):
            nuevo, n = rx.subn(lambda mm: f'<abbr class="gl" tabindex="0" data-def="{d}">{mm.group(0)}</abbr>',
                               parte, count=1)
            if n:
                parte = nuevo
                pendientes.remove((rx, d))
        partes[i] = parte
    return "".join(partes)

def plegar_tablas(html, umbral=12):
    """Recorta las tablas muy largas con un botón para desplegarlas. El contenido sigue en el DOM."""
    def rep(m):
        bloque, filas = m.group(0), m.group(0).count("<tr>") - 1
        if filas <= umbral:
            return bloque
        return (f'<div class="plegable" data-filas="{filas}">{bloque}'
                f'<button class="plg-btn" type="button">Ver las {filas} filas completas</button></div>')
    return re.sub(r'<div class="table-scroll[^"]*">.*?</table></div>', rep, html, flags=re.S)

PLEGABLE_JS = """<script>(function(){
  // Glosario: si la definición se saldría por la derecha, se ancla al otro lado del término
  function flip(e){
    var el=e.currentTarget, r=el.getBoundingClientRect();
    el.classList.toggle('gl-der', r.left+440 > document.documentElement.clientWidth);
  }
  document.querySelectorAll('abbr.gl').forEach(function(a){
    a.addEventListener('mouseenter',flip); a.addEventListener('focus',flip);
  });
  document.querySelectorAll('.plegable').forEach(function(box){
    var b=box.querySelector('.plg-btn');
    b.addEventListener('click',function(){
      var open=box.classList.toggle('abierto');
      b.textContent=open?'Contraer la tabla':'Ver las '+box.dataset.filas+' filas completas';
    });
  });
})();</script>"""

def build_toc(toc):
    items = ""
    for num, title, sid, subs in toc:
        subhtml = ""
        if subs and num != "00":
            lis = "".join(f'<li><a href="#{s}">{t}</a></li>' for s, t in subs[:8])
            subhtml = f'<ul class="toc-sub">{lis}</ul>'
        items += f'<div class="toc-item"><a href="#{sid}"><span class="toc-num">{num}</span>{title}</a>{subhtml}</div>'
    return (f'<section id="indice" style="background:var(--white)"><div class="section-inner">\n'
            f'<div class="section-num">··</div><h2 class="section-title">Cómo leer este estudio</h2>\n'
            f'<p class="section-lead">De macro a micro: el terreno, la industria, cada competidor al detalle, el capítulo especial de desempleo y la síntesis accionable. Metodología y referencias completas al final.</p>'
            f'{build_mapa()}\n{build_rutas()}\n'
            f'<h3 id="indice-detallado">Índice detallado</h3>\n'
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
<div class="viz-sub">El color resume el dato documentado en cada celda desde la perspectiva del AHORRADOR; el chip repite el veredicto para lectura sin color. La columna "Pago al canal" mide otra cosa (cuánto gana el asesor) y por eso usa azul. Fila de Sura enmarcada en rojo. Fuentes: fichas 3.1-3.11 y Gran Matriz de la sección 02.</div>
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

def _wrap(title, sub, body, note, wide=False):
    cls = "viz viz-wide" if wide else "viz"
    return (f'<div class="{cls}"><div class="viz-title">{title}</div><div class="viz-sub">{sub}</div>'
            f'{body}<div class="bar-note">{note}</div></div>')

# ── 01 · Los tres pisos del retiro y dónde vive el PPR ──
def viz_pilares():
    pisos = [
        ("Piso 3", "Ahorro voluntario", "El PPR", "El propio ahorrador, con subsidio fiscal",
         f"Deducible hasta <b>$213,973.20</b> en 2026, con devolución de hasta 35% {_b('A')}", 1),
        ("Piso 2", "Contributivo obligatorio", "La Afore", "Trabajador, patrón y Estado",
         f"Repone en promedio <b>55.5%</b> del último sueldo, contra el 70% que la OCDE considera deseable {_b('A')}", 0),
        ("Piso 1", "No contributivo", "Pensión y Fondo de Pensiones para el Bienestar", "El Estado",
         f"Complementa <b>solo hasta $17,885.85</b> mensuales {_b('A')}", 0),
    ]
    filas = ""
    for etiqueta, tipo, nombre, quien, alcance, acc in pisos:
        filas += (f'<div class="piso{" piso-acc" if acc else ""}">'
                  f'<div class="piso-tag">{etiqueta}<span>{tipo}</span></div>'
                  f'<div class="piso-main"><b>{nombre}</b><span class="piso-quien">Lo paga: {quien}</span></div>'
                  f'<div class="piso-alcance">{alcance}</div></div>')
    corte = ('<div class="piso-corte"><span>Techo de la red estatal: $17,885.85 al mes</span>'
             '<p>Arriba de ese ingreso, el complemento público ya no crece. Ahí empieza el cliente del PPR: '
             'no es quien no tiene pensión, es quien tiene una que no le alcanza.</p></div>')
    return _wrap("¿De dónde sale el mercado del PPR? Los tres pisos del retiro en México",
        "El PPR no compite con la Afore ni con la pensión pública: se monta encima de ellas para cubrir lo que ninguna alcanza.",
        f'<div class="pisos">{filas}{corte}</div>',
        "Fuentes: OCDE Pensions at a Glance 2023 (tasa de reemplazo); IMSS 2026 (tope del complemento); LISR y UMA 2026 (tope deducible). "
        "El detalle de cada piso está en 1.2 y el cálculo de la brecha en 1.3.")

# ── 02 · La anatomía de un peso aportado ──
def viz_peso():
    compuertas = [
        ("1", "Costo de adquisición", "Lo que cobra quien te vendió el plan",
         f"<b>40% a 50%</b> de la prima del año 1 {_b('C')}✓", f"<b>$0</b>: no hay comisión de entrada {_b('A')}"),
        ("2", "Costo de la protección", "Lo que cuesta el seguro de vida embebido",
         f"Según edad, en la tabla de la póliza, <b>que no es pública</b> {_b('A')}", "No aplica: no hay protección incluida"),
        ("3", "Administración anual", "Lo que se cobra cada año por operar el plan",
         f"Embebido en la prima, <b>sin desglose público</b> {_b('A')}", f"<b>1.00% a 2.46%</b> visible en el DICI {_b('A')}"),
        ("4", "Salida anticipada", "Lo que pierdes si necesitas tu dinero antes",
         f"Rescate cercano a <b>$0</b> los primeros 3 años {_b('B')}", f"<b>$0</b>: liquidez diaria sin castigo propio {_b('A')}"),
    ]
    filas = ""
    for n, nombre, que, seguro, fondo in compuertas:
        filas += (f'<div class="cp-row"><div class="cp-n">{n}</div>'
                  f'<div class="cp-name"><b>{nombre}</b><span>{que}</span></div>'
                  f'<div class="cp-seg cp-seguro">{seguro}</div>'
                  f'<div class="cp-seg cp-fondo">{fondo}</div></div>')
    head = ('<div class="cp-row cp-head"><div></div><div></div>'
            '<div class="cp-seg">Si es un PPR-seguro</div><div class="cp-seg">Si es un PPR-fondo</div></div>')
    fiscal = ('<div class="cp-fiscal"><b>Y en sentido contrario, lo que el Estado te devuelve:</b> '
              f'hasta <b>35%</b> de lo aportado al deducir, con tope de $213,973.20 en 2026 {_b("A")}. '
              f'Pero si retiras antes de los 65 años, el SAT retiene <b>20%</b> {_b("A")}. '
              'Ese castigo es del SAT, no del emisor, y el ahorrador promedio no distingue uno del otro.</div>')
    return _wrap("La anatomía de un peso aportado: por dónde se va antes de llegar a tu ahorro",
        "Todo peso que entra a un PPR cruza las mismas cuatro compuertas. Lo que cambia entre arquetipos no es cuántas hay, sino cuáles puedes ver.",
        f'<div class="compuertas">{head}{filas}</div>{fiscal}',
        "El desglose completo de cada cargo está en la tabla de anatomía del costo de esta misma sección, y la economía del canal en 3.12. "
        "Advertencia de método: ningún emisor del arquetipo seguro publica el desglose; por eso la columna de la izquierda tiene celdas sin cifra en vez de estimaciones.",
        wide=True)

# ── 02 · El árbol de las cuatro familias ──
def viz_familias():
    ramas = [
        ("Retiro deducible", "El PPR", "Art. 151-V · 185 · 93", "20 a 40 años", "$500 a $18,000 al año", 1),
        ("Ahorro no deducible", "El dotal", "Art. 93", "5 a 20 años", "desde $1,000 de prima", 0),
        ("Vida entera", "Protección vitalicia", "Art. 93", "hasta los 99-101 años", "desde $500 de prima", 0),
        ("Ahorro educativo", "El plan para los hijos", "Art. 93", "5 a 23 años", "desde $60,000 de suma asegurada", 0),
    ]
    cards = ""
    for nombre, apodo, arts, plazo, entrada, acc in ramas:
        cards += (f'<div class="rama{" rama-acc" if acc else ""}">'
                  f'<div class="rama-name">{nombre}</div><div class="rama-apodo">{apodo}</div>'
                  f'<div class="rama-meta"><span>Régimen fiscal</span>{arts}</div>'
                  f'<div class="rama-meta"><span>Plazo típico</span>{plazo}</div>'
                  f'<div class="rama-meta"><span>Entrada mínima</span>{entrada}</div></div>')
    tronco = ('<div class="tronco"><div class="tronco-in">'
              '<span class="tronco-eyebrow">El mismo motor técnico</span>'
              '<b>Un dotal</b>'
              '<p>Prima que compra protección más ahorro garantizado, valor en efectivo, seguro prorrogado '
              'y aportaciones adicionales. Idéntico en las cuatro familias.</p></div></div>')
    return _wrap("El PPR no es un producto: es una etiqueta fiscal sobre un dotal",
        "Cuatro familias comerciales que la industria vende por separado comparten la misma arquitectura. Lo único que cambia es el artículo de la LISR que se invoca y el plazo.",
        f'<div class="arbol">{tronco}<div class="ramas">{cards}</div></div>',
        f"Levantamiento propio Aldebaran, 9 emisores, 4 familias, cortes abr-2023 a abr-2025 {_b('B')}. "
        "Consecuencia para el tamaño de mercado: el universo direccionable no son los 39 autorizados del SAT, es todo el ahorro con vida. "
        "La puerta de entrada de la categoría es el producto educativo y el dotal corto, no el PPR.")

# ── 02 · Rendimiento real contra plazo ──
def viz_plazo():
    YMAX, YMIN, XMAX = 4.0, -5.0, 40.0
    y = lambda v: (YMAX - v) / (YMAX - YMIN) * 100
    x = lambda p: p / XMAX * 100
    # (serie, clase, plazo, lo, hi, etiqueta, lado, ancla vertical de la etiqueta)
    pts = [
        ("Educativo", "s-edu", 8, -3.4, -3.4, "8 años: −3.4%", "der", "mid"),
        ("Educativo", "s-edu", 18, -1.4, -1.4, "18 años: −1.4%", "der", "mid"),
        ("Ahorro", "s-aho", 10, -0.6, -0.6, "10 años: −0.6%", "izq", "mid"),
        ("Ahorro", "s-aho", 20, 2.6, 2.6, "20 años: +2.6%", "der", "mid"),
        ("Retiro", "s-ret", 15, -4.2, -0.8, "15 años: −0.8% a −4.2%", "der", "mid"),
        # anclada al extremo superior: en el punto medio caería justo encima de la línea de cero
        ("Retiro", "s-ret", 35, -1.8, 1.7, "35 años: +1.7% a −1.8%", "izq", "hi"),
    ]
    marks = ""
    for serie, cls, plazo, lo, hi, lab, lado, ancla in pts:
        left = x(plazo)
        if lo != hi:
            top, h = y(hi), y(lo) - y(hi)
            marks += (f'<div class="pl-range {cls}" style="left:{left:.1f}%;top:{top:.1f}%;height:{h:.1f}%"></div>'
                      f'<div class="pl-dot {cls}" style="left:{left:.1f}%;top:{y(hi):.1f}%"></div>'
                      f'<div class="pl-dot {cls}" style="left:{left:.1f}%;top:{y(lo):.1f}%"></div>')
            ty = y(hi) if ancla == "hi" else (y(lo) if ancla == "lo" else (y(hi) + y(lo)) / 2)
        else:
            marks += f'<div class="pl-dot {cls}" style="left:{left:.1f}%;top:{y(hi):.1f}%"></div>'
            ty = y(hi)
        marks += f'<div class="pl-lab pl-{lado} {cls}" style="left:{left:.1f}%;top:{ty:.1f}%">{lab}</div>'
    grid = "".join(f'<div class="pl-gl" style="top:{y(v):.1f}%"><span>{v:+g}%</span></div>'
                   for v in (4, 2, 0, -2, -4))
    xs = "".join(f'<span style="left:{x(p):.1f}%">{p}</span>' for p in (0, 10, 20, 30, 40))
    leg = ('<div class="viz-legend">'
           '<span><i class="lg s-ret"></i>Retiro deducible (PPR)</span>'
           '<span><i class="lg s-aho"></i>Ahorro no deducible</span>'
           '<span><i class="lg s-edu"></i>Ahorro educativo</span>'
           '<span><i class="lg lg-line"></i>Línea de cero: ni gana ni pierde poder adquisitivo</span></div>')
    plot = (f'<div class="plazo"><div class="pl-area">{grid}'
            f'<div class="pl-zero" style="top:{y(0):.1f}%"></div>{marks}</div>'
            f'<div class="pl-x">{xs}</div>'
            f'<div class="pl-xtitle">Plazo del plan, en años</div></div>')
    return _wrap("El hallazgo más contraintuitivo: a plazo corto, el ahorro garantizado pierde poder adquisitivo",
        "Rendimiento real anual implícito en las ilustraciones que los propios emisores publican, es decir ya descontada la inflación. "
        "Arriba de la línea de cero el ahorrador gana poder adquisitivo; abajo, aporta más de lo que recibe.",
        plot + leg,
        f"Cálculo Aldebaran sobre ilustraciones de prima contra monto meta del levantamiento propio {_b('B')}, con inflación de 3.5%, "
        "el supuesto que el propio material usa. Los dos casos de retiro se muestran como rango porque la ilustración no declara si sus primas "
        "son niveladas o indexadas 🔍; bajo cualquiera de las dos lecturas el resultado queda por debajo de la inflación. "
        "La causa del patrón: los gastos de adquisición se amortizan en más años conforme el plazo crece.")

# ── 03 · El circuito del dinero: mismo cliente, dos destinos ──
def viz_circuito():
    rutas = [
        ("PPR-seguro", "cir-seg", "$47,000 a $60,000", "en los primeros 24 meses",
         f"40-50% de la prima del año 1, más renovaciones {_b('C')}✓",
         "$77,000 a $95,000", "Rescate cercano a $0 los primeros 3 años", 1),
        ("PPR-fondo", "cir-fon", "$1,200 a $1,800", "en los primeros 24 meses",
         f"Trail de 0.4% a 0.6% sobre el saldo, sin comisión de entrada {_b('B')}",
         "$100,000 a $150,000", "Liquidez diaria, sin castigo de salida", 0),
    ]
    cols = ""
    for nombre, cls, monto, cuando, como, largo, cliente, acc in rutas:
        cols += (f'<div class="cir-col {cls}{" cir-acc" if acc else ""}">'
                 f'<div class="cir-tag">{nombre}</div>'
                 f'<div class="cir-big">{monto}</div><div class="cir-when">{cuando}</div>'
                 f'<div class="cir-how">{como}</div>'
                 f'<div class="cir-foot"><span>A 20 años</span>{largo}</div>'
                 f'<div class="cir-foot"><span>Mientras tanto, el cliente</span>{cliente}</div></div>')
    return _wrap("El circuito del dinero: por qué el canal empuja un arquetipo y no el otro",
        "Mismo cliente, misma aportación de $100,000 al año, dos productos. Lo que cambia no es lo que gana el ahorrador: es cuándo cobra quien se lo vendió.",
        f'<div class="circuito"><div class="cir-src"><b>El cliente aporta</b><em>$100,000</em><span>al año</span></div>'
        f'<div class="cir-cols">{cols}</div></div>'
        '<div class="cir-punch"><b>25 a 50 veces más</b> gana el asesor en los primeros dos años vendiendo un seguro que un fondo, '
        'por exactamente el mismo dinero del cliente. Esa es la explicación completa de por qué el canal tradicional no vende fondos: '
        'no es preferencia de producto, es nómina.</div>',
        "Cálculo Aldebaran con la aritmética visible en la tabla maestra de esta sección. Los insumos del arquetipo seguro son nivel C triangulado "
        "(borrador, vacantes y referencias sectoriales); los del arquetipo fondo son nivel A y B (DICI de Principal, página de asesores de GBM). "
        "Nota que a 20 años el trail paga más en pesos nominales: el problema no es el monto total, es que llega en los años 8 a 20.",
        wide=True)

# ── 04 · La línea de vida del ahorrador que pierde el empleo ──
def viz_vida_desempleo():
    hitos = [
        ("Año 0", "Contrata el plan", "Empieza a pagar primas y a acumular valor en efectivo.", "ok"),
        ("Años 1 al fin del pago", "La ventana desprotegida", "El retiro parcial <b>todavía no está disponible</b>: solo se habilita al terminar el periodo de pago. "
         "Quien pierde el empleo en el año 4 de un plan a 20 no tiene acceso a nada de esto.", "mal"),
        ("El evento", "Pierde el empleo", "Lo que el mercado ofrece hoy: pausar aportaciones, préstamo automático de prima "
         "con intereses contra su propio ahorro, o rescatar con castigo.", "evento"),
        ("Tras el periodo de pago", "Retiro parcial del valor en efectivo", "Máximo <b>3 retiros</b> en toda la vigencia, de hasta <b>50%</b> del valor en efectivo, "
         "y <b>la protección por fallecimiento se reduce en la misma proporción</b>.", "mal"),
        ("Desde los 60 años", "Un retiro por año póliza", "La liquidez se abre justo cuando el riesgo de desempleo ya bajó.", "tibio"),
    ]
    filas = ""
    for cuando, titulo, texto, tono in hitos:
        filas += (f'<div class="hito hito-{tono}"><div class="hito-when">{cuando}</div>'
                  f'<div class="hito-body"><b>{titulo}</b><p>{texto}</p></div></div>')
    veredicto = ('<div class="hito-veredicto"><b>En ningún punto de la línea hay transferencia de riesgo.</b> '
                 'La industria ya identificó la contingencia y le puso nombre comercial, pero la respuesta que ofrece es '
                 'autoseguro con penalización: el ahorrador financia su propia emergencia con su propio ahorro y pierde '
                 'cobertura justo cuando su familia queda más expuesta.</div>')
    return _wrap("Qué le pasa hoy al ahorrador mexicano que pierde el empleo",
        "Recorrido por la vida de una póliza de ahorro con seguro. En rojo, los tramos donde el producto no responde.",
        f'<div class="hitos">{filas}{veredicto}</div>',
        f"Condiciones del retiro parcial: levantamiento propio Aldebaran, corte feb-2024 {_b('B')}. "
        f"Ausencia de cobertura de desempleo: verificada en condiciones generales registradas ante CNSF {_b('A')}, con 0 menciones de "
        "\"desempleo\" en el clausulado de dos emisores. El comparable que prueba que el riesgo sí se asegura en México está en 4.2.2.")

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
        "Rango publicado o documentado en prospectos, DICI y condiciones registradas. Barra roja: Sura.",
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
            '<div class="vs-row"><b>Qué compra el ahorrador:</b> protección (vida, invalidez) + disciplina forzada + garantías en UDIs/USD</div>'
            '<div class="vs-row"><b>Costo:</b> embebido en la prima, opaco por diseño ' + _b("A") + '</div>'
            '<div class="vs-row"><b>Si cancela pronto:</b> valor de rescate cercano a $0 los primeros 3 años ' + _b("A") + '</div>'
            '<div class="vs-row"><b>Quién lo empuja:</b> 40,000+ agentes y promotorías</div></div>')
    right = ('<div class="vs-col"><div class="vs-title">PPR-fondo (y el digital)</div>'
             '<div class="vs-row"><span class="vs-big">0.4-1.2%</span><br>anual sobre saldo gana el canal, recurrente ' + _b("A") + '/' + _b("B") + '</div>'
             '<div class="vs-row"><b>Qué compra el ahorrador:</b> inversión pura, portafolios transparentes, liquidez diaria</div>'
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
       "scatter-oportunidades": viz_oportunidades,
       # Diagramas conceptuales
       "pilares-retiro": viz_pilares, "anatomia-peso": viz_peso,
       "arbol-familias": viz_familias, "rendimiento-plazo": viz_plazo,
       "circuito-dinero": viz_circuito, "vida-desempleo": viz_vida_desempleo}

KPIS = """<div class="kpi-inner">
  <div><div class="kpi-num"><em>$213,973</em></div><div class="kpi-label">Deducible por persona en 2026 (5 UMA) <span class="conf conf-a">A</span></div></div>
  <div><div class="kpi-num">39</div><div class="kpi-label">Instituciones autorizadas por SAT <span class="conf conf-a">A</span></div></div>
  <div><div class="kpi-num">25-50×</div><div class="kpi-label">Lo que gana el asesor con un PPR-seguro vs. fondo (24 meses) <span class="conf conf-c">C</span></div></div>
  <div><div class="kpi-num"><em>$39 mil M</em></div><div class="kpi-label">Drenados de Afores por desempleo en 2025 <span class="conf conf-b">B</span></div></div>
  <div><div class="kpi-num">0</div><div class="kpi-label">PPR con cobertura de desempleo en México (veredicto Alcance B) <span class="conf conf-a">A</span></div></div>
</div>"""

def build_rail():
    """Barra de progreso de lectura, anclada bajo el menú fijo."""
    return ('<div class="progress" aria-hidden="true"><div class="progress-fill"></div>'
            '<span class="progress-pct">0%</span></div>')

# Progreso de lectura + resaltado de la sección activa en el menú superior (que ya es fijo).
# Sin dependencias externas y sin muebles nuevos que se encimen con el contenido.
RAIL_JS = """<script>(function(){
  var fill=document.querySelector('.progress-fill');
  var pct=document.querySelector('.progress-pct');
  var links=[].slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  var secs=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
  var tick=false;
  function upd(){
    tick=false;
    var h=document.documentElement;
    var max=h.scrollHeight-h.clientHeight;
    var p=max>0?(h.scrollTop/max)*100:0;
    if(fill) fill.style.width=p+'%';
    if(pct) pct.textContent=Math.round(p)+'%';
    var mid=h.scrollTop+h.clientHeight*0.35, cur=-1;
    for(var i=0;i<secs.length;i++){ if(secs[i]&&secs[i].offsetTop<=mid) cur=i; }
    for(var j=0;j<links.length;j++) links[j].classList.toggle('on',j===cur);
  }
  addEventListener('scroll',function(){ if(!tick){tick=true;requestAnimationFrame(upd);} },{passive:true});
  addEventListener('resize',upd); upd();
})();</script>"""

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

/* ── Barra de progreso de lectura, bajo el menú fijo ── */
.progress { position: fixed; top: 52px; left: 0; right: 0; height: 3px; z-index: 99;
  background: rgba(0,0,0,0.07); pointer-events: none; }
.progress-fill { height: 100%; width: 0; background: var(--red); transition: width 90ms linear; }
.progress-pct { position: absolute; right: 0.8rem; top: 5px; font-size: 0.62rem; font-weight: 700;
  color: var(--gray-light); letter-spacing: 0.04em; }
@media (max-width: 760px) { .progress-pct { display: none; } }

/* Sección activa resaltada en el menú superior */
.nav-links a.on { color: var(--red); font-weight: 800; box-shadow: inset 0 -2px 0 var(--red); }

/* ── Mapa del estudio (secuencia macro → micro) ── */
.mapa { display: grid; grid-template-columns: repeat(5, 1fr); align-items: stretch; gap: 0; margin-top: 1rem; }
.mapa-step { display: grid; align-content: start; gap: 0.3rem; padding: 1rem 1.1rem; text-decoration: none;
  border: 1px solid var(--gray-border); border-radius: 7px; background: #FBFAF8; transition: all 140ms ease; }
.mapa-step:hover { background: var(--white); border-color: var(--red); transform: translateY(-2px); }
.mapa-num { font-family: 'Anton', sans-serif; font-size: 1.5rem; color: var(--red); line-height: 1; }
.mapa-name { font-weight: 800; font-size: 0.9rem; color: var(--black); }
.mapa-q { font-size: 0.78rem; color: var(--dark); font-weight: 600; line-height: 1.4; margin-top: 0.15rem; }
.mapa-scope { font-size: 0.71rem; color: var(--gray); line-height: 1.4; }
.mapa-arrow { align-self: center; width: 22px; height: 8px; flex-shrink: 0;
  background: linear-gradient(to right, var(--gray-border) 0 60%, transparent 60%);
  position: relative; }
.mapa-arrow::after { content: ""; position: absolute; right: 2px; top: 50%; transform: translateY(-50%);
  border-left: 6px solid var(--gray-border); border-top: 4px solid transparent; border-bottom: 4px solid transparent; }
.mapa-wrap .mapa { grid-template-columns: 1fr 22px 1fr 22px 1fr 22px 1fr 22px 1fr; }
@media (max-width: 1000px) { .mapa-wrap .mapa { grid-template-columns: 1fr; gap: 0.5rem; }
  .mapa-arrow { display: none; } }

/* ── Rutas de lectura ── */
.rutas { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
.ruta { border: 1px solid var(--gray-border); border-radius: 7px; padding: 1.1rem 1.2rem; background: #FBFAF8; }
.ruta-top { display: flex; align-items: baseline; justify-content: space-between; gap: 0.5rem; }
.ruta-label { font-weight: 800; font-size: 0.92rem; color: var(--black); }
.ruta-time { font-family: 'Anton', sans-serif; font-size: 1rem; color: var(--red); }
.ruta-who { font-size: 0.76rem; color: var(--gray); margin: 0.3rem 0 0.7rem !important; line-height: 1.45; }
.ruta-list { list-style: decimal; margin: 0 0 0 1.1rem !important; padding: 0; }
.ruta-list li { margin: 0.28rem 0 !important; }
.ruta-list a { font-size: 0.79rem; color: var(--dark); text-decoration: none; font-weight: 600; }
.ruta-list a:hover { color: var(--red); text-decoration: underline; }

/* Impresión: el andamiaje de navegación no viaja al papel */
@media print { .progress, nav { display: none !important; } }

/* ═══ DIAGRAMAS CONCEPTUALES ═══ */
/* Series categóricas (validadas para daltonismo sobre fondo blanco) */
.s-ret, .lg.s-ret { background: #E63329; } .s-aho, .lg.s-aho { background: #2563EB; }
.s-edu, .lg.s-edu { background: #B45309; }
.lg-line { background: repeating-linear-gradient(90deg, var(--gray-light) 0 4px, transparent 4px 8px); }

/* ── 01 · Pisos del retiro ── */
.pisos { display: grid; gap: 0.5rem; margin-top: 1rem; }
.piso { display: grid; grid-template-columns: 190px 260px 1fr; gap: 1rem; align-items: center;
  border: 1px solid var(--gray-border); border-left: 4px solid var(--gray-light);
  border-radius: 6px; padding: 0.85rem 1.1rem; background: #FBFAF8; }
.piso-acc { border-left-color: var(--red); background: var(--red-light); }
.piso-tag { font-family: 'Anton', sans-serif; font-size: 1rem; color: var(--gray); line-height: 1.15; }
.piso-tag span { display: block; font-family: 'Poppins', sans-serif; font-size: 0.68rem;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--gray-light); }
.piso-acc .piso-tag { color: var(--red-dark); }
.piso-main b { display: block; font-size: 0.92rem; color: var(--black); }
.piso-quien { font-size: 0.73rem; color: var(--gray); }
.piso-alcance { font-size: 0.82rem; color: var(--dark); line-height: 1.5; }
.piso-corte { border: 1px dashed var(--red); border-radius: 6px; padding: 0.8rem 1.1rem; background: var(--white); }
.piso-corte span { font-family: 'Anton', sans-serif; color: var(--red); font-size: 0.95rem; }
.piso-corte p { margin: 0.25rem 0 0 !important; font-size: 0.82rem; color: var(--dark); }
@media (max-width: 900px) { .piso { grid-template-columns: 1fr; gap: 0.35rem; } }

/* ── 02 · Compuertas del peso aportado ── */
.compuertas { display: grid; gap: 0.4rem; margin-top: 1rem; }
.cp-row { display: grid; grid-template-columns: 34px 250px 1fr 1fr; gap: 0.8rem; align-items: stretch; }
.cp-head .cp-seg { background: var(--black); color: var(--white); font-weight: 800;
  font-size: 0.78rem; text-align: center; padding: 0.45rem; border: none; }
.cp-n { font-family: 'Anton', sans-serif; font-size: 1.3rem; color: var(--red);
  display: grid; place-content: center; }
.cp-name { display: grid; align-content: center; }
.cp-name b { font-size: 0.86rem; color: var(--black); }
.cp-name span { font-size: 0.73rem; color: var(--gray); line-height: 1.4; }
.cp-seg { font-size: 0.8rem; line-height: 1.5; color: var(--dark); padding: 0.7rem 0.9rem;
  border: 1px solid var(--gray-border); border-radius: 6px; }
.cp-seguro { background: rgba(230,51,41,0.05); }
.cp-fondo { background: rgba(37,99,235,0.05); }
.cp-fiscal { margin-top: 1rem; padding: 0.85rem 1.1rem; border-left: 3px solid var(--green);
  background: rgba(5,150,105,0.06); border-radius: 0 6px 6px 0; font-size: 0.83rem; color: var(--dark); line-height: 1.55; }
@media (max-width: 900px) { .cp-row { grid-template-columns: 30px 1fr; }
  .cp-seg { grid-column: 2; } .cp-head { display: none; }
  .cp-seguro::before { content: "PPR-seguro · "; font-weight: 800; color: var(--red-dark); }
  .cp-fondo::before { content: "PPR-fondo · "; font-weight: 800; color: var(--blue); } }

/* ── 02 · Árbol de familias ── */
.arbol { margin-top: 1rem; }
.tronco { display: grid; place-items: center; margin-bottom: 1.1rem; }
.tronco-in { max-width: 640px; text-align: center; border: 2px solid var(--black);
  border-radius: 8px; padding: 1rem 1.4rem; background: var(--white); }
.tronco-eyebrow { font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--gray-light); }
.tronco-in b { display: block; font-family: 'Anton', sans-serif; font-size: 1.6rem; color: var(--black); line-height: 1.2; }
.tronco-in p { margin: 0.3rem 0 0 !important; font-size: 0.8rem; color: var(--gray); }
.ramas { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 0.8rem; }
.rama { border: 1px solid var(--gray-border); border-top: 3px solid var(--gray-light);
  border-radius: 6px; padding: 0.9rem 1rem; background: #FBFAF8; position: relative; }
.rama::before { content: ""; position: absolute; top: -1.1rem; left: 50%; width: 1px;
  height: 1.1rem; background: var(--gray-border); }
.rama-acc { border-top-color: var(--red); background: var(--red-light); }
.rama-name { font-weight: 800; font-size: 0.88rem; color: var(--black); }
.rama-apodo { font-size: 0.74rem; color: var(--gray); margin-bottom: 0.6rem; }
.rama-acc .rama-apodo { color: var(--red-dark); font-weight: 700; }
.rama-meta { font-size: 0.76rem; color: var(--dark); margin-top: 0.35rem; }
.rama-meta span { display: block; font-size: 0.66rem; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--gray-light); font-weight: 700; }

/* ── 02 · Rendimiento real contra plazo ── */
.plazo { margin: 1.2rem 0 0.3rem; }
.pl-area { position: relative; height: 330px; margin-left: 46px; border-left: 2px solid var(--gray-border);
  border-bottom: 2px solid var(--gray-border); }
.pl-gl { position: absolute; left: 0; right: 0; border-top: 1px dashed var(--gray-border); }
.pl-gl span { position: absolute; left: -46px; top: -0.55em; font-size: 0.68rem;
  font-weight: 700; color: var(--gray-light); width: 40px; text-align: right; }
.pl-zero { position: absolute; left: 0; right: 0; border-top: 2px solid var(--gray); }
.pl-dot { position: absolute; width: 11px; height: 11px; border-radius: 50%;
  transform: translate(-50%, -50%); box-shadow: 0 0 0 2px var(--white); }
.pl-range { position: absolute; width: 7px; transform: translateX(-50%); border-radius: 4px; opacity: 0.32; }
.pl-lab { position: absolute; font-size: 0.71rem; font-weight: 700; white-space: nowrap;
  background: transparent !important; color: var(--black); }
.pl-der { transform: translate(12px, -50%); }
.pl-izq { transform: translate(calc(-100% - 12px), -50%); }
.pl-x { position: relative; height: 1.3rem; margin-left: 46px; }
.pl-x span { position: absolute; transform: translateX(-50%); font-size: 0.68rem;
  font-weight: 700; color: var(--gray-light); padding-top: 0.3rem; }
.pl-xtitle { margin-left: 46px; text-align: center; font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em; color: var(--gray-light); }
@media (max-width: 700px) { .pl-lab { font-size: 0.63rem; } .pl-area { height: 280px; } }

/* ── 03 · Circuito del dinero ── */
.circuito { display: grid; grid-template-columns: 200px 1fr; gap: 1.2rem; align-items: center; margin-top: 1rem; }
.cir-src { text-align: center; border: 2px solid var(--black); border-radius: 8px; padding: 1rem; background: var(--white); }
.cir-src b { display: block; font-size: 0.76rem; color: var(--gray); }
.cir-src em { display: block; font-family: 'Anton', sans-serif; font-style: normal;
  font-size: 1.9rem; color: var(--black); line-height: 1.15; }
.cir-src span { font-size: 0.72rem; color: var(--gray-light); }
.cir-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; }
.cir-col { border: 1px solid var(--gray-border); border-radius: 7px; padding: 1rem 1.1rem; background: #FBFAF8; }
.cir-acc { border-color: var(--red); background: var(--red-light); }
.cir-tag { font-weight: 800; font-size: 0.82rem; color: var(--black); text-transform: uppercase; letter-spacing: 0.04em; }
.cir-big { font-family: 'Anton', sans-serif; font-size: 1.7rem; color: var(--blue); line-height: 1.2; }
.cir-acc .cir-big { color: var(--red-dark); }
.cir-when { font-size: 0.72rem; color: var(--gray); }
.cir-how { font-size: 0.78rem; color: var(--dark); margin-top: 0.5rem; line-height: 1.45; }
.cir-foot { font-size: 0.77rem; color: var(--dark); margin-top: 0.6rem;
  border-top: 1px solid var(--gray-border); padding-top: 0.45rem; }
.cir-foot span { display: block; font-size: 0.64rem; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--gray-light); font-weight: 700; }
.cir-punch { margin-top: 1rem; padding: 0.9rem 1.1rem; background: var(--black); color: #F0EEEA;
  border-radius: 7px; font-size: 0.86rem; line-height: 1.55; }
.cir-punch b { color: var(--white); }
@media (max-width: 900px) { .circuito { grid-template-columns: 1fr; } .cir-cols { grid-template-columns: 1fr; } }

/* ── 04 · Línea de vida del desempleo ── */
.hitos { display: grid; gap: 0.5rem; margin-top: 1rem; }
.hito { display: grid; grid-template-columns: 210px 1fr; gap: 1.1rem;
  border: 1px solid var(--gray-border); border-left: 4px solid var(--gray-light);
  border-radius: 6px; padding: 0.85rem 1.1rem; background: #FBFAF8; }
.hito-ok { border-left-color: var(--green); }
.hito-mal { border-left-color: var(--red); background: rgba(230,51,41,0.05); }
.hito-tibio { border-left-color: var(--amber); background: rgba(180,83,9,0.05); }
.hito-evento { border-left-color: var(--black); background: var(--white); border-style: dashed; }
.hito-when { font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--gray-light); align-self: center; }
.hito-body b { font-size: 0.88rem; color: var(--black); }
.hito-body p { margin: 0.2rem 0 0 !important; font-size: 0.82rem; color: var(--dark); line-height: 1.5; }
.hito-veredicto { margin-top: 0.5rem; padding: 0.95rem 1.15rem; background: var(--black);
  color: #F0EEEA; border-radius: 7px; font-size: 0.86rem; line-height: 1.55; }
.hito-veredicto b { color: var(--white); }
@media (max-width: 820px) { .hito { grid-template-columns: 1fr; gap: 0.3rem; } }

/* ═══ FASE 3 · Figuras, glosario emergente y tablas plegables ═══ */
.fig-n { display: inline-block; font-family: 'Anton', sans-serif; font-size: 0.72rem;
  color: var(--red); background: var(--red-light); border: 1px solid rgba(230,51,41,0.25);
  border-radius: 4px; padding: 0.1rem 0.4rem; margin-right: 0.5rem; vertical-align: 0.08em; }
.figlist { list-style: none; margin: 1rem 0 0 !important; padding: 0; columns: 2; column-gap: 2.5rem; }
.figlist li { break-inside: avoid; margin: 0.3rem 0 !important; }
.figlist a { text-decoration: none; color: var(--dark); font-size: 0.82rem; }
.figlist a:hover { color: var(--red); }
@media (max-width: 820px) { .figlist { columns: 1; } }

/* Glosario emergente: definición al pasar el cursor o al enfocar con teclado */
abbr.gl { text-decoration: none; border-bottom: 1px dotted var(--gray-light);
  cursor: help; position: relative; outline: none; }
abbr.gl:hover, abbr.gl:focus { border-bottom-color: var(--red); }
abbr.gl::after { content: attr(data-def); position: absolute; left: 0; top: calc(100% + 8px);
  z-index: 60; width: max-content; max-width: min(420px, 80vw); padding: 0.7rem 0.9rem;
  background: var(--black); color: #F0EEEA; border-radius: 6px; font-size: 0.78rem;
  font-weight: 400; line-height: 1.5; text-transform: none; letter-spacing: normal;
  box-shadow: 0 6px 24px rgba(0,0,0,0.22); pointer-events: none;
  /* display:none y no visibility: un pseudo-elemento oculto por visibility sigue
     ocupando layout y ensancharía el documento entero */
  display: none; }
abbr.gl:hover::after, abbr.gl:focus::after { display: block; }
abbr.gl.gl-der::after { left: auto; right: 0; }
@media (hover: none) { abbr.gl::after { display: none; } }

/* Tablas largas: se recortan con degradado y un botón que las despliega */
.plegable { position: relative; }
.plegable > .table-scroll { max-height: 420px; overflow-y: auto; }  /* overflow-x sigue en auto: las tablas anchas lo necesitan */
.plegable::after { content: ""; position: absolute; left: 0; right: 0; bottom: 2.6rem; height: 90px;
  background: linear-gradient(to bottom, transparent, var(--cream)); pointer-events: none; }
.plegable.abierto > .table-scroll { max-height: none; }
.plegable.abierto::after { display: none; }
.plg-btn { display: block; margin: 0.6rem auto 0; font-family: 'Poppins', sans-serif;
  font-size: 0.76rem; font-weight: 700; color: var(--red-dark); background: var(--white);
  border: 1px solid var(--red); border-radius: 999px; padding: 0.4rem 1.1rem; cursor: pointer; }
.plg-btn:hover { background: var(--red); color: var(--white); }
section[style*="white"] .plegable::after { background: linear-gradient(to bottom, transparent, var(--white)); }
@media print { .plegable > .table-scroll { max-height: none !important; }
  .plegable::after, .plg-btn { display: none !important; } }
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
    shell = shell.replace("Uso confidencial del cliente", "Preparado para Sura · uso confidencial")
    start = shell.index('<div class="kpi-strip">')
    end = shell.index('<section id="resumen">')
    shell = shell[:start] + f'<div class="kpi-strip">{KPIS}</div>\n\n' + shell[end:]

    toc = []
    built = [build_section(*s, toc) for s in SECTIONS]
    built.insert(1, build_toc(toc))  # índice después del resumen ejecutivo
    sections_html = "\n\n".join(built)

    # Fase 3: figuras numeradas con su índice, glosario emergente y tablas largas plegables
    sections_html, indice_figs = numerar_figuras(sections_html)
    sections_html = sections_html.replace("<p>{{indice-figuras}}</p>", indice_figs)
    # El glosario emergente no se aplica a los anexos: ahí vive el glosario mismo y sería circular
    corte = sections_html.index('<section id="anexos"')
    sections_html = anotar_glosario(sections_html[:corte], leer_glosario()) + sections_html[corte:]
    sections_html = plegar_tablas(sections_html)

    start = shell.index('<section id="resumen">')
    end = shell.index("<footer>")
    shell = shell[:start] + sections_html + "\n\n" + shell[end:]

    # Progreso de lectura y riel de navegación: markup tras el nav, script antes de cerrar body
    shell = shell.replace("</nav>", "</nav>\n\n" + build_rail(), 1)
    shell = shell.replace("</body>", RAIL_JS + "\n" + PLEGABLE_JS + "\n</body>", 1)

    # Guard de sesión (patrón del estudio anterior) al inicio del <head> del estudio
    shell = shell.replace("<head>", "<head>\n" + GUARD_JS, 1)
    shell = shell.replace("<title>", '<meta name="robots" content="noindex, nofollow">\n  <title>', 1)

    login = login_html()
    for base in (DOCS, ROOT):
        (base / "estudio.html").write_text(shell, encoding="utf-8")
        (base / "index.html").write_text(login, encoding="utf-8")
    size = (DOCS / "estudio.html").stat().st_size
    root_assets = ROOT / "assets"
    if root_assets.exists(): shutil.rmtree(root_assets)
    shutil.copytree(assets, root_assets)
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"OK -> estudio.html ({size/1024:.0f} KB) + index.html (login) en docs/ y raíz")

if __name__ == "__main__":
    main()
