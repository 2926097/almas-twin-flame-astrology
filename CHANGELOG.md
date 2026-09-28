# Changelog

## 1.20.0 — 2026-09-28

### Síntesis root-first y temporalidad TTRANSIT
- Formaliza un protocolo de síntesis interpretativa que comienza por raíces y motivos semánticos, evitando inventarios planos de técnicas o aspectos.
- Amplía la hermenéutica source-based de compuesta/Davison, declinaciones, antiscios, sinastría, casas, funciones planetarias, geometría de aspectos, extremos angulares/nodales, sustrato natal y campo relacional.
- Hace disponibles para autoría el contexto dracónico, contactos planeta–ángulo, Fortuna/Espíritu y puntos secundarios como Juno/Eros cuando el canonical los contiene.
- Profundiza motivos de continuidad kármica, transformación transpersonal, Quirón/WOUND_REPAIR, polaridad erótica/espejo y coherencia/afinidad sin convertirlos en etiquetas ontológicas automáticas.
- Añade hermenéutica temporal M26–M27 y conserva `trigger_context` como superficie de autoría sin alterar IAT.
- Registra fuentes y contrato de método para `TTRANSIT` y añade un generador autónomo de tránsitos contra endpoints natales de raíces M17 usando `aspect_policy` explícita.
- Añade `temporal-reading.synthetic.json`, que demuestra una lectura Saturno cuadratura Venus integrada en una raíz Venus–Plutón y conserva el límite de no predicción factual.
- La suite del núcleo alcanza **537 tests** en Python 3.10 y 3.12; `Núcleo Python`, `Contrato público`, `Backend astronómico`, `Publicación DOCX` y `Publicación PDF` terminan en PASS en la PR de cierre.
- No añade nuevos scores, pesos, thresholds, discriminadores activados ni afirmaciones de validación científica de ontologías metafísicas.

## 1.19.0 — 2026-09-27

### Autoría interpretativa y publicación B5
- Reorienta la fase 1.19 hacia la lectura astrológica y la hermenéutica/metafísica basada en fuentes; la infraestructura técnica queda como soporte de cálculo, trazabilidad y control de calidad.
- M31 expone `evidence`, `semantic_motifs` y `doctrine` a S01/S10 para que la síntesis no quede reducida a índices.
- Activa `authored_report` en `SKILL.md` como paso obligatorio después de M31 cuando se solicita una lectura o informe, priorizando significado astrológico/hermenéutico sobre exposición metodológica.
- Añade `ALMAS_AUTHORED_REPORT` con once secciones, fingerprint canónico, referencias de evidencia/claims/fuentes y bibliografía editorial.
- Añade un fixture interpretativo sintético completo que integra astrología, doctrina comparada y contraevidencia sin representar personas reales.
- Añade `ALMAS_B5_BOOK_V1` para DOCX ISO B5 176×250 mm mediante `python-docx==1.2.0`.
- Añade `ALMAS_B5_PDF_V1` con conversión LibreOffice y preflight fail-closed mediante `pypdf==6.19.0`.
- El preflight PDF comprueba B5/CropBox, cifrado, páginas vacías, texto, fingerprint, once títulos y fuentes embebidas.
- QA visual: 13/13 páginas del fixture renderizadas e inspeccionadas sin cortes, solapamientos ni desbordes.
- La suite del núcleo alcanza **498 tests** en Python 3.10 y 3.12; los workflows de contrato público, backend astronómico, publicación DOCX y publicación PDF terminan en PASS.
- No añade técnicas, pesos, thresholds, scores, discriminadores ni validación científica de ontologías metafísicas.

## 1.18.0 — 2026-09-27

