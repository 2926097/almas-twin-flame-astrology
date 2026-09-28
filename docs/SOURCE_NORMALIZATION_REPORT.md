# ALMAS · Normalización del corpus de fuentes

**Estado:** línea base cerrada; corpus extensible.  
**Fuente canónica de cifras:** `reference/source-normalization-audit.json`.

## Línea base vigente

- **44 fuentes**;
- **97 conceptos**;
- **73 relaciones doctrinales/genealógicas**;
- **23 fuentes VERIFIED_PRIMARY**;
- **21 fuentes VERIFIED_METADATA**;
- **0 fuentes PARTIAL**;
- **0 conceptos de fuente sin definición**;
- **0 referencias de concepto a fuentes inexistentes**;
- **0 aristas genealógicas rotas**.

Distribución:

- P1 primaria: 25;
- P2 académica: 7;
- P3 histórica/técnica: 2;
- P4 método identificado: 10.

### Declinaciones y antiscios

La misma fase incorpora a Kt Boehrer como fuente de método para declinaciones/paralelos y a Firmicus Maternus, `Mathesis` II.29, como fuente histórica primaria para antiscios. El objetivo es fortalecer el significado técnico de M05–M06 sin convertir simetrías o declinaciones en discriminadores metafísicos.

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

## Refuerzo interpretativo 1.20

El corpus incorpora como fuentes de método a John Townley para la carta compuesta y a Ronald C. Davison para sinastría/`Relationship Horoscope`. La finalidad es mejorar la fundamentación de M07–M09 y de la narrativa de cartas relacionales.

La incorporación no crea nuevos scores ni discriminadores. Permite distinguir con mayor precisión qué afirmaciones proceden del método astrológico y cuáles son síntesis hermenéuticas de ALMAS.

## Evolución

Las cifras de este documento son una vista humana. Si el corpus cambia, el objeto canónico que debe actualizarse primero es `reference/source-normalization-audit.json`; CI comprueba que sus totales coincidan con los registros efectivos.
