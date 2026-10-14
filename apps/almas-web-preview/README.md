# ALMAS Web — vista experimental aislada

Esta carpeta contiene un visor **read-only** de JSON canónico, cuya importación permanece estrictamente local, y una demostración **separada, opcional y sintética** del motor Python. El botón de demostración ejecuta únicamente una solicitud GET fija a través del proxy Vercel; no transmite el JSON importado, fechas ni identidades. El motor calcula en Render puntuaciones de pilares **sintéticos previamente definidos**, no cartas ni resultados `canonical_analysis`. El módulo `validator.mjs` es **solo un preflight estructural parcial**, NO un validador completo de JSON Schema Draft 2020-12 y nunca sustituye M30/M31. Los test fixtures son mínimos y no pretenden validar el esquema oficial completo.

Comprobación local (Node 20+):

```bash
node --test apps/almas-web-preview/test/validator.test.mjs
```

Desplegar **todos** los activos del visor: `index.html`, `app.mjs`, `birth-request.mjs`, `birth-ui.mjs`, `birth-geocoding.mjs`, `symbolic-reading.mjs`, `validator.mjs`, `local-inspection.mjs`, `evidence-graph.mjs`, `astrology-view.mjs`, `report-view.mjs`, `json-lexical-digest.mjs`, `full-schema-validator.mjs` (generado durante build), `api/synthetic.js`, `api/canonical-demo.js` y `vercel.json`, únicamente a la aplicación Vercel aislada con Vercel Authentication activada. **No omitir `local-inspection.mjs`: `app.mjs` lo importa estáticamente y su ausencia impediría cargar toda la interfaz.** Configurar `ALMAS_ENGINE_URL` y `ALMAS_API_SHARED_SECRET` cifradas solo para Preview. El endpoint se conecta exclusivamente al servicio gratuito Render `almas-engine-synthetic-preview`, con `autoDeploy=no`, y rechaza métodos con payload y rutas dinámicas. No usar casos privados como fixtures. Mantener Atacires SHADOW/NO-GO y sin alterar los índices productivos. Consultar `ENGINE_DEMO.md`, `CANONICAL_GATE_DEMO.md`, `LOCAL_EVIDENCE_VIEWER.md` y los tests.


## Entrada natal por ciudad (geocodificación explícita)

El formulario de ALMAS Web 1.3 sustituye las tres cajas visibles de latitud, longitud y zona IANA de cada persona por **Ciudad de nacimiento** y **Buscar ciudad**. No se ejecutan consultas al abrir la página ni al teclear. Cuando el usuario pulsa el botón (o Enter), `birth-ui.mjs` envía **exclusivamente el texto escrito en la caja de ciudad**, mediante GET directo desde el navegador a `https://geocoding-api.open-meteo.com/v1/search` (sin cookies ni referer), nunca nombres, fechas, horas o el resto de la solicitud. Open-Meteo obtiene los datos de GeoNames, con atribución CC BY 4.0 visible en el panel. La API gratuita está destinada a uso no comercial; antes de distribución comercial se requiere servicio/licencia apropiada.

Se ofrecen hasta diez coincidencias indicando ciudad, división administrativa y país, **sin seleccionar nunca automáticamente**. La elección explícita fija únicamente en estado local la latitud, longitud y `timezone` IANA proporcionados por el servicio; los tres campos se mantienen ocultos. Cualquier edición posterior del texto invalida tanto la elección como solicitudes calculadas/exportaciones. Si la API no encuentra una localidad o no devuelve coordenadas/zona válidas, el formulario se bloquea sin adivinar coordenadas; se puede buscar `Ciudad, Provincia` o `Ciudad, País`.

Esta es una localización orientativa del municipio, no coordenadas de una dirección natal ni garantía automática del huso **histórico**. El backend local sigue validando el horario civil y rechaza transiciones DST ambiguas o inexistentes. La política CSP del servidor local permite conexión exclusivamente al propio origen y al endpoint geográfico citado. No se modifica la política **NO-GO** de procesamiento remoto personal.

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

## Gate de inicio astronómico local (1.3.1, cambio propuesto)

El servidor privado local **no se inicia** si no encuentra un kernel SPK en disco, si su SHA-256 no coincide exactamente con el suministrado, si falta `moira-astro==6.8.2` o si se intenta utilizar un sistema de casas distinto de `PLACIDUS` sin referencia dorada. La opción `--preflight-only` comprueba estos requisitos sin levantar un puerto ni tratar datos natales. Un resultado `LOCAL_RUNTIME_READY` **no** significa certificación independiente de los cálculos: el gate dorado astronómico permanece separado.

Para utilizar el kernel DE440s público de JPL/NAIF que ya aparece en `.github/workflows/astronomy-backend.yml`:

```bash
curl --fail --location \
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp' \
  --output /ruta/local/de440s.bsp
echo 'c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2  /ruta/local/de440s.bsp' | sha256sum --check -
PYTHONPATH=src .venv/bin/python apps/almas-web-preview/local_engine_server.py \
  --kernel-path /ruta/local/de440s.bsp \
  --kernel-sha256 c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2 \
  --kernel-family DE440 --house-system PLACIDUS --preflight-only
```

La descarga es una acción manual, explícita y previa al cálculo, y no transmite nacimientos. Para ejecutar después el servidor se usa el mismo comando **sin** `--preflight-only` tras generar los activos `npm run build`. Nunca subas archivos personales ni el kernel a la Preview.

## Lectura automática simbólica experimental (1.3.4)

El panel de análisis local incluye una lectura por cada punto ya presente en `canonical.natal_context.subjects.*.point_signs`. El módulo `symbolic-reading.mjs` reutiliza `astrology-view.mjs` para mostrar posiciones, signos, casas, decanatos, regentes y retrogradación **solo si están declarados**. No calcula efemérides, aspectos, orbes, posiciones, nuevos índices ni estados de modelos. Para los planetas y puntos contemplados por la política editorial `ALMAS_SYMBOLIC_EDITORIAL_V1` aporta asociaciones convencionales etiquetadas siempre `E_PROJECT_HYPOTHESIS`, no hechos probados ni diagnóstico psicológico. No evalúa por sí solo vínculos de llama gemela.

Cada comentario conserva una ruta canónica y los datos faltantes se etiquetan como no evaluables. La lectura puede descargarse como JSON únicamente por pulsación local; no llega a Vercel, Render ni a un modelo de IA remoto. **Esta lectura no sustituye la autoría fuente-a-fuente ni el DOCX/PDF oficial**. Su transparencia es una base para el trabajo editorial, no una certificación científica.