### Backend astronómico de producción
- Añade `ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1` y el adaptador opcional `ALMAS_MOIRA_JPL_SPK_V1`.
- Fija `moira-astro==6.8.2` como extra `astronomy-moira`; el núcleo ALMAS no adquiere una dependencia astronómica obligatoria.
- Exige kernel JPL BSP local, familia DE430/DE440/DE441 y SHA-256 verificado antes de cálculo.
- Prohíbe descargas de efemérides y geocodificación implícita durante el cálculo.
- Añade timezone IANA fail-closed para horas ambiguas/inexistentes y exige coordenadas numéricas.
- Normaliza True Node como `NORTH_NODE` y deriva `SOUTH_NODE`; produce declinaciones, casas y ASC/DSC/MC/IC.
- Bloquea cualquier fallback polar o cambio efectivo del sistema de casas.
- Implementa Davison mediante midpoint UTC y midpoint geográfico esférico explícitos.
- M02 y M08 pasan de `BACKEND_REQUIRED` a `EXECUTABLE_HANDLER`.
- Añade schema de procedencia astronómica y workflow específico de compatibilidad Moira en Python 3.10/3.12.
- La suite del núcleo alcanza **483 tests deterministas**; el workflow específico valida Moira 6.8.2, Skyfield 1.55 y los contratos del gate en Python 3.10/3.12.
- Preregistra `ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1` con seis casos sintéticos, tolerancias inmutables y etapas planetas/nodo/casas.
- Ejecuta con el DE440s oficial fingerprintado las etapas `PLANETARY_REFERENCE`, `TRUE_NODE_REFERENCE`, `HOUSE_REFERENCE` y `COMPLETE_GATE`; todas obtienen PASS en los seis casos y en Python 3.10/3.12.
- El `COMPLETE_GATE` valida 47 medidas por caso y 282 por entorno con cero fallos; el máximo global es 39,8903887122″ en ASC/H1 de `G06_CAPE_TOWN_2050`, por debajo del límite preregistrado de 60″, sin modificar thresholds tras observar resultados.
- Endurece `canonical-analysis.schema.json`: raíz cerrada, superficie M30 completa, composición de schemas especializados y trazabilidad obligatoria del backend astronómico.
- Añade `semantic-motif-graph.schema.json`, la auditoría namespace→productor→schema y validación Draft 2020-12 con `jsonschema==4.26.0`.
- Valida tanto una salida M30 sintética como la ejecución FULL M00–M31 y añade pruebas negativas de namespace/campo/procedencia inválidos.
- Corrige Q6 para conservar `PX_PILLAR_SCORE` en la escala canónica 0–100; elimina la doble multiplicación por 100 detectada al validar el pipeline completo.
- No cambia técnicas, pesos, scoring, ontología ni discriminadores.

## 1.17.0 — 2026-09-27

### Manifiestos normativos estructurales
- Añade `ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1` y elimina de M15 la tabla hardcodeada de fuente→familia técnica/dependencia/elegibilidad, conservando exactamente la taxonomía 1.16.
- Añade `ALMAS_DECLARED_ORB_CONTRACT_V1` y `schemas/aspect-policy.schema.json`: cada aspecto debe declarar `angle` y `orb`; no existen orbes implícitos ni inferencia runtime.
- Añade `ALMAS_STRUCTURAL_LOADING_CONTRACT_V1`, que enlaza root strength, root→pillar y recurrencia semántica sin introducir una segunda capa de pesos.
- Añade `ALMAS_STRUCTURAL_POLICY_MANIFEST_V1` como punto público único de descubrimiento para técnica, dependencia, orbes, elegibilidad y loading.
- M15 expone `technique_dependency_registry_id` como procedencia normativa.
- Mantiene todos los pesos de técnica/aspecto en 1.0, la robustez horaria en M23–M25 y `support_only` fuera de la creación de núcleo.
- No añade módulos analíticos, técnicas, scores, discriminadores ni ontología.
- La suite de release alcanza **443 tests deterministas** en Python 3.10 y 3.12.

## 1.16.0 — 2026-09-27

### Validation Operations V1–V5
- Añade `ALMAS_VALIDATION_PREREGISTRATION_BUNDLE_V1` para congelar candidato, fórmula, versión/commit, cohorte, cegamiento, leakage, replicación, controles, ablaciones, endpoints y criterios antes de abrir el holdout.
- Añade `ALMAS_HOLDOUT_OPEN_GATE_V1`, que verifica el preregistro y permite iniciar una evaluación sin promover ni activar el candidato.
- Añade `ALMAS_VALIDATION_EXECUTION_LEDGER_V1`, una cadena append-only SHA-256 con los eventos PREREGISTERED → HOLDOUT_OPENED → HOLDOUT_EVALUATED → DOCUMENTARY_REVEALED → VALIDATION_CLOSED.
- Añade `ALMAS_VALIDATION_CONTINUITY_GATE_V1`, que certifica continuidad criptográfica V1→V2→S7→V3 antes de permitir presentar evidencia a S8.
- Añade `ALMAS_VALIDATION_CLOSURE_RELEASE_AUDIT_V1`: revelado documental tardío con invariancia estructural, cierre confirmatorio y paquete agregado de auditoría de release.
- Un ciclo S8 elegible sólo puede cerrar como `PROMOTION_ELIGIBLE_AWAITING_VERSIONED_ACTIVATION`; la activación en la misma release permanece prohibida.
- Mantiene `automatic_registry_mutation=false`, scoring/weighting/ontology/L3 deshabilitados y `metaphysical_probability=false` en V1–V5.
- Mantiene vacío el registro canónico PX v3 y no declara holdout externo real ejecutado ni discriminador L3 real validado.
- La suite de release alcanza **434 tests deterministas** en Python 3.10 y 3.12.

## 1.15.0 — 2026-09-27

