# Invariantes · M31 report document model

Una release falla si:

1. M31 genera modelo documental con un gate BLOCKED.
2. M31 acepta un gate reportable sin canonical_fingerprint.
3. M31 acepta un canonical cuyo fingerprint ya no coincide con M30.
4. M31 modifica canonical_analysis.
5. M31 copia valores analíticos dentro del modelo documental.
6. M31 genera narrativa interpretativa.
7. M31 genera DOCX o PDF.
8. M31 selecciona silenciosamente un perfil de renderizado.
9. M31 ejecuta preflight PDF.
10. M31 expone un número de secciones distinto de once.
11. El orden de secciones no es determinista.
12. Una sección omite la diferencia entre rutas disponibles y ausentes.
13. Una sección sin rutas obligatorias disponibles se presenta READY.
14. Un informe PARTIAL no conserva degradation_reasons.
15. Un informe PARTIAL no exige disclosure explícito.
16. El documento deja de declarar canonical_analysis como fuente analítica.
17. canonical_fingerprint_verified puede ser distinto de true.
18. canonical_values_embedded puede ser distinto de false.
19. canonical_values_mutated puede ser distinto de false.
20. publication_pipeline_required puede ser distinto de true.
21. Si ontological_discrimination existe, S06 debe conservar esa ruta canónica.
22. S08 y S11 deben conservar la ruta ontological_discrimination.promotion_trace.
23. M31 no puede copiar promotion_ref ni otros valores ontológicos fuera de canonical_analysis.
24. La ambigüedad SHARED_ORIGIN_UNDIFFERENTIATED/INDETERMINATE no puede perderse por omisión de ruta.

## Paso 17 · Reporting metodológico de discriminadores

1. `promotion_reporting` debe existir en el modelo documental M31.
2. `promotion_reporting` deriva del registro canónico de promoción y de `ALMAS_PROMOTION_STATE_MACHINE_V1`, no del contenido narrativo del caso.
3. `promotion_reporting.methodological_status_only` debe ser `true`.
4. `promotion_reporting.ontological_inference_allowed` debe ser `false`.
5. `promotion_reporting.case_classification_mutated` debe ser `false`.
6. `promotion_reporting.irc_mutated` debe ser `false`.
7. Cada discriminador reportado debe mantener `ontological_weight=0`.
8. Cada discriminador reportado debe mantener `can_change_case_classification=false`.
9. Cada discriminador reportado debe mantener `can_raise_irc=false`.
10. S08 y S11 deben declarar `methodological_reporting_paths=["promotion_reporting"]`.
11. El snapshot metodológico no modifica el fingerprint de `canonical_analysis`.
12. `promotion_trace` describe L3 usados en el caso; `promotion_reporting` describe el estado metodológico del registro y no debe confundirse con evidencia de caso.
13. Un candidato EXPLORATORY/BLOCKED/RETIRED debe poder aparecer en el informe sin que ello eleve su autoridad ontológica.
14. `validated_discriminator_ids=[]` debe seguir reportándose como cero L3 mientras no exista una promoción real.

## Paso 18 · Genealogía documental de discriminadores

1. `promotion_reporting.source_genealogy` debe existir en el pipeline productivo.
2. Su autoridad debe ser `ALMAS_CANONICAL_DISCRIMINATOR_SOURCE_GENEALOGY`.
3. Debe mantener `methodological_provenance_only=true`.
4. Debe mantener `ontological_inference_allowed=false`.
5. `source_count_adds_weight=false`.
6. `source_priority_adds_ontological_weight=false`.
7. `cross_tradition_identity_allowed=false`.
8. Cada OD debe conservar `direct_case_evidence=false`.
9. Cada OD debe conservar `can_change_case_classification=false`.
10. Cada OD debe conservar `can_raise_irc=false`.
11. Los límites `does_not_support` deben conservarse junto a los apoyos.
12. Las no-equivalencias doctrinales deben mantenerse explícitas.
13. La genealogía no modifica el fingerprint de `canonical_analysis`.
14. La genealogía no convierte P1 en ground truth de una díada.
15. La genealogía no modifica el estado de promoción del discriminador.
