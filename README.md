# ALMAS · Astrología Metafísica Relacional

**Versión pública:** 1.21.0  
**Estado:** pipeline modular M00–M31 ejecutable + recurrencia semántica PX/PS v2 + calibración de especificidad S1–S9 + perfiles de análisis + backends astronómicos inyectables

ALMAS es una única skill modular para investigar relaciones desde astrología relacional, ontología comparada, doctrina, reconstrucción preencarnatoria, validación y hermenéutica. No reduce un vínculo a una etiqueta única.

## Principios

- Separar siempre dato calculado/documental, técnica, doctrina, uso contemporáneo e hipótesis del proyecto.
- Rareza estadística no equivale a probabilidad metafísica.
- La temporalidad activa arquitectura previa; no crea ontología.
- Ningún aspecto, asteroide, evento o sincronía aislada define una categoría.
- Las técnicas dependientes no cuentan como confirmaciones independientes.
- Cuando dos modelos producen la misma firma y no existe discriminador validado, el resultado permanece `INSUFFICIENT`.
- Los hechos observables, el consentimiento y los límites reales prevalecen sobre cualquier lectura simbólica.
- Los casos privados no se publican ni se reutilizan como fixtures encubiertos.

## Arquitectura

ALMAS se publica como **una única skill**. Sus motores son módulos internos:

- astrología metafísica relacional;
- ontología multiaxial;
- doctrina, genealogía y fuentes;
- contrato preencarnatorio;
- roles y causalidad;
- temporalidad y hechos documentales;
- validación, ablación y robustez;
- reporting.

La arquitectura normativa está en `docs/MODULE_ARCHITECTURE.md`.

Los manifiestos y registros principales tienen funciones distintas:

- `manifests/almas-module-manifest.json`: módulos arquitectónicos de ALMAS;
- `manifests/structural-policy-manifest.json`: técnica, dependencia, orbes, elegibilidad y loading estructural;
- `manifests/analysis-pipeline-manifest.json`: secuencia M00–M31 de un análisis FULL;
- `manifests/preincarnation-pipeline-manifest.json`: pipeline preencarnatorio de ocho etapas;
- `manifests/execution-registry.json`: estado ejecutable real de cada etapa M00–M31.

## Modelos e índices

Los cuatro modelos operativos recurrentes son:

- **AF** — almas afines;
- **KA** — vínculo kármico;
- **AG** — almas gemelas / soulmate;
- **LG** — llamas gemelas / twin flame.

Sus índices no son probabilidades metafísicas:

- **IEM** — Índice de Encaje del Modelo.
- **IDD** — Índice de Discriminación Diagnóstica.
- **IRC** — Índice de Robustez de la Clasificación.
- **IAT** — Índice de Activación Temporal.
- **ICC** — Índice de Cobertura Canónica.
- **ICE** — Índice de Contraevidencia Estructural.

La ontología completa se analiza por ejes independientes de origen, contrato preencarnatorio, historia/continuidad, función, fenomenología, polaridad, modalidad, fase, viabilidad y reciprocidad.

## Flujo canónico

`fuentes + datos → cálculo → evidencia → deduplicación → raíces independientes → validación → ontología → reconstrucción preencarnatoria → temporalidad/hechos → informe`

`canonical_analysis.json` es la verdad analítica de la capa astrológica. El módulo contractual consume esa salida mediante el bridge canónico y no debe recalcular silenciosamente la evidencia.

Desde 1.13.0, una ejecución FULL configurada puede derivar automáticamente fuerza de raíces, pilares, atribuciones Shapley/IDD, sensibilidad horaria, componentes de robustez, un universo nulo autocontenido y `canonical_analysis`. Desde 1.14.0, PX y PS se reconstruyen mediante recurrencia semántica multitécnica sin reescribir `root_key`; M23 publica una curva R5/R15/R30/R60/R120 incluso sin rating horario documentado; y M30 evalúa completitud relativa a perfiles como `FULL_ASTROLOGY` o `FULL_MULTIDISCIPLINARY`.

Desde 1.15.0, ALMAS añade calibración de especificidad S1–S9 sin cambiar los scores de producción: mide dependencia/diversidad de la recurrencia, calibra motivos contra nulls y controles sintéticos, define firewalls para cohortes externas y candidatos PX v3, y bloquea por release cualquier activación PX v3 no versionada.

Desde 1.16.0, ALMAS operacionaliza el ciclo de validación con preregistro V1, apertura holdout V2, ledger criptográfico V3, continuidad V4 y cierre/auditoría V5. Estos controles permiten demostrar trazabilidad del procedimiento sin convertir una evaluación en activación automática, validación L3 ni probabilidad metafísica.

Desde 1.17.0, ALMAS publica un manifiesto estructural único que enlaza técnica, dependencia, orbes y loading. Los orbes siguen siendo explícitos y declarados por entrada; 1.17 no introduce valores implícitos, nuevas técnicas ni nuevos pesos.

Desde 1.18.0, M02 y M08 pueden ejecutarse con el adaptador opcional `MoiraProductionBackend`. La instalación del núcleo sigue sin arrastrar un motor astronómico; el extra `astronomy-moira` fija Moira 6.8.2 y todo cálculo exige un kernel JPL local cuyo SHA-256 forma parte de la procedencia.

Desde 1.19.0, el cierre M31 alimenta `authored_report`: una capa de autoría centrada en astrología y hermenéutica/metafísica basada en fuentes. La cadena materializa después DOCX y PDF B5 con fingerprint, bibliografía y preflight, sin recalcular la astrología ni convertir la infraestructura técnica en el contenido principal del informe.

