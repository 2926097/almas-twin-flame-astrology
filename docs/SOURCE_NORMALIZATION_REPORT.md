# ALMAS · Normalización del corpus de fuentes

**Estado:** línea base cerrada; corpus extensible.  
**Fuente canónica de cifras:** `reference/source-normalization-audit.json`.

## Línea base vigente

- **38 fuentes**;
- **92 conceptos**;
- **73 relaciones doctrinales/genealógicas**;
- **21 fuentes VERIFIED_PRIMARY**;
- **17 fuentes VERIFIED_METADATA**;
- **0 fuentes PARTIAL**;
- **0 conceptos de fuente sin definición**;
- **0 referencias de concepto a fuentes inexistentes**;
- **0 aristas genealógicas rotas**.

Distribución:

- P1 primaria: 23;
- P2 académica: 7;
- P3 histórica/técnica: 1;
- P4 método identificado: 7.

## Criterio

“Línea base cerrada” significa que el corpus actual es internamente auditable, no que la bibliografía esté agotada.

Toda fuente nueva debe:

1. registrar procedencia, tradición y función documental;
2. declarar `supports` y `does_not_support`;
3. enlazar conceptos definidos;
4. registrar nuevas relaciones de equivalencia/no-equivalencia cuando proceda;
5. preservar A/B/C/D/E;
6. no aportar puntuación astrológica por su mera existencia.

## Anclas documentales

Los documentos usados directamente por los mapeos doctrina→astrología deben disponer de:

- `verification_anchor`;
- `verification_anchor_type`;
- `evidence_scope`.

La granularidad de una afirmación no puede superar la granularidad de su ancla.

Véanse:

- `docs/SOURCE_ANCHOR_POLICY.md`;
- `docs/MAPPED_SOURCE_ANCHOR_REPORT.md`;
- `reference/source-registry.json`.

## Evolución

Las cifras de este documento son una vista humana. Si el corpus cambia, el objeto canónico que debe actualizarse primero es `reference/source-normalization-audit.json`; CI comprueba que sus totales coincidan con los registros efectivos.
