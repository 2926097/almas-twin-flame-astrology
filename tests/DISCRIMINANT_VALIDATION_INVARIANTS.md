# Invariantes de validez discriminante · Paso 14

Una release falla si ocurre cualquiera de estas condiciones:

1. Un L3 carece de `discriminant_validation`.
2. `policy_id` no es `ALMAS_DISCRIMINANT_VALIDATION_V1`.
3. Desarrollo y evaluación no son disjuntos.
4. Falta un par declarado en `validated_pairs`.
5. CI95 inferior de sensibilidad < 0.60.
6. CI95 inferior de especificidad < 0.90.
7. balanced accuracy < 0.75.
8. CI95 superior de `FALSE_SPECIFICITY_RATE` > 0.05.
9. Existe falsa especificidad en controles sintéticos/adversariales.
10. Una salida probabilística no tiene calibración aprobada.
11. Una salida categórica inventa calibración probabilística.
12. El registro productivo actual autoriza L3 sin haber satisfecho estos criterios.
13. La tasa puntual sustituye al intervalo de incertidumbre.
14. Un par con mal rendimiento queda oculto mediante promedio global.
15. Las métricas se interpretan como probabilidad metafísica.

Estas invariantes validan el clasificador operacional y su política de promoción. No validan una ontología metafísica.
