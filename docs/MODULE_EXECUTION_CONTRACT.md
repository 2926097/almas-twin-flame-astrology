# Contrato común de ejecución modular ALMAS

## Objeto

Este documento define el contrato operativo común para convertir la arquitectura M00–M31 en módulos ejecutables sin alterar la regla de **una única skill pública modular**.

La existencia de una etapa en el manifiesto no equivale a que exista ya un motor Python completo. El registro `manifests/execution-registry.json` separa explícitamente especificación, lógica reutilizable e implementación ejecutable.

## Entrada común

Todo handler recibe un `ModuleContext` con:

- `module_id`;
- `module_name`;
- `mode`;
- `raw_input`;
- `canonical_snapshot`;
- `prior_results`.

El snapshot canónico debe tratarse como inmutable. El módulo devuelve cambios; no modifica el estado compartido directamente.

## Salida común

Todo handler devuelve `ModuleResult` con:

- `module_id`;
- `status`;
- `payload`;
- `canonical_updates`;
- `evidence_refs`;
- `limitations`;
- `diagnostics`.

Los estados de ejecución son:

- `COMPLETED`: el módulo se ejecutó y puede producir actualizaciones canónicas;
- `SKIPPED`: la etapa fue omitida por una regla explícita de ejecución;
- `NOT_APPLICABLE`: la etapa no corresponde al caso o modo;
- `NOT_EVALUABLE`: faltan datos, cálculo o implementación suficiente;
- `FAILED`: se produjo un error operativo.

Estos estados son **estados de ejecución** y no sustituyen los estados epistemológicos `SUPPORTED`, `COMPATIBLE`, `INSUFFICIENT`, `CONTRADICTED` y `NOT_EVALUABLE` utilizados en ontología y diagnóstico diferencial.

## Propiedad del estado canónico

Cada actualización canónica reclama un namespace de primer nivel. Una vez que un módulo lo ha escrito, otro módulo no puede sobrescribirlo silenciosamente.

Esta regla implementa el invariante:

> un módulo no recalcula ni sustituye de forma silenciosa valores canónicos producidos por otro.

Las transformaciones legítimas deben escribir un nuevo namespace derivado o introducirse mediante una regla explícita futura con genealogía de procedencia.

## Orquestador

`src/almas_tfa/orchestrator.py` valida que el manifiesto FULL contenga exactamente M00–M31 en orden.

El orquestador:

1. recorre la secuencia declarada;
2. construye un contexto inmutable para cada etapa;
3. ejecuta únicamente handlers registrados;
4. marca como `NOT_EVALUABLE` las etapas todavía sin implementación;
5. acumula resultados y estado canónico;
6. registra la propiedad de cada namespace;
7. bloquea sobrescrituras intermodulares;
8. puede detenerse ante el primer fallo cuando `stop_on_failure=True`.

Por diseño, el primer esqueleto no finge que las 32 etapas están implementadas.

## Relación con canonical_analysis.json

El orquestador es infraestructura de ejecución. No sustituye `schemas/canonical-analysis.schema.json`.

Cuando estén implementados los handlers suficientes, determinados módulos publicarán namespaces canónicos que podrán ensamblarse y validarse contra `canonical-analysis.schema.json`.

Hasta entonces debe distinguirse:

`orchestration run != canonical_analysis completo`.

## Política de implementación

La secuencia recomendada es:

`contrato común → orquestador → adaptadores de lógica existente → cálculo/evidencia → ontología → contrato → temporalidad → reporting`.

No se modifican en este paso fórmulas, pesos, umbrales, modelos ontológicos ni discriminadores.

## Adaptadores ejecutables iniciales

La primera integración conecta al pipeline lógica ya existente sin cambiar sus fórmulas:

- `M18` — pilares: acepta pilares precomputados o deriva el valor de un pilar desde intensidades de raíces mediante `pillar_score`;
- `M19` — índices estructurales: reutiliza `score_model` y `supported_gate`;
- `M21` — discriminación diferencial: reutiliza `diagnostic_discrimination` e `idd_band`;
- `M25` — robustez: reutiliza `robustness_index` sobre componentes preregistrados.

Estos adaptadores viven en `src/almas_tfa/handlers.py`. Las etapas restantes continúan explícitamente como no implementadas hasta disponer de un motor reproducible.

## Frontera de M02 · carta natal

`src/almas_tfa/astrology_backend.py` define un protocolo `AstrologyBackend` y una solicitud `NatalRequest`. `src/almas_tfa/astrology_handlers.py` aporta `make_m02_natal(backend)`.

