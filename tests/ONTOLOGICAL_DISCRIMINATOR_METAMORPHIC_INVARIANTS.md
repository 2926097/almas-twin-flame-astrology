# Invariantes metamórficas · discriminador ontológico

Las relaciones metamórficas verifican que transformaciones equivalentes de la entrada no alteren una conclusión que no depende de dicha transformación.

## Identidad de salida

Deben conservar el output completo:

1. MR01 · permutar el orden de las observaciones;
2. MR02 · invertir el orden interno de cada par;
3. MR03 · duplicar exactamente una observación de la misma raíz;
4. MR04 · cambiar únicamente `note`;
5. MR05 · cambiar mayúsculas/minúsculas de `mode`;
6. MR06 · añadir evidencia L1 no discriminante;
7. MR08 · añadir observaciones `NOT_EVALUABLE` sin efecto decisorio;
8. MR10 · expresar `pair_coverage` como A_vs_B o B_vs_A;
9. MR12 · expresar una observación como Mapping o `PairObservation`;
10. MR13 · renombrar `discriminator_id` manteniendo la misma raíz no conflictiva;
11. MR15 · repetir exactamente la misma ejecución.

## Equivalencia semántica

Deben conservar la decisión confirmatoria aunque puedan cambiar metadatos exploratorios o de evidencia:

12. MR07 · añadir señales L2;
13. MR09 · permutar el orden de los modelos candidatos;
14. MR14 · dividir una evidencia concordante en varias raíces independientes que excluyen el mismo modelo.

La decisión semántica incluye:

- modelos excluidos confirmatoriamente;
- modelos supervivientes;
- estado de identificabilidad;
- estado epistemológico;
- clasificación;
- guardarraíl de falsa especificidad.

Para MR09 también deben conservarse, normalizados por par, los estados confirmatorios/exploratorios, cobertura, exclusiones y trazas de promoción.

## Rechazo obligatorio

15. MR11 · si A_vs_B y B_vs_A declaran coberturas incompatibles, la entrada debe rechazarse.

## Límite

Estas pruebas validan invariancia lógica y determinismo del software. No convierten un discriminador L1/L2 en L3 ni demuestran una ontología metafísica.
