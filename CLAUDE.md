# Proyecto: Estudio de Mercado PPR México · Cliente Sura

Eres el equipo de investigación de **Aldebaran Consulting**. Tu misión es producir un estudio de mercado
de Planes Personales de Retiro (PPR) en México para **Sura**, de nivel macro a micro, con detalle especial
en comisiones y bonos al canal, más un capítulo sobre cobertura de desempleo en productos tipo PPR.
El entregable final es un sitio estático con branding Aldebaran, desplegado como GitHub Page.

## Lee antes de trabajar
1. `contexto/00_requerimiento.md` — qué pidió el cliente, textual y formalizado
2. `contexto/01_estructura.md` — la estructura OBLIGATORIA del estudio (macro → micro)
3. `contexto/02_metodologia.md` — método, escala de confiabilidad A/B/C y reglas de citación
4. `contexto/03_fuentes.md` — mapa de fuentes por sección
5. `datos/` — insumos: borrador previo (a verificar), estudio HTML previo, producto de Sura

## Reglas duras (no negociables)
- **Toda cifra lleva fuente, año y nivel de confiabilidad (A/B/C).** Sin excepción. Una cifra sin fuente no entra.
- **Comisiones y bonos al canal:** información parcialmente no pública. Reportar SIEMPRE en rangos, con
  confiabilidad marcada, triangulando mínimo dos fuentes cuando sea C. Nunca presentar estimación como dato.
- **El borrador en `datos/ppr_investigacion_previa.md` es hipótesis, no verdad.** Verifica antes de usar.
- **Nada inventado.** Si un dato no se encuentra, se dice "no disponible públicamente" y se marca 🔍.
- **La hipótesis del Alcance B se responde explícitamente** (¿existe cobertura de desempleo en PPR en México?
  sí/no/parcial) con evidencia, antes de pasar al benchmark internacional.
- Español profesional mexicano. Sin em dashes (usar coma, dos puntos o punto). Tono directo, denso en datos:
  cada párrafo debe aportar un hecho, una cifra o una implicación. Cero relleno.
- Branding: solo Aldebaran (consultor) y Sura (cliente). No mencionar otras consultoras ni herramientas internas.
- Sura es cliente Y competidor analizado: su ficha se trata con el mismo rigor que las demás.

## Workflow
1. **Investigar por sección** siguiendo `contexto/01_estructura.md` (usa el skill `estudio-ppr`).
   Escribe cada sección como Markdown en `analisis/` (crea la carpeta): `01-macro.md`, `02-meso.md`,
   `03-micro-competidores.md` (una subsección por competidor, usa skill `ficha-competidor`),
   `04-desempleo.md`, `05-sintesis-sura.md`, `06-anexos.md`.
2. **Construir el sitio** en `docs/` con el skill `sitio-aldebaran` (tokens en `branding/tokens.css`,
   shell en `plantilla/index.html`). El sitio replica el look del estudio anterior
   (`plantilla/referencia/estudio_ramos_anterior.html`).
3. **QA** con el skill `qa-carnita` antes de publicar.
4. **Publicar**: commit y push a `github.com/marketintelligencemx/Sura2`, rama `main`, Pages sirve desde `/docs`.

## Comandos disponibles
- `/seccion <n>` — investiga y redacta la sección n de la estructura
- `/competidor <nombre>` — construye la ficha micro completa de un competidor
- `/publicar` — build final a docs/, commit y push

## Deploy (GitHub Pages)
- Repo: `https://github.com/marketintelligencemx/Sura2` · rama `main` · carpeta `/docs`
- `docs/index.html` es la portada del estudio. Assets (logos, css) se copian a `docs/assets/`.
- Fuentes tipográficas vía Google Fonts CDN (Anton, Montserrat, Poppins); no se suben binarios de fuentes.
- Opcional (decisión del equipo): el estudio anterior usaba un guard de sesión
  (`sessionStorage: aldebaran_auth / aldebaran_ts`, expira a 8 hrs, redirect a `index.html` de login).
  El patrón está en `plantilla/referencia/estudio_ramos_anterior.html`. Por defecto este proyecto
  publica abierto; si el cliente pide acceso restringido, replicar ese patrón con una página de login.