Esta frontera permite probar y sustituir el motor astronómico sin acoplar el núcleo ALMAS a una dependencia concreta. Una carta sin hora conserva posiciones que el backend pueda calcular, pero el handler registra explícitamente que casas y ángulos no deben tratarse como fiables.

El registro de ejecución marca M02 como `BACKEND_REQUIRED`: la interfaz y el handler existen, pero todavía no se ha incorporado un backend astronómico de producción.

## M03 y M04 · geometría relacional y contexto natal

`M03` calcula sinastría geométrica únicamente cuando la entrada proporciona una `aspect_policy` con ángulo y orbe de cada aspecto. No existen orbes implícitos en el motor. La salida conserva distancia angular, orbe, límite y exactitud, pero no transforma por sí sola un contacto en evidencia ontológica.

`M04` deriva signos, identifica nodos por `point_type=NODE`, conserva ángulos, sitúa puntos en casas utilizando exclusivamente las doce cúspides suministradas por el backend y calcula regencias sólo cuando se declara una `rulership_policy`. De este modo no se impone por defecto una escuela tradicional, moderna o híbrida de regencias.

Los contratos de salida están en `schemas/synastry-output.schema.json` y `schemas/natal-context-output.schema.json`.

## M05 y M06 · declinaciones y simetrías

`M05` calcula paralelos mediante `|dec_A-dec_B|` y contra-paralelos mediante `|dec_A+dec_B|`. Requiere `declination_policy` con los orbes aplicables; no existe orbe implícito.

`M06` calcula el antiscio como `(180°-λ) mod 360°` y el contra-antiscio como el punto opuesto al antiscio. Requiere `antiscia_policy` con los orbes declarados. La salida registra geometría y exactitud; su conversión en evidencia pertenece a M15–M17.

## M07 y M08 · cartas relacionales

`M07` implementa una compuesta de puntos medios sobre los puntos compartidos de ambas cartas. Requiere `composite_policy.midpoint_mode=SHORTEST_ARC`. Una oposición exacta no se resuelve silenciosamente: `opposition_tie_break` puede quedar en `NOT_EVALUABLE` o declarar expresamente una de las dos soluciones.

`M08` dispone de contrato y handler inyectable mediante `DavisonBackend`, pero permanece `BACKEND_REQUIRED`. Para evitar geocodificación implícita exige hora, zona horaria y coordenadas numéricas de ambos sujetos, además de una `davison_policy` registrada.

## M10–M12 · capa dracónica

`M10` exige una `draconic_policy` que identifique el nodo norte mediante `node_id` y declare `transform=NORTH_NODE_TO_ZERO`. La transformación aplicada a cada longitud es `(λ-nodo_norte) mod 360°`. Ángulos y cúspides sólo se transforman cuando la política activa expresamente `include_angles` o `include_houses`.

`M11` calcula los cruces natal A↔dracónica B y natal B↔dracónica A utilizando una `draconic_aspect_policy` declarada. `M12` calcula dracónica↔dracónica y marca la salida `corroborative_only=true`, conforme a la regla de independencia de ALMAS.

## M13 · lotes helenísticos / partes arábigas

`M13` es un evaluador declarativo de fórmulas. Cada lote debe declarar `id`, `source_ref` y una fórmula o variantes `DAY/NIGHT`. Si existen variantes, `lot_policy.sect_by_subject` debe indicar el sect de cada sujeto. ALMAS no escoge fórmulas ni invierte términos de forma implícita.

La forma general soportada es `base + Σ(add) - Σ(subtract)`, normalizada a 0–360°. Los puntos pueden proceder de posiciones natales o ángulos canónicos.

## M14 · capa simbólica secundaria

`M14` sólo procesa `point_ids` expresamente declarados en `secondary_symbolic_policy`. La política debe contener `support_only=true`; cualquier intento de desactivarlo se rechaza. Los contactos se calculan con una política de aspectos propia y quedan etiquetados individualmente como `support_only`.

## M15–M17 · grafo de evidencia y raíces independientes

`M15` normaliza contactos de las capas ejecutables en un grafo de evidencia. No asigna todavía fuerza final: `strength_policy_applied=false`. Cada elemento conserva módulo de origen, familia técnica, familia de dependencia, condición `support_only`, elegibilidad para núcleo, exactitud y `root_key`.

`M16` deduplica dentro de la misma `dependency_family + root_key`, reteniendo de forma determinista la observación de mayor exactitud y conservando las suprimidas con su razón. Los pares ASC/DSC, MC/IC, NN/SN y Vertex/Anti-Vertex se normalizan como ejes para impedir inflar evidencia equivalente; en aspectos angulares, 0°/180° y 60°/120° se reducen por simetría del eje.