### Calibración de especificidad y ciclo PX v3 no operativo
- Añade `ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1`: diversidad de familias/clases, entropía, dominancia, dependencia dracónica y supervivencia leave-one-out por motivo.
- Añade `ALMAS_RECURRENCE_NULL_CALIBRATION_V1`: calibra motivos y agregados PX/PS contra `WITHIN_YEAR` con frecuencias incondicionales/condicionales e intervalos de Wilson.
- Añade `ALMAS_RECURRENCE_SYNTHETIC_CONTROLS_V1`: controles deterministas por rotación semántica y desacoplamiento punto-relación, sin RNG ni interpretación poblacional.
- Añade `ALMAS_EXTERNAL_RECURRENCE_COHORT_V1`: firewall privado para cohortes `PAIR_SHUFFLE`, `MATCHED_AGE` y `MATCHED_AGE_CLOCK`, con preregistro, contaminación/leakage y salida pública agregada.
- Añade `ALMAS_EXTERNAL_RECURRENCE_CALIBRATION_V1`: reutiliza el núcleo matemático de S2 sobre holdouts externos limpios y preregistrados.
- Añade `ALMAS_PX_V3_CANDIDATE_FREEZE_V1` y el registro `ALMAS_PX_V3_CANDIDATES`, que permanece vacío; ninguna fórmula PX v3 real se incorpora a esta release.
- Añade `ALMAS_PX_V3_HOLDOUT_EVALUATION_V1`: runner holdout agregado con fingerprint SHA-256 y prohibición de promoción durante la evaluación.
- Añade `ALMAS_PX_V3_PROMOTION_GATE_V1`: exige holdout, calibración externa, replicación independiente, controles negativos, ablación, auditoría de leakage y criterios preregistrados; `PROMOTION_ELIGIBLE` no activa scoring.
- Añade `ALMAS_PX_V3_ACTIVATION_FIREWALL_V1`: bloquea cualquier activación PX v3 dentro de la línea 1.15 y exige nueva versión, auditoría y contrato público para una futura activación.
- Refuerza el contrato público con schemas, políticas y tests S1–S9.
- Mantiene PX v2 (`ALMAS_SEMANTIC_MOTIF_V2`) como único score operativo; PX, PS, IEM, IDD, IRC y ontología de producción no cambian por S1–S9.
- Mantiene `validated_discriminator_ids=[]`, `PX v3 records=[]` y `metaphysical_probability=false`.
- La suite de release alcanza **394 tests deterministas**.
- No se declara holdout externo real ejecutado, validación L3 ni validación científica de las ontologías metafísicas.

## 1.14.0 — 2026-09-26

### Recurrencia semántica, perfiles de análisis y sensibilidad horaria v2
- Introduce `ALMAS_SEMANTIC_MOTIF_V2`: mantiene `root_key` como identidad geométrica y añade `motif_id` como identidad semántica para detectar recurrencia multitécnica sin fusionar raíces distintas.
- Redefine PX mediante motivos recurrentes presentes en al menos dos familias de dependencia independientes; cada familia cuenta una sola vez, `RELCHART` sigue siendo una única familia y las capas `support_only` no crean recurrencia core.
- Redefine PS como recurrencia de motivos de misión sobre eje meridiano + Sol/Júpiter/Saturno/nodos, sin convertir la firma en prueba de misión compartida factual.
- Eleva M18 a `ALMAS_ROOT_PILLAR_ATTRIBUTION_V2` y M21 a `ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V2`; Shapley puede operar sobre raíces y features de motivo derivadas sin declarar estas últimas raíces independientes.
- Introduce `ALMAS_ANALYSIS_PROFILES_V1`: `FULL_MULTIDISCIPLINARY`, `FULL_ASTROLOGY`, `TEMPORAL` y `SOUL_CONTRACT`. M30 distingue módulos requeridos, opcionales y excluidos; `READY` significa completitud técnica del perfil, no demostración metafísica.
- Eleva el ensamblaje a `ALMAS_CANONICAL_ASSEMBLY_V2` y propaga `analysis_profile` hasta M31.
- Eleva la sensibilidad horaria a `ALMAS_BIRTH_TIME_SENSITIVITY_V2`: publica curva diagnóstica R5/R15/R30/R60/R120 aunque no exista rating horario documentado y sólo crea BIRTH_TIME cuando la fiabilidad exigida está disponible.
- Añade `ALMAS_HELLENISTIC_LOTS_V1` para M13: baseline histórica de Fortuna y Espíritu con inversión por secta; no añade Eros/Necesidad por defecto ni convierte lotes en discriminadores ontológicos.
- Q5 recalcula PX/PS después de cada ablación en vez de reutilizar la recurrencia del baseline.
- Amplía el registro documental a 40 fuentes y 97 conceptos, incorporando procedencia explícita para Fortuna/Espíritu, secta y Daimon sin equiparar estos términos con ontologías modernas.
- Mantiene rareza nula fuera de IRC, temporalidad fuera de la creación de raíces, PU en `NOT_EVALUABLE` sin L3 y `validated_discriminator_ids=[]`.
- La suite alcanza **327 tests deterministas**. No se declara validación empírica externa de las ontologías metafísicas.

## 1.13.0 — 2026-09-26

