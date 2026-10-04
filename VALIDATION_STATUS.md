# Estado de validación

**Versión pública:** 1.26.0

## Release 1.26.0 · Jyotiṣa Relacional observacional

El núcleo VED, sus cuatro capas D1/D9, Vimśottarī, eventos, sensibilidad y auditoría descriptiva son optativos; el efecto sobre scoring es cero. Aṣṭakūṭa completo, Prāṇapada, Yogatārās y el índice escalar IVED no se declaran implementados/validados. La verificación técnica no constituye validación empírica externa. 43 pruebas VED y batería local de 1.139 pruebas PASS, con cinco integraciones largas separadas y sin declaración de PASS íntegro. La publicación remota está pendiente. Resultados y alcance en `docs/RELEASE_AUDIT_1.26.0.md`.

## Release 1.25.0 · SSAR experimental

Las diez fases técnicas incorporan lotes, integración temporal/M27, controles, congelación y bloque canónico optativo. Las nueve ablaciones del pipeline M00–M31 conservan las salidas core. La política experimental está congelada; la métrica principal no está operacionalizada y la validación externa permanece `NOT_PERFORMED`. Los controles sintéticos no son evidencia de eficacia empírica. Auditoría: `docs/RELEASE_AUDIT_1.25.0.md`.

## Release 1.24.1 · Corpus y doctrina

La ampliación incorpora 25 fuentes y conserva nueve textos íntegros pendientes. Distingue atribución doctrinal, método y síntesis ALMAS, contra-doctrina y familias conservadoras de dependencia; añade trazabilidad personal sin alterar scoring ni L3. La regresión local pasa **786 pruebas**, incluidas **17 pruebas del corpus**; contrato público PASS con y sin extras. La verificación remota corresponde al SHA de la PR. Auditoría: `docs/RELEASE_AUDIT_1.24.1.md`.

## Release 1.24 · Surrender y retirada vestal

Se incorpora una extensión exploratoria por sujeto y ventana para abstinencia, celibato elegido, retirada vestal y cuatro dimensiones de surrender. Se verifican contratos, deduplicación transitiva, contraevidencia, aislamiento de sujeto, conservación de índices e integración M27/M30/M31 y personal. El corpus añade siete fuentes y ocho conceptos con no equivalencias explícitas. La revisión independiente detectó y corrigió casos de borde; no existe validación empírica externa del constructo ni cálculo nuevo de cartas privadas. Cierre local: **769 tests PASS**, incluidos **41 controles específicos**, y contrato público **PASS** sin dependencias opcionales. El corpus y sus schemas también pasan. La verificación remota se consulta por el SHA de la PR. Detalle en `docs/RELEASE_AUDIT_1.24.0.md`.

## Release 1.23 · Chiron–Nodal Integration Engine

Se implementa la extensión personal optativa Venus–Nodo–Quirón con dual-node True/Mean, solver temporal de múltiples perfeccionamientos, grupos de dependencia, auditoría de técnica exploratoria, secuencia de proceso y gate M27 para integración documentada. Los canonical personales anteriores siguen válidos. Verificación local cerrada: **728 tests PASS** y contrato público **PASS** (32 módulos, 77 fuentes). Gates locales DOCX (6 tests + fixture) y PDF (4 tests + fixture B5 de 13 páginas) también pasan. No se han lanzado workflows remotos ni matrices Python 3.10/3.12; detalles en `docs/RELEASE_AUDIT_1.23.0.md`.

## Release pública

### Cierre 1.22 · evolución matemática cuantitativa

ALMAS 1.22 versiona explícitamente las tres correcciones matemáticas que no se introdujeron silenciosamente en 1.21: Shapley root-only con PX/PS como interacciones recalculadas, IRC agrupado por dependencia e ICE autónomo fail-closed con declaración de completitud.

La implementación cuantitativa de PR #72 ha superado el gate completo sobre `5c71949a7a476d8285d843d6c4e13ee6047c9936`:

- Python 3.10: **596 tests**, PASS, 10 skipped, 88.677 s;
- Python 3.12: **596 tests**, PASS, 10 skipped, 86.210 s;
- Contrato público: PASS;
- Backend astronómico: PASS;
- Publicación DOCX: PASS;
- Publicación PDF: PASS.

