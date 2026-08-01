# Sura2 · Estudio de Mercado PPR México

Proyecto de Claude Code para producir el estudio de PPR (Planes Personales de Retiro) para Sura,
con branding Aldebaran, desplegable como GitHub Page desde `/docs`.

## Cómo usarlo
1. Abre esta carpeta con Claude Code: `claude`
2. Claude leerá `CLAUDE.md` automáticamente. Pídele: "lee el contexto y proponme el plan de trabajo".
3. Trabaja sección por sección con `/seccion 1`, `/seccion 2`, ... o por competidor con `/competidor GNP`.
4. Cuando el estudio esté completo: `/publicar`.

## Estructura
- `CLAUDE.md` — instrucciones maestras del proyecto
- `contexto/` — requerimiento, estructura del estudio, metodología, fuentes
- `datos/` — insumos: borrador previo, estudio HTML anterior, ficha del producto Sura, referencias del estudio de ramos
- `branding/` — logos Aldebaran y Sura, tokens CSS, guía de marca
- `plantilla/` — shell HTML del sitio + referencia del estudio anterior
- `.claude/skills/` — metodología ejecutable (estudio, fichas, sitio, QA)
- `.claude/commands/` — atajos /seccion, /competidor, /publicar
- `docs/` — destino del build (GitHub Pages)

## Deploy
GitHub Pages: repo `marketintelligencemx/Sura2`, rama `main`, servir desde `/docs`.