### Cierre cuantitativo reproducible del modo FULL
- Cierra M17 con `ALMAS_ROOT_STRENGTH_BASELINE_V1`: fuerza de raíces derivada automáticamente desde exactitud geométrica, sin pesos retrospectivos ajustados al caso.
- Cierra M18 con `ALMAS_ROOT_PILLAR_ATTRIBUTION_V1`: atribución raíz→pilar determinista, un único pilar semántico primario y PX como recurrencia ortogonal; PU permanece `NOT_EVALUABLE` sin discriminador validado.
- Cierra M21 con `ALMAS_MODEL_ATTRIBUTION_SHAPLEY_V1`: atribuciones Shapley sobre `IEM_pre` e IDD AF/KA/AG/LG sin mapas manuales.
- Automatiza M23 mediante `ALMAS_BIRTH_TIME_PERTURBATION_V1`: parrillas horarias preregistradas, `delta90`, preservación de raíces core y componente BIRTH_TIME.
- Automatiza M25 mediante `ALMAS_ROBUSTNESS_Q5_V1`: ABLATION, PARAMETER_PERTURBATION e IDD_STABILITY derivados sin doble contabilización.
- Automatiza M24 mediante `ALMAS_NULL_WITHIN_YEAR_V1`: universo nulo determinista autocontenido, frecuencias estructurales e intervalos de Wilson, sin convertir rareza en probabilidad metafísica.
- Añade `ALMAS_CANONICAL_ASSEMBLY_V1`: ensamblaje de `canonical_analysis` desde M01–M29, ICC de siete dominios y cierre automático del gate M30 cuando la ejecución es íntegra.
- Migra la prueba FULL M00–M31 para retirar los shims cuantitativos de Q1–Q7; el pipeline deriva fuerza, pilares, IDD, sensibilidad horaria, nulls, robustez, ICC/IRC/R_min y canonical sin introducirlos manualmente.
- Mantiene compatibilidad con entradas precomputadas/legacy cuando la ruta automática no es aplicable o cuando se necesita una cohorte nula externa.
- Mantiene sin cambios los thresholds públicos de `SUPPORTED`, la separación ontológica M21, los gates L3 y la regla de que rareza/temporalidad no son probabilidad metafísica.
- No incorpora ningún `VALIDATED_DISCRIMINATOR` real ni declara validación externa de ontologías metafísicas.

## 1.12.0 — 2026-09-26

### Discriminación ontológica, validación y cierre metodológico
- Formaliza identificabilidad, equivalencia observacional y el fallback obligatorio `SHARED_ORIGIN_UNDIFFERENTIATED / INSUFFICIENT`.
- Añade registro doctrinal L1, candidatos operacionales L2 y motor lógico autónomo de discriminación ontológica.
- Integra la subcapa ontológica en M21 sin sustituir ni contaminar IDD AF/KA/AG/LG.
- Integra `ontological_discrimination` en el contrato canónico y preserva `promotion_trace` hasta M31.
- Endurece M25: sólo raíces L3 previamente validadas y confirmadas por M21 pueden entrar como `VALIDATED_DISCRIMINATOR`.
- Añade registro canónico de promoción, máquina de estados y prohibición de autopromoción L2→L3.
- Añade baterías adversariales y metamórficas contra falsa especificidad, duplicación de raíces, ciclos de exclusión, leakage y abuso de `promotion_ref`.
- Añade política de independencia astrológica: ningún aspecto, asteroide, atacir, rareza nula o activación temporal aislada autoriza L3.
- Añade `ALMAS_DISCRIMINANT_VALIDATION_V1` con sensibilidad/especificidad por par, balanced accuracy, Wilson 95 % y `FALSE_SPECIFICITY_RATE`.
- Añade `ALMAS_BLINDING_LEAKAGE_V1` con ejecución estructural ciega, revelado tardío y fingerprints pre/post.
- Añade reporting metodológico de promoción separado de la clasificación de caso y de IRC.
- Añade genealogía documental OD01–OD07 con techos epistemológicos y equivalencias doctrinales prohibidas.
- Añade `ALMAS_PUBLIC_DATA_ISOLATION_V1`, manifests exhaustivos para ejemplos/casos públicos/holdouts y firewall CI de privacidad.
- La suite Python alcanza **266 tests deterministas** en esta release.
- Estados actuales: OD01–OD04 `EXPLORATORY`, OD05–OD06 `BLOCKED`, OD07 `RETIRED`; `validated_discriminator_ids=[]`.
- No se ha ejecutado un holdout externo real y no se declara ningún `VALIDATED_DISCRIMINATOR` real.
- Mantiene sin cambios fórmulas, pesos y thresholds públicos de IEM/IDD/IRC/IAT/ICC/ICE y el gate `SUPPORTED`.

## 1.11.0 — 2026-09-25

