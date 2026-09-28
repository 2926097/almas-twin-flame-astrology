# Política de cegamiento y leakage · Paso 15

## Finalidad

El Paso 15 convierte el blindaje narrativo en un firewall ejecutable.

La política canónica es:

`ALMAS_BLINDING_LEAKAGE_V1`.

Su clasificación epistemológica es:

`E_PROJECT_POLICY`.

Esta política protege la validez operacional del discriminador. No convierte la ontología metafísica en una verdad experimental.

## Dos fases obligatorias

### STEP_A_BLINDED

La fase estructural debe ejecutarse sin:

- autoetiquetas soulmate/twin-flame;
- narrativa relacional;
- modelo esperado;
- clasificación esperada;
- modelo que se espera excluir;
- pistas del analista;
- verdad del holdout;
- outcome conocido;
- narrativa post hoc.

El motor puede recibir los identificadores de los modelos comparados. Conocer los nombres `SOULMATE_MODEL` o `TWIN_FLAME_MODEL` como miembros del par no equivale a conocer la etiqueta del caso.

### STEP_B_DOCUMENTARY_REVEAL

Después de congelar la salida estructural pueden revelarse hechos documentales preregistrados para evaluar temporalidad, viabilidad, reciprocidad, cumplimiento, contraevidencia y uso contemporáneo.

Ese revelado no puede modificar retrospectivamente la salida estructural.

## Firewall de entrada M21

`ontological_discriminator_input` pasa por un escáner recursivo de claves.

Si contiene campos reservados a narrativa, etiqueta, resultado esperado o truth del holdout, M21 falla explícitamente con `BLINDING_LEAKAGE`.

No se silencian ni se eliminan campos contaminantes. El comportamiento es fail-closed.

La clave `note` permanece como anotación semánticamente inerte. Su contenido no participa en la decisión, y la suite metamórfica ya exige que mutarla no altere la salida.

## Fingerprints

ALMAS usa serialización JSON canónica y SHA-256.

Se congelan al menos:

- `structural_input_sha256`;
- `pre_reveal_output_sha256`;
- `post_reveal_structural_output_sha256`.

Para promoción L3:

`pre_reveal_output_sha256 == post_reveal_structural_output_sha256`.

Una diferencia implica que el revelado documental alteró la estructura y bloquea la promoción.

## Auditoría L3

Todo `VALIDATED_DISCRIMINATOR` debe incluir `blinding_audit`.

Son obligatorios:

- `policy_id=ALMAS_BLINDING_LEAKAGE_V1`;
- referencias de auditoría;
- referencias de entrada estructural;
- SHA-256 de entrada;
- SHA-256 de salida antes del revelado;
- SHA-256 estructural después del revelado;
- desarrollo y evaluación disjuntos;
- etiquetas ocultas;
- narrativa oculta;
- resultado esperado oculto;
- outcome del holdout oculto;
- revelado tardío realizado;
- invariancia estructural confirmada.

Además deben ser exactamente cero:

- `forbidden_field_hits`;
- `label_leakage_count`;
- `narrative_leakage_count`;
- `case_fitting_count`;
- `post_holdout_rule_change_count`.

## Identidad del caso

La identidad se registra como:

- `HIDDEN`;
- `PSEUDONYMIZED`;
- `UNAVOIDABLE_PUBLIC`.

ALMAS no presupone que todo caso público pueda cegarse completamente por identidad. Si la identidad es inevitablemente pública, debe existir `identity_risk_refs` que documente el riesgo.

Eso no autoriza revelar la autoetiqueta, la narrativa, el resultado esperado o la truth del holdout.

## CASE_FITTING

Cualquier cambio de regla, feature, peso, criterio o threshold después de abrir el holdout invalida el uso confirmatorio de esa ejecución.

Por ello:

`case_fitting_count = 0`

y

`post_holdout_rule_change_count = 0`

son requisitos de promoción.

## LABEL_LEAKAGE

Existe cuando una autoetiqueta o etiqueta externa del caso influye en la clasificación estructural.

Ejemplos prohibidos en STEP_A:

- “ellos se consideran twin flames”;
- “el caso está archivado como soulmate”;
- “el investigador espera TWIN_FLAME_MODEL”.

La autoetiqueta puede incorporarse después como `D_CONTEMPORARY_USAGE`, nunca como ground truth.

## NARRATIVE_LEAKAGE

Existe cuando la historia biográfica o relacional influye en una estructura que debía haberse calculado sin esa narrativa.

Ejemplos:

- conocer separación/reunión y después ajustar el discriminador;
- usar intensidad o sufrimiento para reforzar una exclusión ontológica;
- introducir eventos posteriores antes de congelar la arquitectura;
- reinterpretar raíces después de leer la historia.

## Relación con la validación discriminante

El Paso 14 y el Paso 15 son gates independientes.

Un discriminador puede tener sensibilidad/especificidad aparentemente adecuadas y aun así quedar bloqueado por leakage.

Asimismo, un protocolo perfectamente ciego no compensa una mala validez discriminante.

Para L3 deben superarse ambos.

## Invariancia por revelado tardío

La función canónica:

`assert_late_reveal_invariance(pre, post)`

calcula ambos fingerprints y falla si difieren.

Esto prueba una propiedad concreta:

el Paso B documental no puede reescribir el Paso A estructural.

No prueba que la ontología metafísica sea verdadera.

## Estado actual

El registro productivo continúa con:

`validated_discriminator_ids = []`.

Todos los registros actuales llevan:

`blinding_audit = null`.

Por tanto, ningún candidato puede adquirir autoridad L3 bajo esta política.

## Siguiente paso

El Paso 16 formalizará el ciclo de promoción completo:

`EXPLORATORY → REPRODUCIBLE → REPLICATION_READY → CONFIRMATORY_ELIGIBLE → VALIDATED_DISCRIMINATOR`

con transiciones reproducibles y gates acumulativos.
