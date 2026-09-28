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

## Fase Q5 · Robustez automática de ablación, parámetros e IDD

Q5 queda implementada mediante la política congelada
`ALMAS_ROBUSTNESS_Q5_V1` y el motor
`src/almas_tfa/robustness_quantification.py`.

Se derivan tres componentes automáticos adicionales para M25:

**ABLATION.** Se utilizan las corridas estructurales
`AB3_NO_DRACONIC`, `AB4_NO_RELCHART`, `AB5_NO_HOUSES_ANGLES`,
`AB6_NO_NODES` y `AB7_TROPICAL_PLANETARY_CORE`. Para cada corrida se
reconstruyen pilares e IEM_pre desde las raíces supervivientes. `AB1` y
`AB2` se excluyen porque asteroides secundarios y temporalidad ya están
impedidos por diseño para crear núcleo; `AB8_INDIVIDUAL_ONLY` se excluye
porque elimina deliberadamente la relación y no constituye una expectativa de
estabilidad del modelo relacional.

**PARAMETER_PERTURBATION.** Los orbes declarados se recalculan con factores
`0.90, 0.95, 1.05, 1.10`. Se perturban sin cambiar datos natales, etiquetas,
doctrina o hechos. Para cada corrida se calcula el máximo cambio absoluto de
IEM_pre y la preservación de raíces core.

**IDD_STABILITY.** Sobre esas mismas corridas paramétricas se vuelven a derivar
las atribuciones Shapley y los IDD por pares. Se mide el máximo cambio absoluto
de IDD y la fracción de corridas que conserva todas las bandas IDD evaluables
del baseline.

Los tres componentes usan:

`R_X = exp(-delta90/20) × sqrt(G)`

con percentil 90 `NEAREST_RANK`.

M25 prioriza el componente automático cuando existe y descarta el adaptador
legacy del mismo `kind`, impidiendo doble contabilización. BIRTH_TIME de Q4,
ABLATION, PARAMETER_PERTURBATION e IDD_STABILITY entran después en el IRC
mediante media geométrica. Los discriminadores ontológicos L3 permanecen
sometidos a su gate independiente y no se crean automáticamente.

Q5 continúa excluyendo rareza nula, temporalidad, ICE e IEM_final de la
derivación de robustez estructural.

## Fase Q6 · Generación automática de universo nulo estructural

Q6 queda implementada mediante la política congelada
`ALMAS_NULL_WITHIN_YEAR_V1` y el motor
`src/almas_tfa/null_generation.py`.

Cuando no se proporcionan `null_model_runs` externos, M24 genera de forma
determinista un universo nulo `WITHIN_YEAR`. Cada sujeto se perturba por
separado mientras el otro permanece fijo. Se conservan año natal, hora local,
zona horaria y localización; sólo se sustituye la fecha de nacimiento por 32
fechas estratificadas dentro del mismo año. Esto produce 64 muestras en una
pareja con dos sujetos.

No se usa RNG: el generador toma el centro de cada estrato del calendario,
excluye la fecha original y conserva una secuencia totalmente reproducible.

Se calculan tres estadísticas independientes:

- `CORE_ROOT_COUNT`;
- `MAX_IEM_PRE`;
- `PX_PILLAR_SCORE`.

Cada estadístico genera su propia frecuencia estructural y su intervalo de
Wilson. Se prohíbe combinarlos en un único p-value.

El null autocontenido no se presenta como población externa. Los modelos
`PAIR_SHUFFLE`, `MATCHED_AGE` y `MATCHED_AGE_CLOCK` requieren un pool
externo apropiado y continúan admitiéndose mediante el adaptador explícito
`null_model_runs`. `EVENT_DATE_SHIFT`, `EPHEMERIS_DATE` y
`TECHNIQUE_SPECIFIC_CYCLE` requieren políticas específicas y no se fabrican
desde una sola pareja.

Q6 fija explícitamente:

`metaphysical_probability = false`

`external_population_claim = false`

`combined_p_value_state = FORBIDDEN`

y M25 mantiene la rareza nula completamente fuera de IRC.

## Fase Q7 · Ensamblaje canónico y cierre FULL

Q7 queda implementada mediante la política congelada
`ALMAS_CANONICAL_ASSEMBLY_V1` y el motor
`src/almas_tfa/canonical_assembly.py`.

El cambio elimina el último shim principal del FULL: ya no es necesario
suministrar manualmente `canonical_analysis` cuando M01–M29 han producido los
namespaces canónicos requeridos.

El ensamblador no recalcula astrología, raíces ni pilares. Serializa los
resultados ya producidos, deriva la cobertura canónica ICC mediante siete
dominios y prepara el objeto que M30 valida y congela mediante fingerprint.

La cobertura utiliza exactamente siete dominios:

1. base natal;
2. sinastría/nodos;
3. ángulos/casas;
4. simetrías;
5. cartas relacionales;
6. dracónica;
7. lotes/capa simbólica secundaria.

Cada dominio recibe q = 1.0, 0.5 o 0.0 según completitud y:

`ICC = 100 × Σq / 7`.

El IDD global de presentación utiliza
`MIN_EVALUABLE_PAIRWISE_IDD`, conservando además todos los IDD por pares. La
elección es conservadora: no permite que una separación muy marcada entre dos
modelos oculte un par que continúe solapado.

Los estados AF/KA/AG/LG se ensamblan a partir de los pilares e ICE ya
disponibles. `SUPPORTED` sólo puede cerrarse cuando ICE es evaluable y se
cumple el gate público de IEM, CORE, ICC, IRC y R_min. Si ICE no es evaluable,
el modelo puede permanecer `COMPATIBLE` pero no elevarse artificialmente a
`SUPPORTED`.

M30 conserva compatibilidad: un `canonical_analysis` explícito sigue teniendo
prioridad y nunca se sobrescribe. Sólo cuando no existe se activa el
ensamblador Q7.

La prueba FULL sintética se ha migrado para retirar los shims cuantitativos
manuales de Q1–Q7: fuerza de raíces, pilares, atribuciones IDD, sensibilidad
horaria, universos nulos, componentes de robustez, ICC/IRC/R_min y
`canonical_analysis` se derivan ahora por el pipeline.

## Estado de cierre

Q1–Q7 forman el cierre cuantitativo de ALMAS 1.13.0. Antes de fusionar la
release deben sincronizarse los metadatos SemVer, ejecutar la auditoría final y
obtener SUCCESS en `Núcleo Python` y `Contrato público` sobre el mismo HEAD.
