# ALMAS 1.13.0 · Cierre cuantitativo estructural

## Estado

Documento de evolución en la rama `evolution/1.13.0-quantitative-closure`.

La finalidad de 1.13.0 es retirar entradas numéricas manuales del flujo FULL
cuando puedan derivarse de forma determinista a partir de la evidencia
canónica. Ninguna regla se ajusta a un caso real concreto.

## Fase Q1 · Fuerza automática de raíces

La primera fase cierra el hueco M17 señalado en 1.12.0.

Política canónica:

`ALMAS_ROOT_STRENGTH_BASELINE_V1`

Fórmula conservada:

`S = F × technique_reliability × birth_time_factor × aspect_coefficient`.

La baseline utiliza coeficientes 1.0 de forma deliberada. Esto no afirma que
todas las técnicas tengan la misma validez empírica; evita inventar diferencias
de peso antes de disponer de una calibración externa preregistrada.

La incertidumbre horaria no se penaliza en M17. Se mide en M23 y se integra en
M25, evitando doble penalización.

La agregación de raíz es `MAX_CORE_EVIDENCE`: una raíz estructural adopta la
mayor fuerza de sus evidencias core ya deduplicadas. Una evidencia
`support_only` puede conservar fuerza diagnóstica, pero nunca sustituye
evidencia core ni convierte una raíz en core-eligible.

## Fase Q2 · Atribución automática raíz → pilar

Q2 queda implementada mediante la política congelada
`ALMAS_ROOT_PILLAR_ATTRIBUTION_V1` y el motor
`src/almas_tfa/pillar_attribution.py`.

La atribución es una `E_PROJECT_HYPOTHESIS`, no una equivalencia doctrinal.
Cada raíz estructural puede recibir **un único pilar semántico primario**. Esto
impide que una misma raíz infle simultáneamente PA, PK, PE, PR, PT o PS.

La prioridad congelada es:

`PS → PK → PT → PE → PR → PA`.

Su función no es declarar una jerarquía metafísica entre esos pilares, sino
resolver solapamientos de manera determinista y conservadora:

- `PS`: misión/servicio sólo cuando existe eje meridiano, ancla de misión y
  recurrencia en al menos dos familias independientes;
- `PK`: Nodo/eje nodal o Saturno con contraparte estructural;
- `PT`: Plutón, Quirón o Urano con contraparte estructural;
- `PE`: relación de espejo dura entre puntos estructuralmente significativos;
- `PR`: coherencia relacional mediante Mercurio o eje de horizonte en relación
  coherente;
- `PA`: afinidad estructural para raíces relacionales que no hayan sido
  absorbidas por una firma más específica.

`PX` es excepcional: funciona como metapilar ortogonal de recurrencia. Una
raíz con pilar primario y al menos dos familias independientes puede alimentar
también PX. Las cargas brutas son 0.5/0.5 y se normalizan conforme a la regla
pública de ALMAS.

`PU` permanece siempre `NOT_EVALUABLE` en esta baseline. No se permite una
atribución automática de singularidad diádica sin discriminador previamente
validado y preregistrado.

M18 ahora prioriza `canonical.independent_roots`. Los adaptadores
`root_strengths` y `pillars` precomputados sólo se conservan como
compatibilidad legacy cuando no existen raíces canónicas evaluables.

La ausencia se convierte en cero únicamente si M03, M05, M06, M09 y M11 están
todos `COMPLETED`. Si la cobertura estructural es incompleta, la ausencia de
una raíz se mantiene como `NOT_EVALUABLE`, evitando convertir datos faltantes
en contraevidencia.

## Próximas fases

Q3: atribuciones automáticas por modelo para IDD M21.

Q4: generador de perturbación horaria y parametrización preregistrada para M23.

Q5: cuantificación canónica de ablación, perturbación paramétrica e IDD stability
para M25.

Q6: generadores de universos nulos para M24, manteniendo rareza estructural
separada de IRC y de cualquier probabilidad metafísica.

Q7: actualización del gate FULL, fixtures y release pública 1.13.0.