### Pipeline modular ejecutable M00–M31
- Añade contrato común de módulos, estados de ejecución y orquestador secuencial con propiedad de namespaces canónicos.
- Implementa M01 y M03–M31 como handlers ejecutables; M02 natal y M08 Davison quedan como fronteras `BACKEND_REQUIRED` con backend inyectable.
- Añade geometría reproducible para sinastría, casas, declinaciones, antiscios, compuesta, RELCHART, dracónicas, lotes y capa simbólica secundaria.
- Convierte contactos en grafo de evidencia, deduplicación por dependencia y raíces independientes sin inventar pesos no preregistrados.
- Añade contraevidencia explícita, ablación AB0–AB8, sensibilidad horaria, modelos nulos/Wilson y agregación de robustez.
- Añade activación temporal anclada, ledger documental append-only y separación estricta entre estructura, temporalidad y hechos.
- Añade firewalls ejecutables para doctrina A–E, viabilidad/reciprocidad factual y reporting derivado sólo de `canonical_analysis`.
- Añade una prueba sintética FULL que ejecuta M00–M31 de extremo a extremo.
- M30 distingue `READY`, `PARTIAL` y `BLOCKED`, calcula fingerprint canónico y bloquea divergencias raw/snapshot.
- M31 cierra el pipeline analítico con un `report_document_model` de 11 secciones, sin incrustar valores ni renderizar documentos.
- La suite Python alcanza 133 tests deterministas en esta release.
- Mantiene sin cambios las fórmulas públicas IEM/IDD/IRC, los thresholds, la ontología y los discriminadores existentes.
- No convierte rareza, intensidad, temporalidad, doctrina ni capas `support_only` en probabilidad o prueba metafísica.

## 1.10.1 — 2026-09-25

### Depuración integral del repositorio
- Repara el validador público: elimina checks contradictorios 1.8.0/1.9.0 y 1.0.0/1.1.0.
- Sustituye versiones internas duplicadas por comprobaciones schema↔fixture dinámicas.
- Elimina la referencia obsoleta a `soul_contract_version`/`soul_version`.
- Sincroniza `preincarnation-pipeline-manifest.json` con el schema 1.9.0.
- Renombra `manifests/module-manifest.json` a `manifests/analysis-pipeline-manifest.json` para distinguir pipeline M00–M31 de arquitectura modular.
- Archiva la antigua arquitectura dual en `docs/history/`.
- Archiva los checksums del paquete base v1.0.0 y los retira de la raíz.
- Elimina el snapshot obsoleto `reference/source-normalization-report.json`; el audit canónico es `reference/source-normalization-audit.json`.
- Archiva el plan de integración documental ya completado y convierte los huecos en `docs/SOURCE_RESEARCH_BACKLOG.md`.
- Depura README, arquitectura, estado de validación y normalización de fuentes.
- No modifica fórmulas, pesos, ontología, thresholds ni discriminadores.

## 1.10.0 — 2026-09-25

### Cláusulas contractuales C4–C8
- Eleva `clause-assembly.schema.json` a 1.1.0.
- Eleva `preincarnation-reconstruction.schema.json` a 1.9.0.
- Toda cláusula separa contenido reconstruido, mecanismo de activación, prueba contractual, integración y cumplimiento.
- Añade `resolution_level`, `claim_refs`, `allowed_conclusion` e `inferential_ceiling` a las cláusulas.
- El techo por defecto de una cláusula astrológicamente reconstruida es R2_RELATIONAL_PREINCARNATIONAL_FUNCTION.
- R3 exige discriminador independiente validado; R4 no puede alcanzar SUPPORTED desde astrología.
- Actualiza fixtures sintéticos, registro de cláusulas, documentación e invariantes.
- La mejora procede de una necesidad detectada en un caso privado, pero se publica sólo como regla general y test sintético.

## 1.9.4 — 2026-09-25

### Claim contract v2
- Eleva `schemas/doctrinal-claim.schema.json` a 2.0.0.
- Toda afirmación relevante transporta clase A–E, alcance, fuentes, anclas, techo inferencial, estado del discriminador y conclusión permitida.
- La narrativa debe publicar `allowed_conclusion`, no un `requested_conclusion` que exceda el techo.
- Añade ejemplos sintéticos para doctrina explícita, contrato R2 y técnica dracónica.
- Integra el claim contract v2 en el gate doctrinal y en CI.
- Refuerza la separación entre técnica verificada y ontología no validada.

## 1.9.3 — 2026-09-25

### Anclas documentales y dracónica
- Añade `verification_anchor`, tipo de ancla y alcance de evidencia a las fuentes usadas por los mapeos doctrina→astrología.
- Los 23 documentos que sustentan los 15 mapeos disponen ahora de ancla explícita.
- Formaliza la política EXACT_PASSAGE / SECTION / CHAPTER / ABSTRACT / AUTHOR_SUMMARY / PUBLISHER_SUMMARY / TABLE_OF_CONTENTS / METADATA_ONLY.
- Añade a María Blaquier como fuente técnica verificable del cálculo dracónico y separa fórmula técnica de interpretación metafísica.
- Registra obligatoriamente la elección Mean/True Node en el uso dracónico.
- Eleva el corpus a 38 fuentes: 23 P1, 7 P2, 1 P3 y 7 P4.
- Añade CI para impedir que un mapeo use una fuente sin ancla documental.
- Mantiene la dracónica como reencuadre nodal corroborativo; verificar el cálculo no valida contratos, vidas pasadas u origen álmico.
- Añade `docs/SOURCE_ANCHOR_POLICY.md` y `docs/MAPPED_SOURCE_ANCHOR_REPORT.md`.

