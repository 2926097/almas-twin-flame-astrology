# ALMAS Web — vista experimental aislada

Esta carpeta contiene un visor **read-only** de JSON canónico, cuya importación permanece estrictamente local, y una demostración **separada, opcional y sintética** del motor Python. El botón de demostración ejecuta únicamente una solicitud GET fija a través del proxy Vercel; no transmite el JSON importado, fechas ni identidades. El motor calcula en Render puntuaciones de pilares **sintéticos previamente definidos**, no cartas ni resultados `canonical_analysis`. El módulo `validator.mjs` es **solo un preflight estructural parcial**, NO un validador completo de JSON Schema Draft 2020-12 y nunca sustituye M30/M31. Los test fixtures son mínimos y no pretenden validar el esquema oficial completo.

Comprobación local (Node 20+):

```bash
node --test apps/almas-web-preview/test/validator.test.mjs
```

Desplegar **todos** los activos del visor: `index.html`, `app.mjs`, `birth-request.mjs`, `birth-ui.mjs`, `validator.mjs`, `local-inspection.mjs`, `evidence-graph.mjs`, `astrology-view.mjs`, `report-view.mjs`, `json-lexical-digest.mjs`, `full-schema-validator.mjs` (generado durante build), `api/synthetic.js`, `api/canonical-demo.js` y `vercel.json`, únicamente a la aplicación Vercel aislada con Vercel Authentication activada. **No omitir `local-inspection.mjs`: `app.mjs` lo importa estáticamente y su ausencia impediría cargar toda la interfaz.** Configurar `ALMAS_ENGINE_URL` y `ALMAS_API_SHARED_SECRET` cifradas solo para Preview. El endpoint se conecta exclusivamente al servicio gratuito Render `almas-engine-synthetic-preview`, con `autoDeploy=no`, y rechaza métodos con payload y rutas dinámicas. No usar casos privados como fixtures. Mantener Atacires SHADOW/NO-GO y sin alterar los índices productivos. Consultar `ENGINE_DEMO.md`, `CANONICAL_GATE_DEMO.md`, `LOCAL_EVIDENCE_VIEWER.md` y los tests.


## ALMAS Web 1.3 — dos nacimientos y motor integral local

La Preview de Vercel **no admite datos natales para cálculo remoto**. Ahora incluye un formulario de dos nacimientos que genera localmente `ALMAS_WORK_REQUEST` v1.26.0, sin solicitar detalles extra ni inferir coordenadas. El botón `Calcular M00–M31 en este equipo` está oculto fuera de `http://127.0.0.1` y solo se habilita tras una comprobación positiva del servicio local.

Para calcular con posiciones e índices del motor real se necesita el programa separado `local_engine_server.py`, que se ejecuta en el ordenador del usuario y requiere un kernel Moira/JPL instalado y verificado. No se publica en Vercel, no acepta conexiones no locales ni transmite datos personales a Render. Requiere pulsar `Calcular` expresamente.

El servidor usa el adaptador y orquestador oficiales, verifica los schemas y SHA de `canonical_analysis`, M30 y M31, devuelve el atlas descriptivo sin autoría, y el navegador vuelve a validarlos antes de permitir el modelo HTML imprimible. Los índices salen del núcleo, nunca se recalculan en JavaScript. **El HTML M31 es declarativo, no un informe narrativo autoral**, y estados no evaluables no se convierten en puntuaciones. La producción privada, el procesamiento multiusuario y la autoría DOCX/PDF permanecen NO-GO.

Instrucciones detalladas, dependencias exactas y pruebas: [ALMAS_WEB_1_3_INTEGRAL_ROADMAP.md](ALMAS_WEB_1_3_INTEGRAL_ROADMAP.md). Prueba adicional: `PYTHONPATH=src:tests python -m unittest discover -s apps/almas-web-preview -p 'test_local_engine_server.py' -v`.

## Validación exhaustiva fuera del navegador

`schema_gate.py` usa `jsonschema==4.26.0`, Draft 2020-12 y el registro local de esquemas oficiales de este repositorio. Resuelve referencias desde el checkout, sin red, no cambia el canonical y produce errores sin imprimir valores de los datos de entrada. Su veredicto `SCHEMA_VALID` acredita exclusivamente conformidad con el **JSON Schema oficial**, nunca un gate M30/M31, regresión del motor ni validación empírica.

```bash
python -m pip install 'jsonschema==4.26.0'
python apps/almas-web-preview/schema_gate.py /ruta/local/canonical_analysis.json
python -m unittest discover -s apps/almas-web-preview/test -p 'test_schema_gate.py' -v
```

El navegador **no llama** a esta CLI; la validación exhaustiva debe ejecutarse en una máquina local o entorno autorizado antes de habilitar cualquier API. Los ejemplos de tests son solo controles negativos de schema y nunca casos personales.

## Pruebas de integración API sintética

```bash
node --test apps/almas-web-preview/test/validator.test.mjs apps/almas-web-preview/test/proxy.test.mjs
PYTHONPATH=src python -m unittest discover -s apps/almas-api-sandbox -p test_server.py -v
```

La CLI canónica offline y la API sintética son superficies **distintas**. El resultado `PRECOMPUTED_PILLARS` de la API **no** supera ni sustituye la validación `canonical_analysis` y M30/M31.

## Synthetic canonical M30/M31 demonstration

A separate, fixed read-only endpoint `/api/canonical-demo` is available
for **synthetic-only** schema + M30/M31 checks. The browser import remains local
and does not use this route. Deploy `api/canonical-demo.js` with the existing
static assets and `vercel.json`. See `CANONICAL_GATE_DEMO.md`.
