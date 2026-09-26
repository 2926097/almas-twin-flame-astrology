# Estado de validación

**Versión pública:** 1.12.0

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
| M02 natal / M08 Davison | Contratos ejecutables; backend de producción pendiente |
| Núcleo Python IEM/IDD/IRC | Publicado y probado unitariamente |
| Discriminación ontológica M21 | Ejecutable; separada de IDD; ambigüedad preservada si no existe L3 |
| Registro de promoción | Activo; `validated_discriminator_ids=[]` |
| Gate L3 hacia M25 | Ejecutable; ningún discriminador real autorizado actualmente |
| Validez discriminante / blinding | Políticas ejecutables; sin holdout externo real |
| Genealogía de discriminadores | OD01–OD07 trazados documentalmente |
| Aislamiento de casos privados | `ALMAS_PUBLIC_DATA_ISOLATION_V1` + manifests exhaustivos |
| CLI de pilares precomputados | Publicada y probada unitariamente |
| Corpus doctrinal | 38 fuentes / 92 conceptos / 73 relaciones |
| Fixtures sintéticos | Publicados |
| Casos privados | Excluidos |
| Casos públicos verificables | Admitidos sólo en `public_cases/` |

## Pruebas automatizadas

La suite Python contiene **266 tests deterministas**, incluidos módulos aislados, firewalls metodológicos y una ejecución sintética completa M00–M31.

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
**Discriminadores L3 reales:** NINGUNO.

La infraestructura incluye:

- protocolo de validación externa;
- schemas de caso y ejecución;
- manifiesto de cohortes;
- endpoints EV1–EV8;
- flujo ciego estructura → apertura documental;
- controles de contaminación/ajuste al caso;
- fixture sintético de prueba de humo.

Hasta ejecutar cohortes holdout reales preregistradas, ALMAS no declara validación empírica externa de llama gemela, alma gemela, contrato álmico u otras ontologías metafísicas.
