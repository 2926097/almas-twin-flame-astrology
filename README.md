# ALMAS · Astrología Metafísica Relacional

**Versión pública:** 1.10.1  
**Estado:** especificación de investigación reproducible + núcleo de scoring ejecutable

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

Hay dos manifiestos con funciones distintas:

- `manifests/almas-module-manifest.json`: módulos arquitectónicos de ALMAS;
- `manifests/analysis-pipeline-manifest.json`: secuencia ejecutable M00–M31 de un análisis FULL.

El pipeline preencarnatorio de ocho etapas está en `manifests/preincarnation-pipeline-manifest.json`.

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
schemas/
reference/
examples/
src/almas_tfa/
tests/
public_cases/
```

## Núcleo Python

El paquete incluye un núcleo determinista para:

- agregación de pilares;
- IEM AF/KA/AG/LG;
- aplicación única de ICE;
- gate estructural `SUPPORTED`;
- IDD mediante Jensen–Shannon;
- componentes de robustez e IRC.

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

La suite Python comprueba el núcleo numérico. El validador contractual comprueba integridad de versiones, manifiestos, schemas, fuentes, genealogía, fixtures y reglas de inferencia.

La infraestructura de validación externa está preregistrada, pero **no se declara validación empírica externa de las ontologías** hasta ejecutar cohortes holdout reales conforme a `docs/EXTERNAL_VALIDATION_PROTOCOL.md`.

## Publicación y privacidad

Los fixtures de `examples/` son sintéticos. Los casos reales sólo pueden aparecer en `public_cases/` cuando los datos subyacentes ya sean públicos, citables e independientemente verificables.

Véase `docs/PUBLICATION_POLICY.md`.

## Versionado

`VERSION` es la única versión pública de ALMAS. Los módulos internos pueden mantener `schema_version`, `manifest_version` o `engine_revision`, pero no SemVer público independiente.

## Licencia

No se ha seleccionado todavía una licencia open source. Publicar el repositorio en GitHub no concede por sí mismo derechos de reutilización adicionales a los previstos por la ley aplicable y los términos de GitHub.
