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
