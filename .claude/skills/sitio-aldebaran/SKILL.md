---
name: sitio-aldebaran
description: >
  Construcción del sitio del estudio con branding Aldebaran para GitHub Pages. Úsalo al generar o
  modificar cualquier HTML del entregable en docs/, al aplicar los tokens de marca, o al preparar
  la publicación en el repo marketintelligencemx/Sura2.
---

# Skill: Sitio del estudio · Branding Aldebaran

## Identidad (no desviarse)
- **Tipografías (Google Fonts CDN):** Anton (títulos hero, uppercase), Montserrat 400-800 (cuerpo y
  labels), Poppins 300-700 (marca y nav).
  `https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;500;600;700;800&family=Poppins:wght@300;400;500;600;700&display=swap`
- **Tokens:** usar `branding/tokens.css` tal cual. Acento rojo #E63329; fondo crema #F5F3EF; texto
  #2D2D2D sobre crema; strips negros #1A1A1A para KPIs. Azul/ámbar/verde solo para semáforos de datos.
- **Logos:** `branding/aldebaran-logo.svg` (nav, izquierda) + `branding/sura-logo.svg` (nav, derecha,
  como cliente). Copiarlos a `docs/assets/`.
- **Referencia viva:** `plantilla/referencia/estudio_ramos_anterior.html` es el estándar de look and
  feel (nav fija, hero blanco con eyebrow rojo, kpi-strip negro, secciones sobre crema). El estudio
  nuevo debe sentirse hermano de ese.

## Estructura del sitio en docs/
- `docs/index.html`: el estudio completo one-page con nav de anclas a las 6 secciones (+ resumen).
  Partir de `plantilla/index.html` (shell ya armado con hero, kpi strip y secciones vacías).
- `docs/assets/`: logos svg + `tokens.css`.
- Si una sección crece demasiado (micro competidores), puede separarse en `docs/competidores.html`
  enlazada desde nav, manteniendo el mismo shell.

## Componentes estándar
- **Hero:** eyebrow rojo uppercase ("Aldebaran Consulting · Estudio de mercado"), H1 Anton
  ("Plan Personal de Retiro"), sub con alcance, meta-row: cliente Sura · fecha de corte · versión.
- **KPI strip (negro):** 4 o 5 números ancla del estudio (tamaño, crecimiento, jugadores, veredicto B).
- **Sección:** número + título (Montserrat 800), intro con el hallazgo, cuerpo con tablas.
- **Badges de confiabilidad:** `<span class="conf conf-a">A</span>` (verde), `conf-b` (ámbar),
  `conf-c` (rojo suave). Ya definidos en tokens.css. TODA cifra en tablas lleva el suyo.
- **Gap chips:** ✅ ⚠️ ❌ 🔍 con clases `gap-si`, `gap-lim`, `gap-no`, `gap-ver`.
- **Tabla de fuentes** al final con URL, fecha de consulta y confiabilidad.

## Publicación (GitHub Pages)
1. Build: contenido final de `analisis/*.md` volcado al HTML de `docs/` con los componentes de arriba.
2. `git add docs && git commit -m "estudio ppr vX" && git push origin main`
   (remoto: `https://github.com/marketintelligencemx/Sura2`).
3. En Settings → Pages: Source = Deploy from a branch, Branch = main, Folder = /docs (una sola vez).
4. Verificar en `https://marketintelligencemx.github.io/Sura2/`.
5. Acceso restringido (opcional): replicar el guard `aldebaran_auth`/`aldebaran_ts` (sessionStorage,
  8 hrs) del estudio anterior con una página de login; por defecto el sitio va abierto.

## Reglas de calidad visual
- Nunca fondo blanco pleno en el body: crema #F5F3EF (el blanco es solo para hero y cards).
- Tablas: encabezado uppercase letterspaced, zebra sutil, números alineados a la derecha.
- Mobile: nav scrolleable horizontal (patrón del estudio previo), tablas con overflow-x.
- Sin librerías JS; CSS puro y HTML semántico. Peso total del sitio < 1 MB sin imágenes.
