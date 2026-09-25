# Viabilidad real y reciprocidad factual · M29

## 1. Finalidad

M29 evalúa dos ejes independientes de la ontología relacional:

- `REAL_VIABILITY`: forma real y sostenible del vínculo según hechos documentados;
- `RECIPROCITY`: grado de bilateralidad interpersonal según hechos observables.

Estos ejes no se derivan de ORIGIN, PREINCARNATION_CONTRACT, FUNCTION, PHASE, intensidad, sincronías ni reciprocidad astrológica.

## 2. Fecha de corte

Toda evaluación declara `as_of_date`.

M29 describe únicamente el estado documental hasta esa fecha. Un evento posterior no puede usarse como prueba del estado anterior.

La salida no predice decisiones futuras.

## 3. Sujetos

La evaluación es diádica y exige exactamente dos sujetos distintos.

Cada base factual declara `subject_ids`. La unión de las bases que sostienen un estado evaluado debe cubrir a ambos sujetos.

La ausencia de evidencia de una de las partes no equivale a asimetría.

## 4. Eventos elegibles

Una base M29 sólo puede usar un evento M27 que cumpla simultáneamente:

- `record_status=ACTIVE`;
- rol `VIABILITY_FACT` o `RECIPROCITY_FACT`, según el eje;
- `documentary_quality_contract_met=true`;
- `date_precision_contract_met=true`;
- `fact_interpretation_separated=true`;
- calidad documental decisiva;
- cobertura de sujetos compatible;
- no ser posterior a `as_of_date` cuando la precisión registrada permite ordenarlo.

Calidades decisivas admitidas:

- `DQ1_PRIMARY_DOCUMENT`;
- `DQ2_DIRECT_SELF_REPORT`;
- `DQ3_CORROBORATED_REPORT`.

`DQ4_SECONDARY_REPORT` y `DQ5_UNVERIFIED` pueden aportar contexto en M27, pero no sostienen por sí solas una clasificación M29 fuerte.

## 5. Basis kinds de viabilidad

- `OBSERVED_STABLE_RELATIONSHIP` → `STABLE`;
- `OBSERVED_UNSTABLE_RELATIONSHIP` → `UNSTABLE`;
- `DOCUMENTED_SEPARATION` → `SEPARATED`;
- `EXPLICIT_NON_ROMANTIC_DEFINITION` → `NON_ROMANTIC`;
- `DOCUMENTED_NO_CONTACT` → `NO_CONTACT`;
- `OTHER_DOCUMENTED_RELATIONSHIP_FORM` → `DEFINED_BY_FACTS`.

Reglas especiales:

- `DOCUMENTED_SEPARATION` exige `event_type=SEPARATION`;
- `DOCUMENTED_NO_CONTACT` exige `event_type=NO_CONTACT`.

`UNKNOWN` no admite una base confirmatoria: expresa que los hechos disponibles no permiten asignar un estado más específico.

## 6. Basis kinds de reciprocidad

- `DOCUMENTED_BILATERALITY` → `BILATERAL`;
- `DOCUMENTED_PARTIAL_RECIPROCITY` → `PARTIAL`;
- `DOCUMENTED_ASYMMETRY` → `ASYMMETRIC`.

`NOT_EVALUABLE` no admite una base confirmatoria.

Para cualquier estado de reciprocidad evaluado, la base conjunta debe cubrir documentalmente a ambos sujetos. No se convierte silencio, ausencia de respuesta o falta de información en una posición interpersonal.

## 7. Tipos de observación

Cada base declara uno de:

- `EXPLICIT_STATEMENT`;
- `OBSERVABLE_ACTION`;
- `MUTUAL_AGREEMENT`;
- `BOUNDARY_OR_REFUSAL`;
- `DOCUMENTED_STATUS`.

El tipo de observación describe la naturaleza factual del soporte. No autoriza inferir estados mentales no documentados.

## 8. Firewalls

M29 fija siempre:

- `factual_basis_only=true`;
- `astrology_used_as_real_world_fact=false`;
- `metaphysical_claim_used_as_real_world_fact=false`;
- `phase_used_as_viability=false`;
- `phenomenology_used_as_reciprocity_fact=false`;
- `absence_used_as_asymmetry=false`;
- `mental_states_inferred=false`;
- `consent_inferred=false`;
- `fidelity_inferred=false`;
- `future_decisions_inferred=false`.

La astrología puede describir arquitectura simbólica; no sustituye hechos sobre la forma real del vínculo.

La metafísica puede aportar modelos interpretativos; no convierte esos modelos en consentimiento, reciprocidad o estabilidad interpersonal.

## 9. Entrada y salida

Entrada canónica:

`schemas/viability-reciprocity-assessment.schema.json`

Salida canónica:

`schemas/viability-reciprocity-output.schema.json`
