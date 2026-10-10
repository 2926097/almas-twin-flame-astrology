# ALMAS Web — vista experimental aislada

Esta carpeta contiene un visor **read-only** de JSON canónico, cuya importación permanece estrictamente local, y una demostración **separada, opcional y sintética** del motor Python. El botón de demostración ejecuta únicamente una solicitud GET fija a través del proxy Vercel; no transmite el JSON importado, fechas ni identidades. El motor calcula en Render puntuaciones de pilares **sintéticos previamente definidos**, no cartas ni resultados `canonical_analysis`. El módulo `validator.mjs` es **solo un preflight estructural parcial**, NO un validador completo de JSON Schema Draft 2020-12 y nunca sustituye M30/M31. Los test fixtures son mínimos y no pretenden validar el esquema oficial completo.

Comprobación local (Node 20+):

```bash
node --test apps/almas-web-preview/test/validator.test.mjs
```

Desplegar `index.html`, `app.mjs`, `validator.mjs`, `api/synthetic.js` y `vercel.json` únicamente a la aplicación Vercel aislada con Vercel Authentication activada. Configurar `ALMAS_ENGINE_URL` y `ALMAS_API_SHARED_SECRET` cifradas solo para Preview. El endpoint se conecta exclusivamente al servicio gratuito Render `almas-engine-synthetic-preview`, con `autoDeploy=no`, y rechaza métodos con payload y rutas dinámicas. No usar casos privados como fixtures. Mantener Atacires SHADOW/NO-GO y sin alterar los índices productivos. Consultar `ENGINE_DEMO.md` y los tests.

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