## 1.9.2 — 2026-09-25

### Auditoría doctrina → astrología
- Añade casos sintéticos negativos que deben impedir sobreinferencia aunque los indicadores sean extremos.
- Audita los 15 conceptos que sí tienen traducción astrológica.
- Añade `source_alignment`, `validation_state`, `inferential_ceiling`, `structural_score_policy`, dependencias, gates, poder discriminante y upgrades prohibidos.
- Establece que score, rareza, recurrencia o número de técnicas nunca pueden superar el techo inferencial.
- Vincula techos críticos a discriminadores explícitos: contrato R2→R3, soul-root→zivug, zivug→twin-flame, split-soul→twin-flame y monadic→related-root.
- Mantiene DRACONIC_ASTROLOGY como técnica corroborativa dependiente de nodos.
- Mantiene LIFE_BETWEEN_LIVES y SOULMATE_EXPERIENCE sin contribución estructural directa.
- Añade cobertura doctrina→astrología para los 92 conceptos y CI que impide crear evidencia desde conceptos contextuales o de límite.
- Añade `docs/DOCTRINE_ASTROLOGY_MAPPING_AUDIT.md`.

## 1.9.1 — 2026-09-25

### Corpus doctrinal y CI
- Cobertura doctrina→astrología explícita para los 92 conceptos: 15 mapeados, 35 no operacionalizados, 29 límites, 9 contexto y 4 técnicas-contexto.
- Cierra la cobertura concepto↔fuente: 37 fuentes, 92 conceptos y 73 relaciones doctrinales.
- Elimina el último estado PARTIAL al verificar Brihadaranyaka Upanishad 1.4.3 con la edición pública de Max Müller.
- Añade 20 conceptos que ya eran usados por el corpus pero aún no estaban formalmente definidos.
- Alinea los schemas de clases conceptuales y relaciones genealógicas con los registros reales.
- Añade no-equivalencias y solapamientos para relaciones planificadas, retorno por otros, teacher–student roots, separación/reunión y otros conceptos.
- Añade auditoría canónica de normalización y comprobaciones CI de integridad fuente↔concepto↔genealogía.
- Repara la divergencia del validador respecto de la versión pública y sincroniza los metadatos a 1.9.1.

## 1.8.4 — 2026-09-24

### Fase 12 · Hechos y biografía documental — completada
- Añade ledger documental separado de la arquitectura simbólica.
- Impone análisis estructural congelado antes de incorporar acontecimientos.
- Separa hecho verificable de interpretación.
- Define calidad documental DQ1–DQ5.
- Permite que los hechos corroboren activación, cumplimiento, contraevidencia, viabilidad o reciprocidad, pero no creen raíces/cláusulas retrospectivamente.
- Añade privacidad, correcciones trazables, esquema, fixture sintético y tests.

## 1.8.3 — 2026-09-24

### Fase 11 · Temporalidad contractual — completada
- Separa estructura, activación, recurrencia e integración/cierre.
- Añade estados LATENT, TRIGGERED, ACTIVE, RECURRING, INTEGRATING, EMBODIED, TRANSFORMED y CLOSED.
- Clasifica ventanas como retrospectivas, actuales, prospectivas, exploratorias o no ancladas.
- Prohíbe convertir fechas futuras en reunión, decisión, contacto o cierre.
- Mantiene IAT separado de IAP.

## 1.8.2 — 2026-09-24

### Fase 10 · Libre albedrío — completada
- Separa estructura previa, elección encarnada, forma relacional y rutas alternativas.
- Añade niveles FD0–FD4 de determinación.
- Exige elección y hechos bilaterales para toda forma compartida.
- Permite cumplimiento individual cuando la función de la cláusula lo admite.
- Impide inferir eventos fijos o decisiones futuras desde astrología.

## 1.8.1 — 2026-09-24

### Fase 9 · Métricas contractuales — completada
- Descompone IAP en ITP, IAA, IRCo, ICCo, IVC, IRCT, ICE-C e ICC-C.
- Define IAP como índice de arquitectura preencarnatoria funcional, no como probabilidad.
- Separa reciprocidad contractual astrológica de reciprocidad interpersonal real.
- Impide que IAP alto eleve por sí solo R3 acuerdo bilateral literal.
- Añade fórmulas, gates, esquema y tests.

## 1.8.0 — 2026-09-24

### Fase 8 · Ablación y dependencia contractual — completada
- Añade batería AB0–AB8 para retirar asteroides, temporalidad, dracónica, cartas relacionales, casas/ángulos, nodos y capas auxiliares.
- Añade AB8_INDIVIDUAL_ONLY para demostrar que las tareas previas existen antes de introducir a la pareja.
- Clasifica dependencia como CORE_STABLE, MULTILAYER_STABLE, DRACONIC_SENSITIVE/DEPENDENT, RELCHART_SENSITIVE/DEPENDENT, ANGULAR_SENSITIVE, SUPPORT_LAYER_DEPENDENT o TEMPORAL_ONLY.
- Exige que causas y cláusulas estructurales sobrevivan sin temporalidad y que cláusulas SUPPORTED sobrevivan sin asteroides.
- Añade esquema, fixture sintético, pipeline y tests.

