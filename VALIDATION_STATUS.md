# Estado de validación

**Versión pública:** 1.16.0

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
| M13 · lotes | `ALMAS_HELLENISTIC_LOTS_V1` como baseline histórica Fortuna/Espíritu |
| Núcleo Python IEM/IDD/IRC | Publicado y probado unitariamente |
| Q1 · fuerza automática M17 | `ALMAS_ROOT_STRENGTH_BASELINE_V1` |
| Q2 · raíz→pilar M18 | `ALMAS_ROOT_PILLAR_ATTRIBUTION_V2` + `ALMAS_SEMANTIC_MOTIF_V2` |
| Q3 · Shapley/IDD M21 | `ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V2` |
| Q4 · sensibilidad horaria M23 | `ALMAS_BIRTH_TIME_SENSITIVITY_V2` + curva R5/R15/R30/R60/R120 |
| Q5 · robustez automática M25 | `ALMAS_ROBUSTNESS_Q5_V1` |
| Q6 · universo nulo M24 | `ALMAS_NULL_WITHIN_YEAR_V1` |
| Q7 · ensamblaje canonical/M30 | `ALMAS_CANONICAL_ASSEMBLY_V2` + `ALMAS_ANALYSIS_PROFILES_V1` |
| S1 · calidad de recurrencia | `ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1` · diagnóstico, no scoring |
| S2 · calibración nula de recurrencia | `ALMAS_RECURRENCE_NULL_CALIBRATION_V1` · WITHIN_YEAR |
| S3 · controles sintéticos | `ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1` · deterministas, sin RNG |
| S4 · firewall cohortes externas | `ALMAS_EXTERNAL_RECURRENCE_COHORT_V1` |
| S5 · calibración externa | `ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1` · diagnóstico |
| S6 · freeze candidatos PX v3 | `ALMAS_PX_V3_CANDIDATE_FREEZE_V1` · registro canónico vacío |
| S7 · runner holdout PX v3 | `ALMAS_PX_V3_HOLDOUT_EVALUATION_V1` · agregado/fingerprint |
| S8 · gate de promoción PX v3 | `ALMAS_PX_V3_PROMOTION_GATE_V1` · elegibilidad no activa |
| S9 · firewall activación PX v3 | `ALMAS_PX_V3_ACTIVATION_FIREWALL_V1` · PX v2 sigue operativo |
| V1 · preregistro de validación | `ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1` · freeze previo al holdout |
| V2 · apertura holdout | `ALMAS_HOLDOUT_OPEN_GATE_V1` · apertura sin evaluación ni promoción |
| V3 · ledger de validación | `ALMAS_VALIDATION_EXECUTION_LEDGER_V1` · cadena append-only SHA-256 |
| V4 · continuidad de validación | `ALMAS_VALIDATION_CONTINUITY_GATE_V1` · certificado V1→V2→S7→V3 |
| V5 · cierre y auditoría de release | `ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1` · revelado tardío + cierre sin activación |
| Discriminación ontológica M21 | Ejecutable; separada de IDD; ambigüedad preservada si no existe L3 |
| Registro de promoción | Activo; `validated_discriminator_ids=[]` |
| Gate L3 hacia M25 | Ejecutable; ningún discriminador real autorizado actualmente |
| Validez discriminante / blinding | Políticas ejecutables; sin holdout externo real |
| Genealogía de discriminadores | OD01–OD07 trazados documentalmente |
| Aislamiento de casos privados | `ALMAS_PUBLIC_DATA_ISOLATION_V1` + manifests exhaustivos |
| CLI de pilares precomputados | Publicada y probada unitariamente |
| Corpus doctrinal | 40 fuentes / 97 conceptos / 73 relaciones |
| Fixtures sintéticos | Publicados |
| Casos privados | Excluidos |
| Casos públicos verificables | Admitidos sólo en `public_cases/` |

## Pruebas automatizadas

La suite Python contiene **434 tests deterministas**, incluidos módulos aislados, firewalls metodológicos, Q1–Q7, S1–S9 y una ejecución sintética completa M00–M31 sin shims cuantitativos manuales.

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

**Infraestructura:** LISTA PARA PRERREGISTRO, APERTURA, CONTINUIDAD Y CIERRE AUDITABLE. Q1–Q7 y la recurrencia semántica siguen reproducibles; 1.15 añadió calibración de especificidad S1–S9 y 1.16 añade Validation Operations V1–V5. No se ha ejecutado todavía un holdout externo real ni se activa PX v3.  
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