`M17` agrupa la evidencia deduplicada en raíces estructurales conservadoras. Separa `core_evidence_ids` de `support_evidence_ids` y deja `strength=null / NOT_CALCULATED` hasta que exista una política explícita para la fórmula `S = F × technique_reliability × birth_time_factor × aspect_coefficient`.

## M20 · contraevidencia

`M20` acepta sólo `EXPLICIT_CONTRADICTION` y `STRUCTURAL_INCOMPATIBILITY`. La ausencia de datos no puede entrar como contraevidencia. Las contradicciones se deduplican por `modelo + dependency_family + contradiction_key`.

El módulo no inventa una fórmula de ICE. Si la entrada contiene `ice_by_model`, se conserva con `ice_state=PRECOMPUTED`; en caso contrario queda `NOT_CALCULATED`. Esto mantiene compatibilidad con el núcleo histórico sin ocultar que M19 precede a M20 en el pipeline vigente.

## M22 · ablación estructural

`M22` ejecuta AB0–AB8 sobre la evidencia deduplicada y las raíces independientes. Registra evidencia y raíces supervivientes/perdidas y una fracción de supervivencia por corrida. `AB7_TROPICAL_PLANETARY_CORE` conserva únicamente sinastría tropical entre luminarias/planetas principales; `AB8_INDIVIDUAL_ONLY` conserva sólo evidencia intrapersonal si existiera.

La salida se marca `structural_only=true` y `dependency_classes_assigned=false`. Las clases contractuales CORE_STABLE, DRACONIC_DEPENDENT, RELCHART_SENSITIVE, etc., no se infieren automáticamente a partir de esta matriz hasta disponer de las unidades contractuales correspondientes.

## M23–M25 · sensibilidad, modelos nulos y robustez

`M23` consume un resumen de perturbación previamente calculado y preregistrado. `time_sensitivity_summary` debe declarar al menos `preregistration_ref`, `delta90` y `preserved_fraction=G`. Aplica exactamente:

`R_X = exp(-delta90/20) × sqrt(G)`.

M23 no genera perturbaciones, no estima `delta90` a partir de muestras y no improvisa una convención de percentil. El componente resultante pertenece a robustez y su agregación final corresponde a M25.

`M24` evalúa corridas nulas preregistradas. Cada corrida conserva `preregistration_ref`, tipo de modelo nulo, `feature_set_ref`, `orb_policy_ref`, `event_set_ref`, `generator_ref`, estadístico observado, regla de extremo y muestras nulas o `n/extreme_count`. Los tipos admitidos son `MATCHED_AGE`, `WITHIN_YEAR`, `MATCHED_AGE_CLOCK`, `EPHEMERIS_DATE`, `PAIR_SHUFFLE`, `EVENT_DATE_SHIFT` y `TECHNIQUE_SPECIFIC_CYCLE`.

M24 no genera el universo nulo: `sampling_generated_by_m24=false`. Su frecuencia describe rareza estructural bajo el modelo declarado y fija `metaphysical_probability=false`.

`M25` es el único agregador canónico de robustez. Incorpora automáticamente `BIRTH_TIME` desde M23 porque su derivación está definida. Otros componentes deben declarar `id`, `kind`, `value`, `source_module`, `preregistration_ref` y `derivation_ref`.

Tipos admitidos: `BIRTH_TIME`, `ABLATION`, `PARAMETER_PERTURBATION`, `IDD_STABILITY` y `VALIDATED_DISCRIMINATOR`.

La presencia de M22 no crea automáticamente un componente IRC: sin una regla preregistrada de conversión, M25 registra `ablation_state=AVAILABLE_NOT_QUANTIFIED`. M24 queda excluido del IRC mediante `null_model_rarity_used_as_robustness=false`.

La agregación normativa permanece:

`IRC = 100 × geometric_mean(applicable_R_i)`

`R_min = min(applicable_R_i)`.

La salida canónica está definida por `schemas/robustness-output.schema.json`.

## M26 y M27 · activación temporal y hechos documentales

`M26` exige señales con familia temporal, intensidad y estado de ventana. Sólo una señal que referencia un `root_id` existente puede quedar anclada. Los coeficientes normativos permanecen: 1.00 para repetición directa, 0.90 para activación de raíz relacional, 0.70 para endpoint y 0 para señal no anclada.

