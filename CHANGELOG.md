# Changelog

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
- Convierte `docs/DUAL_ENGINE_ARCHITECTURE.md` en nota histórica de compatibilidad.
- Añade invariantes CI para impedir que reaparezca la arquitectura dual.

### Fase 1 · Fuentes y genealogía — iniciada
- Formaliza `schemas/source-registry.schema.json`.
- Añade `reference/concept-registry.json`.
- Añade `reference/doctrinal-genealogy.json`.
- Añade `docs/SOURCE_INTEGRATION_PLAN.md` y `docs/SOURCE_GAPS.md`.
- El registro contiene 36 fuentes en el punto de partida de esta fase.
- Establece que una fuente define significado/procedencia/límites pero no añade puntuación astrológica por su mera existencia.

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
