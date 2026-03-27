# AI Log - Geochemical Balance Analyzer

## Herramientas utilizadas
- **GitHub Copilot** (VS Code)

---

## Filosofía de uso

Se decidió usar IA exclusivamente para tareas de **generación de código boilerplate**, **autocompletado de funciones mecánicas**, y **depuración de errores sintácticos**. 

Las decisiones clave del proyecto —arquitectura de la tubería analítica, selección de especies iónicas, definición de constantes químicas (pesos atómicos IUPAC, cargas iónicas), fórmulas de conversión de unidades, lógica de balance de carga, y umbral de calidad (±5%)— fueron **100% responsabilidad del equipo** y se fundamentaron en literatura de geoquímica de aguas (directrices IAH, estándares hidrogeoquímicos).

**Criterio aplicado**: Si la tarea requiere conocimiento de geoquímica o química analítica, la hacemos nosotros. Si es código repetitivo o sintáctico, Copilot acelera.

---

## Registro de uso

### 2026-03-20 | GitHub Copilot | Boilerplate de importaciones
- **Tarea**: Estructura inicial de imports (pandas, numpy, re, Path, OpenCV, RapidOCR).
- **Resultado**: Sugerió la lista estándar de librerías para ML/data science.
- **Decisión**: Aceptado sin cambios; es código estándar.

### 2026-03-20 | GitHub Copilot | Función de análisis de expresiones regulares
- **Tarea**: Generar función `molar_mass(formula)` que parsee fórmulas químicas como "SO4", "HCO3", "PO4" y calcule la masa molar sumando pesos atómicos.
- **Resultado**: Generó regex-based parser con bucle de conteo de átomos.
- **Decisión**: Aceptado con verificación manual. Los pesos atómicos IUPAC 2021 fueron agregados por el equipo (no por IA). Se validó que SO₄ = 96.056 g/mol, HCO₃ = 61.016 g/mol, etc., contra referencias oficiales.

### 2026-03-20 | GitHub Copilot | Conversión de unidades (mg/dm³ → mmol/dm³)
- **Tarea**: Código para convertir concentración mg/L a mmol/L mediante división por masa molar.
- **Resultado**: Sugerió vectorización con pandas (división elemento a elemento) y transposición de matriz.
- **Decisión**: Aceptado. La **decisión química** —que la fórmula correcta es mg/L ÷ g/mol— fue validación del equipo contra literatura de hidrogeoquímica.

### 2026-03-20 | GitHub Copilot | Multiplicación por carga iónica
- **Tarea**: Código para convertir mmol/dm³ a meq/dm³ multiplicando por la carga del ion.
- **Resultado**: Generó `mul(charge_series, axis=0)` para alineación por índice y multiplicación fila-a-fila.
- **Decisión**: Aceptado. La **decisión de dominio** —que meq/L = mmol/L × carga, y que cations son +ve mientras que anions son -ve para agregación posterior— fue responsabilidad del equipo basada en definiciones estándar de equivalentes químicos.

### 2026-03-20 | GitHub Copilot | Agregación de sumas de cationes/aniones
- **Tarea**: Código para sumar contribuciones de cationes (Na⁺, K⁺, Ca²⁺, Mg²⁺, Li⁺) y aniones (Cl⁻, F⁻, SO₄²⁻, HCO₃⁻, CO₃²⁻, PO₄³⁻) por muestra.
- **Resultado**: Sugerió `loc[especies].sum(axis=0)` para extracción y agregación columnaria.
- **Decisión**: Aceptado. La **decisión química** —qué especies son cationes vs. aniones, y que los aniones deben usar valor absoluto antes de sumarlos— fue determinada por el equipo según química estándar.

### 2026-03-20 | GitHub Copilot | Fórmula de Balance de Carga (CBE)
- **Tarea**: Código para calcular CBE(%) = ((ΣCationes - ΣAniones) / (ΣCationes + ΣAniones)) × 100.
- **Resultado**: Generó la fórmula vectorizada y broadcast a todas las muestras.
- **Decisión**: Aceptado. La **decisión de uso** —aplicar fórmula CBE estándar de IAH como métrica de calidad— fue del equipo, no de IA.