Cada señal conserva `structural_family`, `exactitude_orb` y `preregistered_window_rule`. Una señal sólo es `iat_eligible=true` cuando está anclada, preregistrada, posee trazabilidad completa, no es `EXPLORATORY/UNANCHORED` y su fuerza efectiva es mayor que cero.

Dentro de una misma raíz/familia temporal se conserva únicamente la señal de mayor `effective_strength = strength × K`. La recurrencia temporal se registra sólo cuando una misma raíz aparece en dos o más familias temporales independientes; repetir fechas del mismo ciclo no crea familias nuevas.

IAT puede calcularse únicamente si existe `iat_aggregation_policy` con `preregistration_ref`, `window_scope_ref`, pesos por familia, pesos por raíz y `formula=WEIGHTED_MEAN_EFFECTIVE_STRENGTH`. La operacionalización usada es:

`IAT = 100 × Σ(w_i × effective_strength_i) / Σ(w_i)`

con `w_i = family_weight × root_weight`.

Si la política no existe, IAT permanece `NOT_CALCULATED`. Si la política existe pero omite el peso de una señal elegible, la ejecución se rechaza en lugar de ignorarla silenciosamente.

M26 fija `structural_score_modified=false`, `structural_roots_created=false` y `real_world_event_prediction_made=false`. Una ventana futura sólo describe activación potencial de una raíz; no autoriza inferir contacto, mensaje, reconciliación, separación, decisión, consentimiento, reunión o cierre.

`M27` consume `documentary_event_ledger` con `analysis_freeze_ref` y aplica la secuencia `ESTRUCTURA_CONGELADA → EVENTO_DOCUMENTADO → FUNCIÓN_PROBATORIA`. Valida IDs únicos, sujetos, precisión temporal, calidad documental declarada, privacidad, referencias a raíces/cláusulas y correcciones append-only. Una corrección nunca borra el registro anterior: éste queda `SUPERSEDED` y conserva `superseded_by_event_id`.

La coherencia de `date_precision` se audita sin inventar fechas. DQ1 exige al menos una referencia documental y DQ3 al menos dos referencias para sostener la etiqueta declarada; si el respaldo mínimo no existe, la calidad original se conserva pero se registra una incidencia en `documentary_quality_issues`. La independencia de fuentes para DQ3 sólo se marca `DECLARED` cuando la entrada la declara expresamente; de otro modo permanece `NOT_VERIFIED`.

Los roles `ACTIVATION_CORROBORATION`, `FULFILLMENT_EVIDENCE` y `COUNTEREVIDENCE` disponen de trazabilidad de destino. Corroborar activación exige una raíz o cláusula resuelta; cumplimiento exige cláusula resuelta; contraevidencia exige destino resuelto o `counterevidence_effect`. Los demás roles pueden documentar viabilidad, reciprocidad, fenomenología o contexto sin crear estructura.

M27 audita también los `event_refs` procedentes de M26 y separa enlaces resueltos de referencias temporales sin evento documental. Sólo `PUBLIC_VERIFIABLE` y `SYNTHETIC` son exportables públicamente; `PRIVATE_AUTHORIZED` y `PRIVATE_RESTRICTED` permanecen restringidos.

El firewall documental queda fijado en `structural_mutation_allowed=false`, `clause_creation_allowed=false`, `origin_elevation_allowed=false` y `astrology_backfill_allowed=false`. Cada evento replica estos límites. `fact_statement` e `interpretations` permanecen separados.

`analysis_freeze_ref` es obligatorio y se conserva, pero la salida declara `analysis_freeze_reference_verified=false` mientras no exista un registro canónico ejecutable de congelación; M27 no simula esa verificación.

## M09 · consonancia de cartas relacionales

`M09` compara puntos homólogos entre compuesta y Davison únicamente bajo una `relationship_chart_consonance_policy` explícita. Toda observación pertenece a una única familia de dependencia `RELCHART`. El módulo no define una puntuación global de consonancia: `consonance_score=null` y `score_state=NOT_DEFINED` mientras no exista una regla preregistrada.

## M28–M31 · doctrina, realidad factual y publicación

