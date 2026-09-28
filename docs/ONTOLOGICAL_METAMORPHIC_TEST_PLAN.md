# Plan de pruebas metamórficas · discriminador ontológico · Paso 12

## Objeto

La prueba convencional necesita un oráculo esperado para cada caso. Las pruebas metamórficas añaden relaciones entre ejecuciones: si una transformación de la entrada no cambia el contenido epistemológicamente relevante, la salida debe permanecer idéntica o semánticamente equivalente según el tipo de transformación.

## Dos niveles de oráculo

### FULL_OUTPUT_IDENTITY

Se exige igualdad completa del objeto de salida cuando la transformación sólo cambia representación u orden sin añadir información decisoria.

Ejemplos:

- permutación de observaciones;
- inversión del par A/B;
- duplicación exacta de una observación;
- modificación de `note`;
- representación Mapping frente a dataclass;
- orientación de la clave `pair_coverage`.

### SEMANTIC_DECISION_IDENTITY

Se admite que cambien metadatos exploratorios, orden de presentación o inventario de raíces, pero no:

- exclusiones confirmatorias;
- supervivientes;
- identificabilidad;
- estado epistemológico;
- clasificación;
- falsa especificidad.

Se aplica, entre otros, a reordenación de modelos, adición de L2 y multiplicación de raíces concordantes.

## Hallazgo del Paso 12

Antes de ejecutar la suite se detectó que `pair_coverage` dependía de la orientación textual del par. Con modelos reordenados, `A_vs_B=COMPLETE` podía convertirse silenciosamente en cobertura por defecto si el motor buscaba `B_vs_A`.

La corrección hace la consulta bidireccional:

- A_vs_B y B_vs_A son equivalentes;
- si ambas existen y coinciden, se acepta la cobertura;
- si ambas existen y discrepan, se rechaza la entrada.

## Relaciones MR01–MR15

La suite cubre orden de observaciones, orientación de pares, idempotencia, ruido L1/L2, NOT_EVALUABLE, orden de modelos, cobertura bidireccional, representación de entrada, alias de discriminador con misma raíz, multiplicidad de raíces concordantes y determinismo repetido.

## Criterio de cierre

El Paso 12 sólo se cierra si:

- toda la suite metamórfica pasa en Python 3.10 y 3.12;
- el contrato público exige los nuevos artefactos;
- no se modifica VERSION;
- no se promociona ningún candidato;
- no se cambian fórmulas IEM/IDD/IRC/IAT/ICC/ICE.

## Siguiente fase

El Paso 13 formalizó la independencia de la astrología: una señal astrológica no podrá actuar como discriminador ontológico salvo validación discriminante independiente, con controles negativos, dependencia de raíces y prueba fuera de muestra.
