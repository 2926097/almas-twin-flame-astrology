# Invariantes de cegamiento y leakage · Paso 15

Una release falla si ocurre cualquiera de estas condiciones:

1. Un L3 carece de `blinding_audit`.
2. `policy_id` no es `ALMAS_BLINDING_LEAKAGE_V1`.
3. La política deja de ser `E_PROJECT_POLICY`.
4. STEP_A recibe una autoetiqueta del caso.
5. STEP_A recibe narrativa relacional.
6. STEP_A recibe modelo o clasificación esperada.
7. STEP_A recibe truth/outcome del holdout.
8. Se silencian campos contaminantes en lugar de fallar explícitamente.
9. `development_evaluation_disjoint` no es verdadero.
10. `labels_hidden` no es verdadero.
11. `narrative_hidden` no es verdadero.
12. `expected_result_hidden` no es verdadero.
13. `holdout_outcome_hidden` no es verdadero.
14. No existe revelado documental tardío.
15. El fingerprint estructural cambia tras el revelado.
16. `forbidden_field_hits > 0`.
17. `LABEL_LEAKAGE > 0`.
18. `NARRATIVE_LEAKAGE > 0`.
19. `CASE_FITTING > 0`.
20. Existe cualquier cambio de regla después de abrir el holdout.
21. Una identidad `UNAVOIDABLE_PUBLIC` carece de auditoría de riesgo.
22. Una autoetiqueta se convierte en ground truth ontológico.
23. La narrativa revelada modifica retrospectivamente raíces o exclusiones.
24. Superar el gate de cegamiento se interpreta como demostración metafísica.

La clave `note` puede existir sólo como anotación semánticamente inerte; mutarla no puede alterar la decisión.
