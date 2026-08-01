---
name: qa-carnita
description: >
  Control de calidad final del estudio PPR. Úsalo antes de dar por terminada cualquier sección y
  obligatoriamente antes de /publicar. Verifica densidad, fuentes, confiabilidad, estructura y branding.
---

# Skill: QA "pura carnita"

## Checklist de contenido (por sección)
- [ ] Cumple el "contenido mínimo" de su sección en `contexto/01_estructura.md`, punto por punto.
- [ ] Toda cifra tiene fuente, año y badge A/B/C. Cero cifras huérfanas.
- [ ] Las de nivel C tienen dos fuentes o están marcadas "indicio único 🔍".
- [ ] Abre con el hallazgo ("so what") y cierra con implicaciones para Sura.
- [ ] Cero párrafos de relleno: si un párrafo no aporta hecho, cifra o implicación, se corta.
- [ ] Tablas para todo lo comparativo; rangos en comisiones, nunca puntos.

## Checklist del estudio completo
- [ ] La hipótesis del Alcance B está respondida explícitamente (sí/no/parcial) con evidencia, al inicio
      de la sección 04.
- [ ] La tabla maestra de comisiones al canal existe, compara los arquetipos correctamente
      (aportación vs. saldo) y cada celda trae confiabilidad.
- [ ] El gap analysis de Sura usa la escala ✅⚠️❌🔍 y cubre producto, fiscal, digital, canal,
      compensación y coberturas.
- [ ] Resumen ejecutivo autocontenido de 1 página, escrito al final.
- [ ] Anexos: metodología, fuentes con fecha de consulta, glosario.
- [ ] Fecha de corte visible en hero y tablas.

## Checklist de branding y sitio
- [ ] Tokens Aldebaran intactos (rojo #E63329, crema #F5F3EF, Anton/Montserrat/Poppins vía CDN).
- [ ] Logos Aldebaran y Sura en nav; ningún otro logo ni marca de terceros.
- [ ] Badges de confiabilidad y gap chips renderizando.
- [ ] Nav ancla a todas las secciones; mobile sin desbordes; sin librerías JS.
- [ ] Sin em dashes en el texto; español profesional; ortografía revisada.

## Veredicto
El QA se reporta como tabla sección × criterio con ✅/❌ y lista de correcciones. Nada se publica con ❌.
