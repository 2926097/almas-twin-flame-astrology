# ALMAS 1.11.0 · Informes astrológicos personales PDF

## Estado

Este documento define la integración del perfil de informes personales dentro de la arquitectura modular única de ALMAS 1.11.0.

No crea una segunda skill pública. El punto de entrada especializado es `skills/almas-personal-pdf/SKILL.md`.

## Arquitectura

```text
birth/document input
        ↓
astronomy backend
        ↓
personal_canonical_analysis.json
        ↓
validation + canonical fingerprint
        ↓
reference router
        ↓
personal_report_document_model.json
        ↓
narrative authoring
        ↓
DOCX
        ↓
PDF
        ↓
preflight + full-page render QA
```

El motor de publicación no puede corregir ni completar silenciosamente el canonical.

## Integraciones de patrones externos

La implementación es propia y no copia código de terceros. Se han estudiado patrones públicos de:

1. **wvanderen/astrology-skill**  
   Patrón incorporado: frontera cálculo→interpretación, routing y recuperación modular de referencias.  
   Repositorio: https://github.com/wvanderen/astrology-skill  
   Nota: su runtime interpretativo se distribuye bajo MIT; su calculador Swiss Ephemeris se mantiene como unidad AGPL separada.

2. **zhuisDEV/lilacsky**  
   Patrón incorporado: contrato JSON estable con fecha local/UTC normalizada, opciones de cálculo, warnings y metadatos del motor.  
   Repositorio: https://github.com/zhuisDEV/lilacsky  
   Nota: proyecto AGPL-3.0-or-later. ALMAS adopta el patrón de procedencia, no código.

3. **adityarya24/astro-skill**  
   Patrón incorporado: pipeline determinista cálculo→JSON→informe PDF y separación entre cálculo y redacción.  
   Repositorio: https://github.com/adityarya24/astro-skill  
   Nota: MIT. ALMAS conserva su propio modelo editorial B5 y su separación A–E.

4. **aryaminus/astro**  
   Patrón incorporado: API estable de motor reutilizable que puede exponerse en varias superficies sin acoplar el núcleo a un framework.  
   Repositorio: https://github.com/aryaminus/astro  
   Nota: MIT. En ALMAS la API Python se implementa primero; CLI/MCP/REST quedan como superficies posteriores.

## Frontera de cálculo

El informe personal acepta dos fuentes de verdad geométrica:

- un backend astronómico inyectado por ALMAS;
- un JSON calculado externamente y validado.

En ambos casos deben registrarse `calculation_provenance` y warnings. La interpretación no puede fabricar factores ausentes.

## Provenance mínima

`calculation_provenance` conserva:
- engine;
- engine_version;
- ephemeris;
- zodiac;
- house_system;
- node_type;
- timezone;
- coordinates;
- calculation_flags;
- input_hash;
- generated_at cuando exista;
- warnings.

La precisión numérica del backend no equivale a precisión de la hora de nacimiento.

## Router de referencias

La lectura recupera únicamente los dominios activados:

- foundations;
- traditional;
- modern_psychological;
- evolutionary;
- karmic;
- draconic;
- esoteric;
- kabbalah;
- lots;
- symmetry;
- fixed_stars;
- asteroids;
- timing;
- publication.

El router decide qué corpus cargar, no qué conclusión debe obtenerse.

## Perfiles

### EXECUTIVE_PERSONAL_REPORT
Síntesis, calidad de datos, arquitectura natal, temporalidad clave y conclusión.

### STANDARD_PERSONAL_REPORT
Lectura natal profunda con capas complementarias y temporalidad resumida.

### FULL_CRITICAL_REPORT
Informe completo, aparato crítico, contraevidencia, atlas técnico y fuentes.

### TECHNICAL_ATLAS
Prioriza posiciones, casas, aspectos, técnicas derivadas, efemérides y trazabilidad.

### ESOTERIC_KABBALISTIC_REPORT
Amplía la capa esotérica/cabalística sin convertir analogía doctrinal en dato calculado.

## Contrato de publicación

El modelo documental declara:
- fingerprint del canonical;
- perfil;
- rutas disponibles/ausentes;
- secciones;
- dominios de referencia;
- estado READY/PARTIAL;
- B5 como perfil editorial por defecto;
- `canonical_values_embedded=false`;
- `canonical_values_mutated=false`;
- `prose_generated=false`;
- `docx_created=false`;
- `pdf_created=false`;
- `pdf_preflight_performed=false`.

La generación física del documento ocurre después.

## Evolución futura

La API Python de 1.11.0 queda preparada para una futura exposición como:
- `almas-personal-report` CLI;
- herramientas MCP;
- endpoints REST/OpenAPI.

Esas superficies no deben duplicar lógica analítica: solo serializar/validar los mismos contratos.