La auditoría detallada y los run IDs se registran en `docs/RELEASE_AUDIT_1.22.0.md`.

No se ha ejecutado un holdout externo real; PX v3 y los discriminadores L3 continúan inactivos. La validación automatizada de 1.22 prueba coherencia interna y regresión contractual, no verdad científica ni probabilidad metafísica.

El repositorio publica una especificación generalizada con fixtures sintéticos y un núcleo Python determinista. Los casos privados/no públicos permanecen excluidos.

### Cierre 1.21 · informes personales

ALMAS 1.21 porta el reporting astrológico personal a la arquitectura vigente sin crear una segunda skill ni un segundo backend. La cadena personal queda:

`personal_report_request → backend de producción → personal_canonical_analysis → personal_report_document_model → personal_authored_report → DOCX/PDF B5`.

El canonical personal aplica minimización por lista blanca; los perfiles degradan de forma explícita por calidad horaria y conservan contraevidencia y clases A/B/C/D/E. `ALMAS_PERSONAL_REFERENCE_ROUTER_V1` resuelve dominios contra las **76 fuentes** del registro canónico y expone gaps sin inventar referencias.

Validación funcional previa al cierre SemVer:
- Núcleo Python 3.12: **574 tests**, PASS, 10 skipped por extras opcionales;
- Contrato público: PASS;
- Backend astronómico: PASS;
- Publicación DOCX: último run aplicable en `main`, PASS;
- Publicación PDF: último run aplicable en `main`, PASS.

La release no cambia scoring relacional, thresholds, discriminadores, ontología ni la revisión interna del módulo contractual.

### Cierre 1.20 · síntesis root-first y temporalidad trazable

La capa interpretativa profundiza la arquitectura ya calculada sin introducir una segunda verdad analítica. La autoría parte de raíces y motivos semánticos, recupera sus contactos concretos y añade contexto natal, relacional, dracónico, de lotes y puntos secundarios únicamente cuando está disponible en el canonical.

La temporalidad M26 conserva `trigger_context` para autoría y el generador `TTRANSIT` deriva contactos planeta en tránsito → aspecto mayor declarado → endpoint natal de una raíz existente. La lectura sintética de referencia sigue la secuencia `raíz → función transitante → función objetivo → geometría → integración → función evolutiva → límite factual`.

En la PR de cierre 1.20.0:

- Núcleo Python 3.10: 537 tests, PASS (7 skipped);
- Núcleo Python 3.12: 537 tests, PASS (7 skipped);
- Contrato público: PASS;
- Backend astronómico: PASS;
- Publicación DOCX: PASS;
- Publicación PDF: PASS;
- fixture temporal enlazado a la señal M26 generada: PASS.

1.20 no añade scores, pesos, thresholds ni discriminadores activados. La interpretación temporal describe activación simbólica y no constituye predicción factual.

### Cierre 1.19 · autoría y publicación

La cadena documental se encuentra implementada hasta PDF B5 validado:

`canonical_analysis → M30 → M31 → authored_report → DOCX → PDF → preflight → inspección visual`.

En el cierre funcional de 1.19:

- Núcleo Python 3.10/3.12: 498 tests, PASS;
- Contrato público: PASS;
- Publicación DOCX: PASS;
- Publicación PDF: 3 tests materiales, PASS;
- Backend astronómico: PASS como regresión independiente;
- QA visual: 13/13 páginas B5 inspeccionadas sin cortes, solapamientos ni desbordes.

Este cierre valida coherencia de implementación y materialización. No constituye validación científica de la astrología ni de las ontologías metafísicas.

### Capas vigentes

