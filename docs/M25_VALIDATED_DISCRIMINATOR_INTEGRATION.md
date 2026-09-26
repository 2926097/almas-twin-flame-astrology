# Integración de discriminadores ontológicos validados en M25

## Finalidad

M25 es el único agregador canónico de robustez de ALMAS. El tipo `VALIDATED_DISCRIMINATOR` ya existía, pero hasta esta fase podía declararse sin comprobar su relación con la nueva subcapa ontológica de M21.

Esta integración añade un firewall específico:

`L1_DOCTRINAL / L2_EXPERIMENTAL !-> IRC`

Sólo una señal declarada `L3_VALIDATED` y trazable a una raíz confirmatoria de `ontological_discrimination` puede entrar en M25 como `VALIDATED_DISCRIMINATOR`.

## Requisitos acumulativos

Un componente de tipo `VALIDATED_DISCRIMINATOR` debe cumplir simultáneamente:

1. `validation_level = L3_VALIDATED`;
2. `source_module = M21`;
3. `root_key` explícito;
4. existencia de `ontological_discrimination` en el snapshot canónico;
5. presencia de ese `root_key` dentro de `validated_roots`;
6. el par correspondiente debe tener `confirmatory_status = SEPARABLE_VALIDATED`;
7. `preregistration_ref` y `derivation_ref` siguen siendo obligatorios;
8. el valor de robustez debe permanecer en `[0,1]`.

Si falla cualquiera de estas condiciones, M25 rechaza el componente con `ValueError`.

## Qué no hace M25

M25 no convierte una señal L2 en L3.

M25 no determina por sí mismo que un discriminador ha sido validado externamente.

M25 no usa:

- IDD alto;
- IEM alto;
- rareza M24;
- número de sincronías;
- intensidad;
- autoetiqueta;
- score ontológico.

para autorizar un `VALIDATED_DISCRIMINATOR`.

La promoción a `L3_VALIDATED` pertenece al protocolo de validación externa y debe ocurrir antes de que M21 pueda ofrecer una raíz confirmatoria admisible.

## Conflictos

Aunque existan raíces L3 individuales, M25 no las acepta si el par M21 está en:

`CONFLICTING_EVIDENCE`.

El adaptador de M25 sólo extrae raíces de pares cuyo estado confirmatorio sea exactamente:

`SEPARABLE_VALIDATED`.

Esto evita que dos discriminadores L3 incompatibles aumenten IRC.

## Relación con IRC

Una vez superado el gate, el componente entra en la fórmula ya existente:

`IRC = 100 × geometric_mean(applicable_R_i)`

y:

`R_min = min(applicable_R_i)`.

No se crea una nueva fórmula ni un peso especial para la ontología.

La robustez describe estabilidad del sistema de discriminación, no probabilidad metafísica.

## Estado actual

La infraestructura ya puede consumir futuros discriminadores L3.

Sin embargo, esta fase no promueve ningún candidato actual a L3.

Los candidatos definidos en:

`reference/operational-discriminator-candidates.json`

continúan como L2 experimentales, limitados, bloqueados o rechazados según corresponda.

Por tanto, en datos reales actuales no debe aparecer un componente ontológico `VALIDATED_DISCRIMINATOR` salvo que exista una promoción metodológica posterior y documentada.

## Tests

`tests/test_m25_ontological_discriminator.py`

comprueba:

- rechazo L1;
- rechazo L2 aunque esté presente en la vista exploratoria de M21;
- rechazo L3 sin salida canónica M21;
- rechazo de raíz no coincidente;
- rechazo de `source_module` distinto de M21;
- rechazo de raíces pertenecientes a un par L3 conflictivo;
- aceptación de una raíz L3 confirmatoria coincidente;
- no interferencia con otros componentes de robustez.

## Invariante

La regla ejecutable queda fijada como:

`VALIDATED_DISCRIMINATOR_IN_IRC => L3_VALIDATED AND M21_CONFIRMED_ROOT`.

La implicación inversa no es automática: una raíz L3 confirmatoria no entra en IRC si no existe además un componente de robustez preregistrado y cuantificado.
