# ALMAS · Hojas vacías de trabajo de custodia, cribado y doble codificación

**Clasificación:** `RESEARCH_TEMPLATE_ONLY / NOT_FOR_PUBLIC_COMPLETED_DATA`. Estas son **plantillas**, no registros rellenos, no una cohorte, no un consentimiento legalmente aprobado y no una autorización para tratamientos reales. Las hojas **cumplimentadas** deben residir únicamente en almacenamiento institucional o equivalente autorizado, fuera de este repositorio y de los mensajes de GitHub. Se aplican `docs/PRIVATE_CASE_ISOLATION_POLICY.md` y `ALMAS_PUBLIC_DATA_ISOLATION_V1`.

**Documento rector:** `docs/EXTERNAL_COHORT_OPERATIONS_PACKET_2026_10.md`. Elegir y registrar de antemano **RRA temporal** o **identidad diádica declarada** como estudio; no compartir silenciosamente el mismo holdout.

## Hoja A · Registro maestro de elegibilidad (solo custodio)

| Campo privado obligatorio | Formato/código y criterio |
|---|---|
| `screened_unit_ref` | Identificador interno aleatorio, no derivado de datos personales ni de un hash reversible |
| `screen_date` / `screening_rule_version` | Fecha real y criterio congelado anterior al cálculo |
| `recruitment_frame` / `invitation_channel` | Procedencia del universo y mecanismo completo de captación; registrar denominador y no solo aceptaciones |
| `participant_or_public_case_type` | `CONSENTED_PRIVATE` o `PREEXISTING_PUBLIC_VERIFIABLE` |
| `legal_basis_and_custodian_receipt` | Referencia reservada, tras validación del responsable jurídico; sin texto del consentimiento en GitHub |
| `two_birth_sources` / `time_quality` | Fuentes primarias o citas, procedencia por persona, discrepancias; **no** rectificar mirando aspectos |
| `relationship_documentary_source` | Naturaleza observable del vínculo y fuente, separada de etiquetas emic |
| `development_exposure` | `NO_KNOWN_EXPOSURE`, `KNOWN_DEVELOPMENT`, `PILOT`, `UNKNOWN_REVIEW` |
| `eligibility_decision` / `reason_code` | `INCLUDE_CANDIDATE`, `EXCLUDE`, `HOLD_FOR_REVIEW`; jamás asignación automática al holdout |
| `decision_timestamp` / `selection_reviewer` | Recibo firmado/fechado del selector documental sin acceso a sinastría |
| `source_conflict_resolution` | `UNRESOLVED`, `RESOLVED_WITH_DOCUMENT`, `NOT_APPLICABLE`, con procedencia |
| `downstream_split` | Solo una vez cerrado el grafo de personas, antes de observar resultados |

No crear fichas en la rama pública, ni aunque se cambien nombres por iniciales. El denominador público admisible se limita a agregados con protección contra reidentificación.

## Hoja B · Codificación independiente de acontecimientos

Dos codificadores **humanos distintos** reciben fuentes documentalmente elegibles sin las cartas ni los índices. Conservar los archivos A y B originales e independientes, fechados e inalterados, antes de cualquier conciliación.

| Campo | Valor/decisión esperados |
|---|---|
| `coded_unit_ref` / `coder_ref` | Referencias internas a la unidad y persona codificadora |
| `study_event_type` | Clase de evento incluida en el protocolo ex ante |
| `fact_key` | Identificador único del mismo hecho, sin duplicados |
| `event_date_assertion` | Fecha del hecho, no fecha de publicación de noticia |
| `event_date_precision` | `EXACT`, `INTERVAL`, `UNKNOWN`, con incertidumbre |
| `source_locator` / `source_accessed_on` | Referencia privada a página, acta, archivo o pasaje; fecha de acceso |
| `source_independence_group` | Misma agencia/noticia republicada cuenta como un solo origen |
| `event_presence_code` | `EVENT_OBSERVED`, `NO_EVENT_VERIFIED_WITH_COVERAGE`, `NOT_OBSERVED`, `AMBIGUOUS` |
| `coder_certainty` | Categorías y umbrales preregistrados, sin inferir certeza de una intuición |
| `notes_for_adjudication` | Afirmaciones documentales y conflictos, **no** aspectos o narrativas metafísicas |
| `original_file_digest` / `signed_at` | Hash y sello de conservación bajo control del custodio |

La hoja de adjudicación se crea **después**, identifica `A/B agree/disagree`, regla congelada, decisión motivada, codificador adjudicador, fuente nueva, fecha y revisión de acuerdos. Fijar coeficiente de acuerdo, umbral y manejo de missingness antes del análisis. No comunicar al operador estructural las anotaciones de resultado durante el Paso A.

## Hoja C · Ventanas y fechas control, para RRA temporal

