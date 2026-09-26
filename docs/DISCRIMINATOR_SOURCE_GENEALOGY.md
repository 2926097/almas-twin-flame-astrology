# Genealogía de fuentes de los discriminadores · Paso 18

## Finalidad

El Paso 18 conecta cada discriminador OD con la genealogía documental que lo motiva o limita.

La autoridad canónica es:

`ALMAS_CANONICAL_DISCRIMINATOR_SOURCE_GENEALOGY`.

Esta capa responde a:

“¿De qué doctrinas, comparanda, estudios académicos o usos contemporáneos procede este constructo y hasta dónde permiten llegar esas fuentes?”

No responde a:

“¿Qué ontología es verdadera en una pareja concreta?”

## Separación epistemológica

La genealogía conserva simultáneamente:

- A/B/C/D/E;
- prioridad P1–P6;
- rol de la fuente;
- tradición;
- autor;
- obra;
- fecha;
- pasaje/página cuando existe;
- estado de verificación;
- tipo de ancla;
- alcance de evidencia;
- conceptos enlazados;
- `supports[]`;
- `does_not_support[]`.

El límite documental tiene el mismo carácter obligatorio que el apoyo documental.

## Fuente no es peso

La capa fija:

`source_count_adds_weight=false`

`source_priority_adds_ontological_weight=false`.

Por tanto:

`3 fuentes P1 ≠ mayor probabilidad metafísica`.

La prioridad documental regula qué puede atribuirse a una tradición o autor. No cuantifica que una relación real pertenezca a una categoría espiritual.

## No equivalencia entre tradiciones

Cada OD puede declarar:

`required_genealogy_edges`

y:

`forbidden_equivalences`.

Ejemplos que deben permanecer activos:

- `SPLIT_PRIMORDIAL_BEING → TWIN_FLAME_ORIGIN = COMPARATIVE_ANTECEDENT_ONLY`;
- `MONAD → TWIN_FLAME_ORIGIN = NON_EQUIVALENT`;
- `THEOSOPHICAL_MONAD → TWIN_FLAME_ORIGIN = NON_EQUIVALENT`;
- `MONAD_SOUL_PERSONALITY → TWIN_FLAME_ORIGIN = NON_EQUIVALENT`;
- `SOULMATE_EXPERIENCE → TWIN_FLAME_ORIGIN = PHENOMENOLOGY_NOT_ONTOLOGY`;
- `TWIN_FLAME_EMIC_USAGE → TWIN_FLAME_ORIGIN = SELF_LABEL_NOT_DOCTRINAL_VERIFICATION`.

Esto impide convertir una semejanza formal en continuidad doctrinal.

## Techo por discriminador

### OD01, OD02 y OD04

`provenance_class=PROJECT_OPERATIONALIZATION`

`epistemic_ceiling=PROJECT_PROXY_ONLY`.

Las fuentes doctrinales motivan la pregunta; el observable es una construcción ALMAS.

Ni Summit Lighthouse ni ninguna otra fuente primaria define el proxy astrológico construido por ALMAS.

### OD03

`provenance_class=DOCTRINAL_SEPARABILITY_METHOD`

`epistemic_ceiling=CONSTRUCT_SEPARABILITY_ONLY`.

Puede evaluar si los constructos doctrinales son reproduciblemente distinguibles bajo codificación ciega.

No puede demostrar que una pareja real pertenezca a uno de ellos.

### OD05 y OD06

`provenance_class=NONOBSERVABLE_DOCTRINAL_CONSTRUCT`

`epistemic_ceiling=DOCTRINAL_CONCEPT_ONLY`.

Las fuentes permiten describir diferencias doctrinales, pero no proporcionan un observable externo que determine unidad preencarnatoria o fuente monádica común.

Por ello permanecen bloqueados.

### OD07

`provenance_class=CONTEMPORARY_PHENOMENOLOGY`

`epistemic_ceiling=PHENOMENOLOGY_ONLY`.

Stokke puede documentar experiencias reportadas de reconocimiento, sincronicidad y transformación.

No valida ontología soulmate/twin-flame.

## Anclas reforzadas

Durante el Paso 18 se completan las anclas documentales de:

- Alice A. Bailey, *Esoteric Psychology, Volume I*, Chapter II, Question 1;
- Elizabeth Clare Prophet, *Soul Mates and Twin Flames: Q and A Part 1*.

Esto permite conservar su uso como P1 doctrinal con localizador explícito sin ampliar lo que las fuentes dicen.

## Reporting

La capa ejecutable:

`src/almas_tfa/discriminator_source_genealogy.py`

produce para cada OD:

- fuentes;
- prioridad;
- rol;
- tradición;
- autor/obra;
- localizador;
- conceptos;
- relación con el discriminador;
- índices de `supports`;
- índices de `does_not_support`;
- relaciones genealógicas obligatorias;
- equivalencias prohibidas;
- techo epistemológico.

Todos los registros fijan:

`direct_case_evidence=false`

`can_change_case_classification=false`

`can_raise_irc=false`.

## Relación con los pasos 16–17

La genealogía no cambia el estado de promoción.

Un OD puede estar:

- EXPLORATORY;
- BLOCKED;
- RETIRED;
- o eventualmente VALIDATED_DISCRIMINATOR;

y conservar la misma procedencia doctrinal.

La promoción metodológica y la genealogía histórica son dimensiones distintas.

## Regla para un futuro L3

Incluso si un discriminador alcanza L3:

- las fuentes doctrinales continúan siendo fuentes de constructo;
- el holdout/replicación son la evidencia de validación operacional;
- la doctrina no se convierte retroactivamente en ground truth;
- la validez operacional no demuestra ontología metafísica.

## Siguiente paso

El Paso 19 aislará los casos privados del repositorio público y formalizará qué datos pueden entrar en ejemplos, fixtures, holdouts y documentación sin filtrar información personal ni contaminar la validación.
