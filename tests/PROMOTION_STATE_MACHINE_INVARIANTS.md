# Invariantes · Máquina de estados de promoción

1. La política canónica es `ALMAS_PROMOTION_STATE_MACHINE_V1`.
2. La secuencia ascendente es EXPLORATORY → REPRODUCIBLE → REPLICATION_READY → CONFIRMATORY_ELIGIBLE → VALIDATED_DISCRIMINATOR.
3. Ningún salto ascendente de más de un nivel es válido.
4. REPRODUCIBLE exige implementación, reproducibilidad y test sintético.
5. REPLICATION_READY conserva los requisitos previos y añade preregistro, contraevidencia, controles negativos y plan de leakage.
6. CONFIRMATORY_ELIGIBLE conserva los requisitos previos y añade replicación independiente, resultados de controles, Gate doctrinal, evaluación del discriminador, protocolo de holdout y exclusión support-only.
7. VALIDATED_DISCRIMINATOR debe superar todos los gates L3 ya existentes.
8. Un estado inferior a L3 no puede mantener l3_authorized=true.
9. VALIDATED_DISCRIMINATOR no admite rollback.
10. La invalidación de un L3 conduce a RETIRED.
11. RETIRED es terminal.
12. BLOCKED conserva last_active_status.
13. UNBLOCK sólo vuelve a last_active_status y exige block_resolution_refs.
14. transition_id es único por historial.
15. discriminator_id no puede modificarse en una transición.
16. root_key_prefix no puede modificarse en una transición.
17. uses_astrology no puede modificarse en una transición.
18. Cada transición aplicada conserva fingerprints before/after.
19. Los registros importados existentes no cambian de estado durante el Paso 16.
20. validated_discriminator_ids permanece vacío mientras no exista promoción real.
21. La máquina regula validez metodológica y no prueba ontología metafísica.
