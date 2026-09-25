# Estado de validación

**Versión pública:** 1.11.0

## Release pública

El repositorio publica una especificación generalizada con fixtures sintéticos y un núcleo Python determinista. Los casos privados/no públicos permanecen excluidos.

### Capas vigentes

| Capa | Estado |
|---|---|
| Metodología normativa | Publicada |
| Schemas raw/canonical | Publicados |
| Manifiesto arquitectónico | `manifests/almas-module-manifest.json` |
| Pipeline FULL M00–M31 | `manifests/analysis-pipeline-manifest.json` |
| Bridge astrología→contrato | v1.0.0 |
| Reconstrucción preencarnatoria | schema v1.9.0 |
| Clause assembly | schema v1.1.0 |
| Doctrinal Claim | schema v2.0.0 |
| Ontología multiaxial | registry/schema v2.0.0 |
| Contrato causal | v2.0.0 |
| Temporalidad contractual | v2.0.0 |
| Orquestador M00–M31 | Publicado y probado end-to-end con fixture sintético |
| M02 natal / M08 Davison | Contratos ejecutables; backend de producción pendiente |
| Núcleo Python IEM/IDD/IRC | Publicado y unit-tested |
| CLI de pilares precomputados | Publicada y unit-tested |
| Corpus doctrinal | 38 fuentes / 92 conceptos / 73 relaciones |
| Fixtures sintéticos | Publicados |
| Casos privados | Excluidos |
| Casos públicos verificables | Admitidos sólo en `public_cases/` |

## Pruebas automatizadas

La suite Python contiene **75 tests deterministas**, incluidos módulos aislados, firewalls metodológicos y una ejecución sintética completa M00–M31.

El workflow `Python core` ejecuta:

1. instalación editable del paquete;
2. `python -m unittest discover -s tests -p "test_*.py" -v`;
3. el validador del contrato público.

El workflow `Public contract` ejecuta de forma independiente:

`python scripts/validate_public_contract.py`

El validador comprueba, entre otros:

- sincronía de versiones públicas;
- existencia de archivos normativos;
- secuencia M00–M31;
- integridad fuente↔concepto↔genealogía;
- correspondencia schema↔fixture;
- techos inferenciales;
- claims doctrinales;
- discriminadores;
- pipeline preencarnatorio;
- contratos de ejecución M00–M31;
- prueba FULL sintética;
- reglas de privacidad/publicación.

La validación automatizada demuestra coherencia de implementación con las reglas publicadas. No constituye validación científica de la astrología ni convierte índices de encaje en probabilidades metafísicas.

## Validación externa

**Infraestructura:** PREREGISTRATION READY.  
**Holdout externo real:** NOT YET EXECUTED.

La infraestructura incluye:

- protocolo de validación externa;
- schemas de caso y ejecución;
- manifiesto de cohortes;
- endpoints EV1–EV8;
- flujo ciego estructura → apertura documental;
- controles de contaminación/case-fitting;
- fixture sintético de smoke test.

Hasta ejecutar cohortes holdout reales preregistradas, ALMAS no declara validación empírica externa de twin-flame, soulmate, soul-contract u otras ontologías metafísicas.
