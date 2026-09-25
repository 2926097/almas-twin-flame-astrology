# Changelog

## 1.10.2 — 2026-09-25

### Normalización lingüística y estructural
- Establece el español como idioma obligatorio de toda prosa destinada a lectura humana.
- Conserva en inglés únicamente identificadores técnicos, claves, rutas, nombres canónicos y términos cuya traducción rompería compatibilidad.
- Traduce la especificación principal, CLI, métricas, procedencia, políticas, documentación de ejemplos, mensajes del núcleo Python y nombres visibles de CI.
- Corrige la numeración discontinua y duplicada de capítulos en `SKILL.md`.
- Sincroniza superficies de versión a ALMAS 1.10.2.
- No modifica fórmulas, pesos, umbrales, ontología, discriminadores ni contratos de datos.


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

First public GitHub release.

- Defines the generalized AF/KA/AG/LG structural compatibility model.
- Defines IEM, IDD/IDE alias, IRC, IAT, ICC and ICE.
- Defines dependency-aware roots, pillars, counterevidence, null-model, ablation and birth-time robustness rules.
- Defines synastry, declination, antiscia, composite, Davison, draconic and temporal layers at specification level.
- Defines comparative doctrine, hermeneutic synthesis and multidimensional relational ontology.
- Defines the canonical-analysis → report-model → publication contract.
- Adds a dependency-free Python scoring core for pillar aggregation, IEM, IDD and IRC.
- Adds a precomputed-pillar API and `almas-score` command-line interface.
- Adds formal input/output JSON Schemas.
- Adds **14 deterministic unit tests** and GitHub Actions CI.
- Adds public module/discriminator manifests and source-provenance registry.
- Establishes a publication boundary: generalized rules and synthetic fixtures by default; real cases are permitted only when their underlying data are already public, independently verifiable and cited. Private/non-public case material is excluded.