`M28` vive en `src/almas_tfa/doctrine_handlers.py` y aplica el gate doctrinal/hermenéutico. Toda afirmación usa `schema_version=2.0.0`, una clase A–E y un `claim_scope` compatible. `DIRECT_DOCTRINE` sólo puede pertenecer a `C_DOCTRINE` y exige una fuente P1 doctrinal primaria verificada, ancla citada, `source_support_refs` hacia `supports[]` y `does_not_support_checked=true`. `ACADEMIC_DESCRIPTION` exige fuente P2 académica anclada y permanece descripción académica. `D_CONTEMPORARY_USAGE` documenta uso vivo sin promoverlo a ontología. `E_PROJECT_HYPOTHESIS` conserva alternativas y nunca puede presentarse como doctrina directa. Las comparaciones históricas/analógicas no autorizan identidad doctrinal. Cuando se solicita identidad entre conceptos debe declararse `identity_target_concept_id`; una relación genealógica de no equivalencia bloquea esa identidad. M28 fija `doctrine_adds_structural_score=false`, `source_count_used_as_structural_weight=false`, `contemporary_usage_promoted_to_ontology=false`, `project_hypothesis_promoted_to_doctrine=false` y `cross_tradition_identity_inferred=false`. Su salida canónica está definida por `schemas/doctrine-hermeneutics-output.schema.json`.

`M29` vive en `src/almas_tfa/reality_handlers.py` y valida `REAL_VIABILITY` y `RECIPROCITY` exclusivamente desde hechos M27. Toda evaluación declara `assessment_ref`, `as_of_date` y exactamente dos sujetos. Un estado de viabilidad distinto de `UNKNOWN` necesita `viability_basis`; una reciprocidad distinta de `NOT_EVALUABLE` necesita `reciprocity_basis`. Cada base declara `event_id`, `basis_kind`, `observation_type` y `subject_ids`. Sólo son decisivos eventos `ACTIVE`, con rol factual correcto, contratos documental/temporal válidos, separación hecho/interpretación y calidad DQ1/DQ2/DQ3. La base conjunta debe cubrir a ambos sujetos; la ausencia de evidencia de una parte nunca se transforma en asimetría. `DOCUMENTED_SEPARATION` exige un evento `SEPARATION` y `DOCUMENTED_NO_CONTACT` exige `NO_CONTACT`. M29 fija `factual_basis_only=true` y mantiene en `false` el uso de astrología/metafísica como hecho, la inferencia desde PHASE/fenomenología, el uso de ausencia como asimetría y cualquier inferencia de estados mentales, consentimiento, fidelidad o decisiones futuras. Los contratos están en `schemas/viability-reciprocity-assessment.schema.json` y `schemas/viability-reciprocity-output.schema.json`.

`M30` vive en `src/almas_tfa/report_gate_handlers.py` y es el firewall de integridad entre `canonical_analysis` y el informe. Distingue `READY`, `PARTIAL` y `BLOCKED`. Bloquea ausencia o incoherencia del canonical, conflicto entre raw/snapshot, schema o modo inválidos, modelos FULL ausentes, estados/IEM incompatibles, afirmaciones positivas sin evidencia y cualquier módulo previo `FAILED`. Degrada a `PARTIAL` los modos TARGETED/TEMPORAL, la ausencia de traza, módulos `NOT_EVALUABLE`/`SKIPPED` y carencias no críticas de ICC/IRC/indices. `NOT_APPLICABLE` no degrada por sí mismo. Todo canonical evaluado recibe `canonical_fingerprint` SHA-256 determinista. M30 fija `canonical_values_mutated=false` y no corrige ningún valor. Su salida canónica está definida por `schemas/report-gate-output.schema.json`.

`M31` vive en `src/almas_tfa/report_model_handlers.py` y cierra el pipeline analítico M00–M31. Sólo se ejecuta cuando M30 es `READY` o `PARTIAL` y exige el `canonical_fingerprint` del gate. Recalcula el SHA-256 del `canonical_analysis`; cualquier cambio posterior a M30 provoca rechazo. El `report_document_model` contiene exactamente once secciones ordenadas, sus rutas obligatorias/opcionales, disponibilidad y clases epistemológicas permitidas. Los estados de sección son `READY`, `PARTIAL` o `NOT_AVAILABLE`. M31 hereda `degradation_reasons` y exige disclosure cuando el gate es `PARTIAL`. No incrusta valores (`canonical_values_embedded=false`), no genera narrativa (`prose_generated=false`), no modifica el canonical, no selecciona perfil de renderizado y no crea DOCX/PDF ni ejecuta preflight. La publicación material comienza después de M31. Su salida canónica está definida por `schemas/report-document-model.schema.json`.

## Ejecución FULL sintética M00–M31

`configured_handlers(astrology_backend=..., davison_backend=...)` permite inyectar explícitamente los backends de M02 y M08 sobre el registro estándar. La prueba `tests/test_full_pipeline.py` ejecuta las 32 etapas en orden con entradas sintéticas declaradas y exige estado `COMPLETED` para M00–M31, además de verificar que el modelo documental no modifique la verdad canónica.