## 1.7.1 — 2026-09-24

### Fase 6 · Causalidad preencarnatoria — completada
- Añade motor por gates G1–G8 y niveles causales C0–C3.
- Exige tarea previa con pareja retirada, activador específico, independencia, recurrencia, ablación y alternativa competidora.
- No cuantifica causalidad antes de validar los gates.

### Fase 7 · Discriminadores — completada
- Añade discriminación transversal funcional/epistémica.
- Separa contrato funcional de karma genérico y catálisis simple.
- Mantiene explícitamente NOT_VALIDATED los discriminadores ontológicos fuertes.
- Añade fallbacks reproducibles cuando varias ontologías sobreviven.

## 1.7.0 — 2026-09-24

### Fase 5 · Doctrina → astrología — completada
- Añade mapa formal `FUENTE → VARIABLE_METAFISICA → OPERACIONALIZACION_ASTROLOGICA`.
- Separa C_DOCTRINE de E_PROJECT_HYPOTHESIS en cada correspondencia.
- Define indicadores astrológicos admisibles e inferencias inadmisibles por concepto.
- Impide que Kardec, Luria, Prophet o Stokke se conviertan en fuentes de técnicas astrológicas que no enseñan.
- Mantiene la dracónica como B_TECNICA documentada por método identificado y no como prueba ontológica.
- Añade tests automáticos de integridad concepto↔fuente↔operacionalización.

## 1.6.0 — 2026-09-24

### Fase 3 · Separación origen/contrato/función
- Queda absorbida por la ontología multiaxial v2 de ALMAS 1.5.0.

### Fase 4 · Motor del contrato preencarnatorio — completada
- Añade cadena causal contractual C1–C8.
- Separa origen ontológico de contenido contractual.
- Introduce niveles R0–R4 de resolución contractual.
- Introduce granularidad THEME/FUNCTION/ROLE/CONDITION/EVENT/DETAIL.
- Impide elevar contenido literal pre-natal a SUPPORTED desde astrología.
- Añade esquema, fixture sintético, manifiesto y tests de regresión.

## 1.5.0 — 2026-09-24

### Fase 1 · Corpus de fuentes — cerrada
- Normaliza 36 fuentes con tradición, conceptos y estado de verificación.
- Registra 12 fuentes primarias verificadas en texto, 17 verificadas en metadatos, 3 parciales y 4 pendientes.
- Añade informe auditable de normalización y tests de integridad fuente↔concepto.

### Fase 2 · Ontología comparada — completada
- Separa ORIGIN, PREINCARNATION_CONTRACT, HISTORY_CONTINUITY, FUNCTION y PHENOMENOLOGY.
- Mantiene POLARITY, MODALITY, PHASE, REAL_VIABILITY y RECIPROCITY como ejes independientes.
- Añade reglas explícitas de no-implicación entre ejes.
- Vincula los modelos de origen con el registro doctrinal y de conceptos.
- Añade `reference/ontology-registry.json`, `schemas/ontology-output.schema.json` y tests específicos.

## 1.4.0 — 2026-09-24

### Fase 0 · Arquitectura congelada
- Consolida ALMAS como **una única skill pública modular**.
- Convierte el antiguo Soul Contract en módulo interno y conserva su 1.9.0 sólo como `engine_revision`.
- Establece `VERSION` como único SemVer público.
- Añade `manifests/almas-module-manifest.json` y `docs/MODULE_ARCHITECTURE.md`.
- Convierte `docs/history/DUAL_ENGINE_ARCHITECTURE.md` como nota histórica de compatibilidad.
- Añade invariantes CI para impedir que reaparezca la arquitectura dual.

### Fase 1 · Fuentes y genealogía — iniciada
- Formaliza `schemas/source-registry.schema.json`.
- Añade `reference/concept-registry.json`.
- Añade `reference/doctrinal-genealogy.json`.
- Añade `docs/history/SOURCE_INTEGRATION_PLAN_PHASE1.md` y el backlog vivo `docs/SOURCE_RESEARCH_BACKLOG.md`.
- El registro contiene 36 fuentes en el punto de partida de esta fase.
- Establece que una fuente define significado/procedencia/límites pero no añade puntuación astrológica por su mera existencia.
- Normaliza los lotes de planificación preencarnatoria, Cábala luriana, genealogía twin-flame, astrología esotérica/dracónica y fenomenología contemporánea.
- Añade **Gate doctrinal** para distinguir doctrina directa, descripción académica, antecedente histórico, analogía, uso contemporáneo y operacionalización ALMAS.
- Añade no-equivalencias críticas como zivug ≠ twin flame, soul-root ≠ Monad y experiencia emic ≠ ontología.

