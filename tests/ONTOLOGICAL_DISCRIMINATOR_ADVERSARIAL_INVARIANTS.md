# Invariantes adversariales · discriminador ontológico

Esta batería intenta producir falsa especificidad mediante entradas sintéticas hostiles.

Una release falla si ocurre cualquiera de estas condiciones:

1. Un volumen arbitrario de observaciones L1 produce una exclusión confirmatoria.
2. Un volumen arbitrario de observaciones L2 produce una exclusión confirmatoria.
3. Repetir una misma raíz L3 la convierte en varias raíces independientes.
4. Un conflicto interno de la misma raíz L3 elimina un modelo.
5. Un ciclo de exclusiones que elimina todos los candidatos produce una clasificación específica.
6. Observaciones NOT_EVALUABLE actúan como contraevidencia por defecto.
7. Una separación L2 invalida una equivalencia L3 registrada con cobertura completa.
8. Un L3 validado para un par convierte pares no validados en SEPARABLE_VALIDATED.
9. minimum_data_evaluable=false permite exclusiones confirmatorias.
10. Autoetiqueta, runner/chaser, intensidad, destino o sincronicidad alteran la salida ontológica M21.
11. Rareza astrológica o una afirmación temporal altera la clasificación ontológica sin discriminador validado.
12. Un par distinto del registrado puede reutilizar un promotion_ref L3.
13. Una root_key fuera de la familia registrada puede reutilizar un promotion_ref L3.
14. Un registro sin holdout externo completo puede autorizar L3.
15. El ataque exploratorio que elimina todos los modelos modifica la decisión canónica.

Los fixtures son exclusivamente sintéticos. Estos invariantes prueban resistencia operacional del clasificador; no validan una ontología metafísica.