### 2026-03-22 | GitHub Copilot | Depuración de atributos de pandas
- **Tarea**: Error de tipado: `df.loc[...]` retornaba un Series cuando se esperaba DataFrame en algunas iteraciones.
- **Resultado**: Copilot sugirió usar `df.loc[[especies]]` (doble corchete) para mantener dimensionalidad de DataFrame.
- **Decisión**: Aceptado. Era corrección sintáctica pura.

### 2026-03-24 | GitHub Copilot | Autocompletado de names/labels
- **Tarea**: Generar nombres automáticos para CSV de salida (ej. "geochem_mmol_dm3.csv", "geochem_meq_dm3.csv").
- **Resultado**: Sugerencias de nomenclatura sistemática siguiendo patrón "geochem_[unidad]_[etapa].csv".
- **Decisión**: Aceptado. Mejora trazabilidad pero no afecta lógica.

### 2026-03-25 | GitHub Copilot | Boilerplate de exportación CSV
- **Tarea**: Código repetitivo para `.to_csv(path, index=False)` con print de confirmación.
- **Resultado**: Autocompletado sistemático en cada celda.
- **Decisión**: Aceptado sin cambios.

### 2026-03-26 | GitHub Copilot | Generación de README.md
- **Tarea**: Estructura y contenido de documentación bilingüe (Inglés/Español) para repositorio.
- **Resultado**: Propuesta de secciones, estructura de markdown, ejemplos de uso.
- **Modificación**: Se personalizó el contenido para reflejar exactamente el dominio del proyecto (geoquímica de aguas, especies iónicas específicas, métricas de balance de carga). Se agregaron referencias a Directrices IAH y valores IUPAC 2021, que fueron especificaciones del equipo.

---

## LO QUE NO se delegó a IA

1. **Selección de especies iónicas**: Decisión del equipo cuál de las 11+ especies potenciales incluir en el análisis. Se basó en disponibilidad de datos (muestras_sonora.csv) y relevancia hidrogeoquímica.

2. **Constantes químicas**: Todos los pesos atómicos IUPAC, cargas iónicas, y definiciones de especies (ej. ¿es PO₄³⁻ o PO₄²⁻?) fueron verificados manualmente contra literatura estándar de geoquímica.

3. **Decisión OCR → CSV**: Cuando la tubería OCR plateó en precisión debido a ruido en la imagen de origen, la **decisión estratégica de pivotar a ingesta directa desde CSV limpio** fue del equipo. IA no fue consultada.

4. **Narrativa de documentación**: La descripción del proyecto, motivación, y contexto en README.md fue redactado por el equipo. IA solo facilitó estructura de markdown.

5. **Validación de fórmulas**: Todas las fórmulas de conversión de unidades y balance de carga fueron validadas manualmente por el equipo contra literatura de hidrogeoquímica de aguas (IAH guidelines, USGS standards, libros de referencia).

6. **Decisión de umbral ±5%**: La selección del umbral de 5% para flagging de calidad fue una decisión de dominio del equipo basada en estándares geoquímicos de aceptabilidad de balance de carga.

---

## Impacto en reproducibilidad

Todos los códigos sugeridos por Copilot:
- ✅ Se ejecutan correctamente en el pipeline del proyecto
- ✅ Siguen convenciones pandas/numpy estándar (consistencia de estilo)
- ✅ Están documentados con comentarios que demuestran comprensión del equipo

---

## Conclusión

GitHub Copilot fue un **acelerador de sintaxis**, no un sustituto de decisiones analíticas. La capacidad de **formular preguntas relevantes** (¿cuáles son las especies iónicas?), **tomar decisiones informadas** (OCR vs. CSV, qué umbral), y **conectar datos con frameworks sólidos** (IAH, IUPAC, hidrogeoquímica) fue responsabilidad exclusiva del equipo.

Modelo de integración: **Uso Estratégico** (según rúbrica HackODS).

---

**Equipo**: Geochemical Balance Analysis Team  
**Fecha de creación de this log**: 2026-03-26  
**Herramientas**: GitHub Copilot v2026.3  
**Repositorio**: https://github.com/alejandroceba/geochemical-balance