| Capa | Estado |
|---|---|
| Metodología normativa | Publicada |
| Schemas de entrada bruta/canónica | Publicados |
| Manifiesto arquitectónico | `manifests/almas-module-manifest.json` |
| Manifiesto estructural normativo | `ALMAS_STRUCTURAL_POLICY_MANIFEST_V1` · técnica/dependencia/orbes/loading |
| Backend astronómico de producción | `ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1` · Moira 6.8.2 + kernel local SHA-256 |
| Gate astronómico dorado | `ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1` · `COMPLETE_GATE` PASS en Python 3.10/3.12 · 6 casos × 47 medidas |
| Contrato `canonical_analysis` | Draft 2020-12 · raíz cerrada · composición `$ref` especializada · salida M30/FULL validada |
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
| M02 natal / M08 Davison | `ALMAS_MOIRA_JPL_SPK_V1` · ejecutables con kernel JPL local fingerprintado |
| M13 · lotes | `ALMAS_HELLENISTIC_LOTS_V1` como baseline histórica Fortuna/Espíritu |
| Núcleo Python IEM/IDD/IRC | Publicado; 1.22 añade Shapley V3, IRC agrupado e ICE autónomo |
| Q1 · fuerza automática M17 | `ALMAS_ROOT_STRENGTH_BASELINE_V1` |
| Q2 · raíz→pilar M18 | `ALMAS_ROOT_PILLAR_ATTRIBUTION_V2` + `ALMAS_SEMANTIC_MOTIF_V2` |
| Q3 · Shapley/IDD M21 | `ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V3` · raíces como únicos jugadores; PX/PS como interacciones |
| Q4 · sensibilidad horaria M23 | `ALMAS_BIRTH_TIME_SENSITIVITY_V2` + curva R5/R15/R30/R60/R120 |
| Q5 · robustez automática M25 | `ALMAS_ROBUSTNESS_Q5_V1` + agrupación de dependencia IRC |
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
| Corpus doctrinal/técnico | 77 fuentes / 98 conceptos / 73 relaciones |
| Fixtures sintéticos | Publicados |
| Casos privados | Excluidos |
| Casos públicos verificables | Admitidos sólo en `public_cases/` |

## Pruebas automatizadas

La suite Python contiene **574 tests deterministas**, incluidos módulos aislados, firewalls metodológicos, Q1–Q7, S1–S9 y una ejecución sintética completa M00–M31 sin shims cuantitativos manuales.

El workflow `Núcleo Python` ejecuta:

1. instalación editable del paquete con el extra `schema-validation` fijado a `jsonschema==4.26.0`;
2. `python -m unittest discover -s tests -p "test_*.py" -v`;
3. validación Draft 2020-12 del `canonical_analysis` sintético M30 y del pipeline FULL M00–M31;
4. el validador del contrato público.

El workflow `Contrato público` ejecuta de forma independiente:

`python scripts/validate_public_contract.py`

El workflow `Backend astronómico` instala los extras astronómicos de validación en Python 3.10/3.12 y verifica los contratos Moira/Skyfield. Las matrices reales descargan explícitamente el `de440s.bsp` preregistrado desde JPL/NAIF, verifican SHA-256 y MD5 y ejecutan `PLANETARY_REFERENCE`, `TRUE_NODE_REFERENCE`, `HOUSE_REFERENCE` y `COMPLETE_GATE`. Las cuatro etapas están en PASS en Python 3.10 y 3.12. El gate completo evalúa 282 medidas por entorno (47 por cada uno de los seis casos), sin fallos y con resúmenes idénticos entre ambas versiones de Python.

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

**Infraestructura:** LISTA PARA PRERREGISTRO, APERTURA, CONTINUIDAD Y CIERRE AUDITABLE. Q1–Q7 y la recurrencia semántica siguen reproducibles; 1.15 añadió calibración de especificidad S1–S9, 1.16 Validation Operations V1–V5, 1.17 formalizó técnica/dependencia/orbes/loading y 1.18 incorpora un backend astronómico de producción opcional y fail-closed. No se ha ejecutado todavía un holdout externo real ni se activa PX v3.  
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

## RRA · revisión 1.25.0 R3

Retornos y overlays experimentales con políticas congeladas. Contraste técnico Moira/Skyfield de Sol, Luna y Venus retrógrado: recibo en `validation/returns/runtime-receipt.json`. Pruebas de contratos, negativos, dependencia y pipeline: `tests/test_return_activation.py`. La validación relacional externa permanece **NOT_PERFORMED**; ningún caso personal se empleó para diseño. Los controles nulos son exploratorios, condicionales a referencias fijas; cartas EVENT que exigen recomputación quedan bloqueadas.
