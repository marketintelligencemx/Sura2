# Insumo: comparativo de producto (deducibles vs no deducibles)

Carpeta de entrada para los PDFs de comparativo competitivo de planes de ahorro e inversión
de largo plazo. Deja los archivos aquí, sin renombrar (yo los normalizo al procesarlos).

- `deducibles/` — productos que califican como deducibles de ISR (Art. 151 fracc. V LISR,
  Art. 185 LISR): PPR y equivalentes.
- `no_deducibles/` — productos de ahorro e inversión con mecánica similar al PPR pero sin
  beneficio fiscal: dotales, unit-linked, seguros de vida con componente de inversión,
  fondos y planes de ahorro programado.

## Reglas de tratamiento (obligatorias)

1. **Anonimato del origen.** El material se usa como insumo de análisis. En el estudio no se
   menciona quién elaboró el comparativo ni se reproduce su marco de lectura, títulos,
   segmentación ni conclusiones tal cual. Se reconstruye el análisis con criterio propio
   de Aldebaran.
2. **La aseguradora que originó el material se trata como un competidor más**, con la misma
   ficha, mismo nivel de detalle y mismo rigor que el resto del panel, incluido Sura.
3. **Confiabilidad: B.** Material de elaboración propia (Aldebaran), no publicado. Las cifras
   entran al estudio como **B**, citadas como "Análisis competitivo propio, Aldebaran
   Consulting, <mes año>". Excepción: si una celda del comparativo reproduce un dato de
   fuente pública primaria (CNSF, CONSAR, condiciones generales registradas), se cita la
   fuente primaria con su nivel propio, que suele ser A. La confiabilidad la determina el
   origen último del dato, no quién armó la tabla.
4. **Fecha de corte.** Anotar el año y mes del documento. Producto y comisiones cambian por
   generación de venta; una tabla sin fecha no entra al estudio.
5. Estos PDFs son insumo interno. No se publican ni se enlazan desde `docs/`.
6. **Integración.** El material no forma capítulo aparte. Los productos alimentan el panorama
   meso (`analisis/02-meso.md`), las fichas de cada emisor (`analisis/03-micro-competidores.md`)
   y, sobre todo, cierran en implicaciones para Sura (`analisis/05-sintesis-sura.md`).

## Qué extraigo de cada documento

- Emisor, nombre comercial del producto y generación o versión
- Régimen fiscal (deducible / no deducible) y tope aplicable
- Prima mínima, plazos, moneda y esquema de aportación
- Comisiones: administración, adquisición, rescate y penalizaciones por retiro anticipado
- Comisión y bonos al canal, si aparecen
- Rendimiento ilustrado, tasa garantizada y supuestos usados
- Coberturas anexas: fallecimiento, invalidez, enfermedades graves, **desempleo**
- Condiciones de rescate, préstamos sobre póliza y valores garantizados
