# Invariantes · Genealogía de fuentes de discriminadores

1. La autoridad canónica es `ALMAS_CANONICAL_DISCRIMINATOR_SOURCE_GENEALOGY`.
2. Deben existir exactamente OD01–OD07.
3. `derived_from` debe coincidir con el registro de candidatos operacionales.
4. Toda `source_id` debe existir en `reference/source-registry.json`.
5. Priority, role, tradition, author, work y metadatos de ancla del snapshot deben coincidir con el registro fuente.
6. Todo `support_index` debe apuntar a un elemento existente de `supports[]`.
7. Todo `does_not_support_index` debe apuntar a un elemento existente de `does_not_support[]`.
8. Cada uso de fuente debe conservar al menos un límite `does_not_support`.
9. Toda relación de `required_genealogy_edges` debe existir literalmente en `reference/doctrinal-genealogy.json`.
10. Toda `forbidden_equivalence` debe estar respaldada por `not_equivalent_to` o por una relación genealógica explícitamente no identitaria.
11. P1–P6 no añade peso ontológico.
12. El número de fuentes no añade IEM, IDD o IRC.
13. Una fuente doctrinal P1 no convierte una operacionalización ALMAS en C_DOCTRINE.
14. OD01/OD02/OD04 conservan techo `PROJECT_PROXY_ONLY`.
15. OD03 conserva techo `CONSTRUCT_SEPARABILITY_ONLY`.
16. OD05/OD06 conservan techo `DOCTRINAL_CONCEPT_ONLY`.
17. OD07 conserva techo `PHENOMENOLOGY_ONLY`.
18. Toda genealogía de OD mantiene `direct_case_evidence=false`.
19. Toda genealogía de OD mantiene `can_change_case_classification=false`.
20. Toda genealogía de OD mantiene `can_raise_irc=false`.
21. Platón y Brihadaranyaka son comparanda/antecedentes, no identidad histórica automática con twin flame.
22. Mónada teosófica y Mónada–alma–personalidad no equivalen a twin flame.
23. Fenomenología soulmate/twin-flame no constituye ontología.
24. Autoetiqueta contemporánea no constituye verificación doctrinal.
25. La genealogía histórica y la promoción metodológica son ejes independientes.
