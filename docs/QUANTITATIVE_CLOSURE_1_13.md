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

## Fase Q3 · Atribuciones automáticas por modelo e IDD

Q3 queda implementada mediante la política congelada
`ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V1` y el motor
`src/almas_tfa/model_attribution.py`.

M21 ya no necesita mapas `attributions` manuales cuando existe
`pillar_attribution` canónico evaluable. La función de valor congelada es
`IEM_pre`: se excluyen deliberadamente ICE, IEM_final, temporalidad, modelos
nulos y cualquier inferencia ontológica.

La unidad de atribución es la raíz independiente canónica. Para hasta 10 raíces
se calcula Shapley exacto. Para conjuntos mayores se utiliza una aproximación
determinista por permutaciones antitéticas, con semilla fija, máximo de 4096
permutaciones y control explícito de convergencia.

Las mismas permutaciones se reutilizan para AF, KA, AG y LG. Después se
normalizan las contribuciones sólo para calcular la divergencia Jensen–Shannon
y el IDD por pares.

El resultado conserva dos capas separadas:

- `model_attributions`: contribución Shapley de cada raíz al IEM_pre de cada
  modelo;
- `pairwise_idd`: separación distribucional AF↔KA↔AG↔LG.

Un IDD alto no se convierte en discriminador ontológico y no autoriza a elegir
entre origen monádico, split-soul, twin-soul o twin-flame.

Si la cobertura estructural Q2 es incompleta, la atribución automática queda
`NOT_EVALUABLE`. M21 conserva el adaptador legacy de atribuciones
precomputadas únicamente como compatibilidad transitoria.

## Fase Q4 · Perturbación horaria automática y componente BIRTH_TIME

Q4 queda implementada mediante la política congelada
`ALMAS_BIRTH_TIME_PERTURBATION_V1` y el motor
`src/almas_tfa/time_perturbation.py`.

La política usa una parrilla simétrica por fiabilidad horaria declarada:

- A: ±15 minutos, paso 5;
- B: ±30 minutos, paso 10;
- C: ±60 minutos, paso 15;
- D: ±120 minutos, paso 30.

Estas ventanas son una `E_PROJECT_POLICY` experimental y no una validación
empírica externa de las categorías A/B/C/D.

Para cada combinación de offsets de ambos sujetos se recalculan las capas
estructurales necesarias M02→M17 y se reconstruyen pilares e IEM_pre con las
mismas políticas Q1/Q2. La combinación 0/0 se usa como baseline y no cuenta
como perturbación.

La métrica principal es:

`delta_i = max_m |IEM_pre_m(perturbación) - IEM_pre_m(baseline)|`

para m ∈ {AF, KA, AG, LG}.

`delta90` utiliza percentil 90 por método `NEAREST_RANK`.

La fracción preservada G se define en esta baseline como la media de
preservación de las raíces core del baseline:

`G = mean(|roots_baseline ∩ roots_i| / |roots_baseline|)`.

El componente horario mantiene la fórmula pública:

`R_birth_time = exp(-delta90/20) × sqrt(G)`.

M23 genera automáticamente la parrilla sólo cuando se han inyectado backend
natal y backend Davison y ambos sujetos poseen hora, zona, localización y
`time_reliability` A/B/C/D. Toda perturbación generada debe ser evaluable; si
una falla, Q4 falla cerrado. Se conserva el antiguo
`time_sensitivity_summary` únicamente como fallback legacy explícito.

Q4 no recalcula IDD: la estabilidad de IDD es un componente separado de Q5,
evitando doble contabilización. Tampoco utiliza ICE, IEM_final, temporalidad ni
rareza de modelos nulos.

## Próximas fases

Q5: cuantificación canónica de ablación, perturbación paramétrica e IDD stability
para M25.

Q6: generadores de universos nulos para M24, manteniendo rareza estructural
separada de IRC y de cualquier probabilidad metafísica.

Q7: actualización del gate FULL, fixtures y release pública 1.13.0.