| Campo | Requisito |
|---|---|
| `observation_unit_ref` | Referencia interna, sin identificar sujetos en informes públicos |
| `covered_interval_start/end` | Intervalo temporal con cobertura defendible para el evento **definido** |
| `coverage_method` | Diario diligenciado, registro institucional u otro método descrito y aceptado ex ante |
| `coverage_gaps` | Intervalos no observados; no se imputan como ausencia |
| `coverage_source_refs` | Referencias originales; acceso controlado |
| `event_opportunity` | Posibilidad real de observar el tipo de hecho en el intervalo |
| `control_sampling_frame` | Universo completo de días elegibles, no selección por carta |
| `control_sampling_rule_version` | Estratos de estación, calendario, edad, aniversarios y exclusiones |
| `sampling_seed` / `selection_timestamp` | Aleatorización reproducible, si la hay, antes de revelar resultados |
| `negative_status` | Solo `NO_EVENT_VERIFIED_WITH_COVERAGE` constituye control negativo candidato |
| `admissible_for_primary_endpoint` | Decisión revisada, no se infiere automáticamente por rellenar los campos |

**Regla obligatoria:** `NOT_OBSERVED != NO_EVENT_VERIFIED_WITH_COVERAGE`; `AMBIGUOUS` tampoco es control negativo. Si faltan garantías de observación negativa, mantener `NOT_EVALUABLE`. Los periodos sin noticia o un diario no completado nunca son por sí mismos control admisible.

## Hoja D · Grafo de dependencia y reparto

El custodio construye localmente un grafo con vértices para personas, vínculos y, cuando proceda, fuentes/eventos dependientes. Reconstruye los componentes conexos **antes** de asignar particiones. Un componente completo solo puede figurar en `DEVELOPMENT_ONLY`, `PILOT_ONLY`, `EXTERNAL_HOLDOUT` o `INDEPENDENT_REPLICATION`, sin solapamientos de personas ni cronologías reutilizadas. Registrar razón y fecha de cada exclusión. Una observación previamente examinada durante ajustes no se vuelve confirmatoria renombrando su identificador.

Campos de control: `component_ref`, `member_refs` (privados), `linked_fact_refs`, `exposure_flags`, `partition`, `partition_assignment_method`, `partition_frozen_at`, `partition_digest`, `reviewer_receipt`.

## Hoja E · Recibo de congelación y apertura

| Fase | Evidencia mínima previa y comprobación |
|---|---|
| `PREPARED` | Estudio elegido, población, método y criterios de inclusión, exclusión, evento, cobertura, tamaño/parada, pérdidas y estadístico; recursos y fuente de datos documentados |
| `FROZEN` | SHA y hash de versión, programas, orbes, aspectos, cuerpos, AB0–AB8, perturbaciones horarias, nulls, multiplicidad y anexos; timestamp íntegro |
| `REGISTERED` | Identificador verificable de registro anterior al acceso al holdout y copia sellada del protocolo; **no** basta un issue ni una PR |
| `BLINDED_EXECUTED` | Huella del resultado estructural sin etiquetas de pareja, narrativas ni eventos de respuesta revelados |
| `DOCUMENTARY_REVEALED` | Recibo posterior del custodio; log de acceso y de cualquier desviación |
| `EVALUATED` | Informe de denominadores, faltantes, controles, sesgos, negativos, intervalos, interpretación limitada al observable y auditoría externa |
| `REPLICATED` | Cohorte verdaderamente independiente, sin compartir personas/casos ni ajustar reglas tras resultados |

**Puerta de entrada:** una hoja rellenada sin fuentes/firmas, una URL sin sello temporal, un hash sin archivo verificable, una firma ficticia, un supuesto consentimiento no validado o un lote sintético **no** acreditan un hito. El estado sigue siendo `NO-GO` hasta auditoría real.

## Hoja F · Salida agregada pública admisible

Sin datos individuales ni cuasiidentificadores, y sujeta a una evaluación específica de riesgo de reidentificación, informar solamente: `study_protocol_ref`, `study_type`, `status`, `screened_total`, `eligible_total`, `excluded_total`, `component_count`, `coder_agreement_metric` y su denominador, `observed_period_count`, `verified_negative_period_count`, `non_evaluable_total`, `external_holdout_count`, `replication_count`, `registered_protocol_ref`, `frozen_commit`, `audit_receipt_ref`. Si el tamaño de celdas es pequeño o permite identificar sujetos, no publicar esos agregados hasta que se mitiguen los riesgos. Ningún campo de esta salida equivale por sí solo a una declaración de validación empírica.

**Corte inicial comprobado:** `external_holdout_count=0` en los manifiestos públicos; ninguna de estas plantillas está cumplimentada. El avance del issue #123 requiere actuaciones externas de personas responsables, no más pruebas sintéticas.
