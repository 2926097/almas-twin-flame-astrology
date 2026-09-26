# Invariantes · M30 report gate

Una release falla si:

1. M30 genera READY sin `canonical_analysis` suministrado o ensamblado correctamente por Q7.
2. M30 modifica valores del canonical.
3. Dos canonical divergentes raw/snapshot se resuelven silenciosamente.
4. Un módulo previo `FAILED` no bloquea.
5. Un módulo previo `NOT_EVALUABLE` o `SKIPPED` permite READY.
6. La ausencia de traza permite READY.
7. Un análisis TARGETED/TEMPORAL se etiqueta READY como si fuera FULL.
8. Un FULL carece de AF, KA, AG o LG y sigue READY.
9. Un modelo `NOT_EVALUABLE` conserva IEM numérico.
10. Un modelo evaluado conserva `iem=null`.
11. Un modelo `SUPPORTED` o `COMPATIBLE` puede existir con evidencia canónica vacía.
12. ICC o IRC fuera de 0–100 se aceptan.
13. El gate M30 inventa ICC, IRC, IAT, ICE o IDD; ICC/IDD sólo pueden llegar del ensamblador Q7 bajo su política congelada y el resto de sus módulos propietarios.
14. M30 altera contraevidencia, doctrina u ontología.
15. El gate no distingue `blocking_issues` de `degradation_reasons`.
16. Un canonical reportable no conserva `canonical_fingerprint`.
17. `canonical_values_mutated` puede ser distinto de false.