## 1.3.1 — 2026-09-24

- Soul Contract alcanza **v1.9.0** como subskill independiente, con motores reproducibles para las ocho etapas de reconstrucción preencarnatoria.

- Soul Contract avanza independientemente a **v1.2.0** con motor diferencial del origen de las almas, modelos doctrinales competidores y fallback `SHARED_ORIGIN_UNDIFFERENTIATED`.

- Soul Contract avanza independientemente a **v1.1.0** con reconstrucción preencarnatoria en ocho etapas y contrato JSON propio.

- Reafirma ALMAS como proyecto paraguas con dos skills interoperables: Astrología Metafísica Relacional y Contrato Álmico.
- Añade módulo de causa contractual y controles contra circularidad interpretativa.
- Amplía el registro doctrinal y académico con Kardec, Zohar, Talmud, Kwilecki, Stokke, Crane, Bailey y Prophet.
- Distingue antecedentes doctrinales, documentación académica y método astrológico contemporáneo.

## 1.3.0 — 2026-09-24

- Mantiene ALMAS como un único proyecto modular y separa funcionalmente dos skills interoperables: motor astrológico y motor de contrato álmico.
- Define la astrología como método metafísico de investigación dentro de ALMAS.
- Convierte los guardacarriles en controles metodológicos internos, no en negación del paradigma metafísico.
- Organiza la lógica contractual detallada en módulos internos y contratos JSON dentro de la misma skill.
- Añade un contrato JSON de intercambio entre ambos motores.
- Mantiene raíces, temporalidad, robustez y contraevidencia durante el traspaso.
- Permite casos reales públicos y verificables con procedencia; excluye material privado no publicado.


## 1.2.0 — 2026-09-24

- Añade arquitectura de roles preencarnatorios dentro del módulo de contrato álmico.
- Separa A_EN_B, B_EN_A y CAMPO_COMUN.
- Define roles funcionales: activador, catalizador, espejo, memoria, estructurador, liberador, confrontador, portador de vulnerabilidad, integrador, mediador, testigo y compañero de aprendizaje.
- Exige trazabilidad desde el radix receptor hasta la cláusula contractual.
- Añade intensidades PRIMARIO, SECUNDARIO, CORROBORATIVO, INSUFICIENTE y NO_EVALUABLE.
- Prohíbe convertir un rol simbólico en obligación, autoridad o permanencia.

## 1.1.1 — 2026-09-24

- Añade estado temporal independiente para cada cláusula contractual.
- Define LATENTE, ACTIVADA, EN_DESARROLLO, INTEGRADA, TRANSFORMADA, CERRADA y NO_EVALUABLE.
- Impide asignar integración o cierre únicamente desde técnicas astrológicas o fechas futuras.
- Exige hechos documentados y firmas preregistradas para integración, transformación y cierre.

## 1.1.0 — 2026-09-24

- Integra el contrato álmico como módulo transversal de la única Skill ALMAS.
- Añade ocho cláusulas contractuales: encuentro/reconocimiento, vínculo amoroso, herida/reparación, libertad/autonomía, comunicación/verdad, transformación/poder, integración/encarnación y liberación/cierre.
- Añade extracción direccional A_EN_B, B_EN_A y CAMPO_COMUN.
- Añade tres tiempos contractuales: activación inicial, desarrollo y cumplimiento/transformación/cierre.
- Añade esquema JSON de contrato álmico e invariantes de regresión.
- Establece terminología española como presentación pública principal.
- Mantiene los identificadores técnicos heredados sólo cuando son necesarios para compatibilidad.
- Reafirma la frontera de privacidad: ningún caso privado o identificable se publica.

## 1.0.0 — 2026-09-24

Primera release pública en GitHub.

- Define el modelo generalizado de compatibilidad estructural AF/KA/AG/LG.
- Define IEM, IDD/alias IDE, IRC, IAT, ICC e ICE.
- Define raíces con control de dependencia, pilares, contraevidencia, modelos nulos, ablación y robustez frente a hora natal.
- Define a nivel de especificación sinastría, declinaciones, antiscios, compuesta, Davison, dracónica y capas temporales.
- Define doctrina comparada, síntesis hermenéutica y ontología relacional multidimensional.
- Define el contrato análisis canónico → modelo de informe → publicación.
- Añade un núcleo Python sin dependencias externas para agregación de pilares, IEM, IDD e IRC.
- Añade API de pilares precomputados y la interfaz de línea de comandos `almas-score`.
- Añade schemas JSON formales de entrada/salida.
- Añade **14 tests unitarios deterministas** y CI con GitHub Actions.
- Añade manifiestos públicos de módulos/discriminadores y registro de procedencia de fuentes.
- Establece la frontera de publicación: reglas generalizadas y fixtures sintéticos por defecto; los casos reales sólo se permiten cuando sus datos subyacentes ya son públicos, independientemente verificables y citados. El material privado/no público queda excluido.
