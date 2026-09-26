# Estado de validación

**Versión pública:** 1.11.0

## Release pública

El repositorio publica una especificación generalizada con fixtures sintéticos y un núcleo Python determinista. Los casos privados/no públicos permanecen excluidos.

### Capas vigentes

| Capa | Estado |
|---|---|
| Metodología normativa | Publicada |
| Schemas de entrada bruta/canónica | Publicados |
| Manifiesto arquitectónico | `manifests/almas-module-manifest.json` |
| Pipeline FULL M00–M31 | `manifests/analysis-pipeline-manifest.json` |
| Puente astrología→contrato | v1.0.0 |
| Reconstrucción preencarnatoria | schema v1.9.0 |
| Ensamblaje de cláusulas | schema v1.1.0 |
| Afirmación doctrinal | schema v2.0.0 |
| Ontología multiaxial | registro/schema v2.0.0 |
| Contrato causal | v2.0.0 |
| Temporalidad contractual | v2.0.0 |
| Orquestador M00–M31 | Publicado y probado de extremo a extremo con fixture sintético |
| M30 · gate de informe | READY/PARTIAL/BLOCKED + fingerprint canónico |
| M31 · report_document_model | 11 secciones canónicas; cierre del pipeline analítico |
| Informes personales PDF | Módulo interno, 5 perfiles, canonical personal + fingerprint + router de referencias |
| M02 natal / M08 Davison | Contratos ejecutables; backend de producción pendiente |
| Núcleo Python IEM/IDD/IRC | Publicado y probado unitariamente |
| CLI de pilares precomputados | Publicada y probada unitariamente |
| Corpus doctrinal | 38 fuentes / 92 conceptos / 73 relaciones |
| Fixtures sintéticos | Publicados |
| Casos privados | Excluidos |
| Casos públicos verificables | Admitidos sólo en `public_cases/` |

## Pruebas automatizadas

La suite Python contiene **143 tests deterministas**, incluidos módulos aislados, firewalls metodológicos y una ejecución sintética completa M00–M31.

El workflow `Núcleo Python` ejecuta:

1. instalación editable del paquete;
2. `python -m unittest discover -s tests -p "test_*.py" -v`;
3. el validador del contrato público.

El workflow `Contrato público` ejecuta de forma independiente:

`python scripts/validate_public_contract.py`

El validador comprueba, entre otros:

- sincronía de versiones públicas;
- existencia de archivos normativos;
- secuencia M00–M31;
- integridad fuente↔concepto↔genealogía;
- correspondencia schema↔fixture;
- techos inferenciales;
- afirmaciones doctrinales;
- discriminadores;
- pipeline preencarnatorio;
- contratos de ejecución M00–M31;
- prueba FULL sintética;
- reglas de privacidad/publicación.

La validación automatizada demuestra coherencia de implementación con las reglas publicadas. No constituye validación científica de la astrología ni convierte índices de encaje en probabilidades metafísicas.

## Validación externa

**Infraestructura:** LISTA PARA PRERREGISTRO.  
**Holdout externo real:** NO EJECUTADO.

La infraestructura incluye:

- protocolo de validación externa;
- schemas de caso y ejecución;
- manifiesto de cohortes;
- endpoints EV1–EV8;
- flujo ciego estructura → apertura documental;
- controles de contaminación/ajuste al caso;
- fixture sintético de prueba de humo.

Hasta ejecutar cohortes holdout reales preregistradas, ALMAS no declara validación empírica externa de llama gemela, alma gemela, contrato álmico u otras ontologías metafísicas.


## Validación de la ampliación personal PDF

La ampliación de informes personales en ALMAS 1.11.0 está cubierta por **10 tests deterministas** adicionales dentro de la suite total de 143.

Se verifican:
- canonical personal READY/PARTIAL/BLOCKED;
- degradación por calidad de hora natal C/D;
- bloqueo de casas de retorno sin localidad documentada;
- routing modular de referencias;
- inmutabilidad del canonical;
- determinismo de los cinco perfiles;
- rechazo de perfiles desconocidos;
- propagación de warnings de cálculo;
- rechazo de colecciones de retornos mal tipadas;
- exclusión del router para capas marcadas explícitamente como no disponibles.

Sobre el HEAD de integración, GitHub Actions ejecutó correctamente:
- **Núcleo Python: SUCCESS** — 143 tests, OK, y validador público PASS;
- **Contrato público: SUCCESS**.

La ampliación no modifica M00–M31, fórmulas IEM/IDD/IRC/IAT/ICC/ICE, thresholds, ontología ni discriminadores.