Desde 1.20.0, la autoría adopta una síntesis **root-first**: parte de raíces y motivos semánticos ya calculados, integra sustrato natal, casas, ángulos/nodos, campo compuesto/Davison, dracónicas, lotes y puntos secundarios cuando aportan contexto, y desarrolla la temporalidad mediante activaciones concretas trazables. `TTRANSIT` puede generarse automáticamente contra endpoints de raíces existentes; el tránsito activa arquitectura previa y no predice por sí mismo acontecimientos ni decisiones de otra persona.

## Repositorio

```text
SKILL.md
VERSION
CHANGELOG.md
VALIDATION_STATUS.md
docs/
  ARCHITECTURE.md
  MODULE_ARCHITECTURE.md
  ONTOLOGY.md
  METRICS.md
  REPORTING.md
  SOURCE_POLICY.md
  PUBLICATION_POLICY.md
  EXTERNAL_VALIDATION_PROTOCOL.md
  history/
manifests/
  almas-module-manifest.json
  analysis-pipeline-manifest.json
  preincarnation-pipeline-manifest.json
  execution-registry.json
schemas/
reference/
examples/
src/almas_tfa/
tests/
public_cases/
```

## Núcleo Python

El paquete incluye un orquestador determinista y módulos ejecutables para:

- agregación de pilares;
- IEM AF/KA/AG/LG;
- aplicación única de ICE;
- gate estructural `SUPPORTED`;
- IDD mediante Jensen–Shannon;
- componentes de robustez e IRC;
- contrato común de módulos;
- validación de la secuencia M00–M31;
- ejecución secuencial de handlers registrados con protección contra sobrescritura canónica;
- geometría de sinastría, casas, declinaciones, antiscios, compuesta, RELCHART y dracónicas;
- lotes declarativos y baseline histórica Fortuna/Espíritu, más capa secundaria `support_only`;
- grafo de evidencia, deduplicación, raíces independientes y grafo de motivos semánticos recurrentes;
- contraevidencia, ablación AB0–AB8, sensibilidad horaria, modelos nulos y robustez;
- activación temporal y ledger documental;
- firewalls doctrinales, viabilidad/reciprocidad y gate de reporting;
- modelo documental M31 con fingerprint canónico y 11 secciones trazables;
- discriminación ontológica experimental integrada en M21 con preservación obligatoria de ambigüedad;
- registro canónico de promoción de discriminadores y firewall L3 hacia M25;
- gates de validez discriminante, cegamiento/leakage, genealogía documental y aislamiento de casos privados.

`M02` (natal) y `M08` (Davison) disponen de contrato ejecutable pero requieren backends astronómicos inyectados. `configured_handlers(...)` permite suministrarlos sin acoplar ALMAS a una biblioteca concreta.

La prueba `tests/test_full_pipeline.py` ejecuta sintéticamente M00–M31 de extremo a extremo.

Instalación local:

```bash
python -m pip install -e .
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate_public_contract.py
```

CLI para pilares ya calculados:

```bash
almas-score examples/precomputed-pillars.json
```

La CLI no calcula posiciones astronómicas; consume pilares ya derivados.

## Fuentes y doctrina

La política documental está en `docs/SOURCE_POLICY.md`. El registro canónico es `reference/source-registry.json`.

Las fuentes definen procedencia, significado y límites. No añaden puntuación astrológica por existir. Las operacionalizaciones astrología→metafísica creadas por ALMAS permanecen `E_PROJECT_HYPOTHESIS` salvo que una fuente describa explícitamente la técnica.

## Validación

![Public contract](https://github.com/2926097/almas-twin-flame-astrology/actions/workflows/public-contract.yml/badge.svg)
![Python core](https://github.com/2926097/almas-twin-flame-astrology/actions/workflows/python-tests.yml/badge.svg)

La suite Python cubre núcleo numérico, módulos M00–M31, recurrencia semántica, perfiles de análisis y una ejecución FULL sintética. El número exacto de tests se publica en `VALIDATION_STATUS.md`. El validador contractual comprueba integridad de versiones, manifiestos, schemas, fuentes, genealogía, fixtures y firewalls de inferencia.

La infraestructura de validación externa está preregistrada, pero **no se declara validación empírica externa de las ontologías** hasta ejecutar cohortes holdout reales conforme a `docs/EXTERNAL_VALIDATION_PROTOCOL.md`.

Actualmente no existe ningún `VALIDATED_DISCRIMINATOR` real: OD01–OD04 permanecen `EXPLORATORY`, OD05–OD06 `BLOCKED` y OD07 `RETIRED`. Cuando no existe un discriminador L3 aplicable, la ambigüedad ontológica debe preservarse.

## Publicación y privacidad

Los fixtures de `examples/` son sintéticos. Los casos reales sólo pueden aparecer en `public_cases/` cuando los datos subyacentes ya sean públicos, citables e independientemente verificables.

Véase `docs/PUBLICATION_POLICY.md`.

## Versionado

`VERSION` es la única versión pública de ALMAS. Los módulos internos pueden mantener `schema_version`, `manifest_version` o `engine_revision`, pero no SemVer público independiente.

## Licencia

No se ha seleccionado todavía una licencia open source. Publicar el repositorio en GitHub no concede por sí mismo derechos de reutilización adicionales a los previstos por la ley aplicable y los términos de GitHub.
