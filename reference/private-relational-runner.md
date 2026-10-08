# Runner privado de solicitudes relacionales

## Finalidad

`ALMAS_PRIVATE_RELATIONAL_RUNNER_V1` cierra el trayecto operativo entre una
solicitud del panel y el pipeline M00-M31 sin publicar datos de una relación
privada.

La función de librería es
`execute_relational_work_request(work_request, manifest, ...)`.
El entrypoint de repositorio es:

`python scripts/run_relational_work_request.py REQUEST.json --output-dir ...`

## Preflight sin astronomía

`--assessment-only` ejecuta exclusivamente el assessment contractual. Puede
usarse para que el frontend sepa si la solicitud contiene sujetos, perfil y
políticas suficientes antes de inicializar Moira.

## Ejecución de producción

La ejecución real exige declarar:

- `--kernel-path`;
- `--kernel-sha256`;
- `--kernel-family` (`DE430`, `DE440` o `DE441`);
- `--house-system`.

No existe descarga automática, geocodificación ni autodetección silenciosa del
kernel. El `MoiraProductionBackend` verifica la versión fijada y el SHA-256.

El runner usa el mismo backend para M02 y M08, llama a
`configured_handlers(...)` y ejecuta el manifiesto normativo
`manifests/analysis-pipeline-manifest.json`.

## Salidas locales

El directorio indicado recibe:

- `request_assessment.json`;
- `raw_input.json`;
- `orchestration_run.json`;
- `execution_receipt.json`;
- `canonical_analysis.json`, únicamente cuando existe en la salida canónica
  del pipeline.

El runner nunca reconstruye un canonical alternativo. Si M30 no lo produce,
`canonical_analysis.json` no se crea.

## Privacidad

El runner no envía el caso a GitHub, no ejecuta network I/O propio y no publica
fixtures. El archivo de solicitud y todas las salidas permanecen en las rutas
locales indicadas por el operador. La política general de publicación de ALMAS
sigue prohibiendo reutilizar casos privados como ejemplos sintéticos.

## Receipt

`execution_receipt.json` conserva hash SHA-256 de la solicitud, perfil,
preset de política, fingerprint de política, procedencia del backend, estado
de todos los módulos, módulos FAILED/NOT_EVALUABLE, estado M30 y fingerprint
canónico cuando exista.

El receipt declara expresamente:

`canonical_reconstructed_outside_pipeline=false`

`network_io_requested_by_runner=false`

`case_published_by_runner=false`
