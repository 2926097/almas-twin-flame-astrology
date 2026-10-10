# ALMAS Web — vista experimental aislada

Esta carpeta es una web estática de inspección **read-only** de JSON canónico. Ningún cálculo se ejecuta ni se envían archivos a servidores. El módulo `validator.mjs` es **solo un preflight estructural parcial**, NO un validador completo de JSON Schema Draft 2020-12 y nunca sustituye M30/M31. Los test fixtures son mínimos y no pretenden validar el esquema oficial completo.

Comprobación local (Node 20+):

```bash
node --test apps/almas-web-preview/test/validator.test.mjs
```

Desplegar únicamente `index.html`, `app.mjs`, `validator.mjs` a la aplicación Vercel aislada con Vercel Authentication activada. No conectar a Render ni usar casos privados como fixtures. Mantener Atacires SHADOW/NO-GO y sin alterar los índices productivos. La rama es experimental y no debe fusionarse sin revisión.

## Validación exhaustiva fuera del navegador

`schema_gate.py` usa `jsonschema==4.26.0`, Draft 2020-12 y el registro local de esquemas oficiales de este repositorio. Resuelve referencias desde el checkout, sin red, no cambia el canonical y produce errores sin imprimir valores de los datos de entrada. Su veredicto `SCHEMA_VALID` acredita exclusivamente conformidad con el **JSON Schema oficial**, nunca un gate M30/M31, regresión del motor ni validación empírica.

```bash
python -m pip install 'jsonschema==4.26.0'
python apps/almas-web-preview/schema_gate.py /ruta/local/canonical_analysis.json
python -m unittest discover -s apps/almas-web-preview/test -p 'test_schema_gate.py' -v
```

El navegador **no llama** a esta CLI; la validación exhaustiva debe ejecutarse en una máquina local o entorno autorizado antes de habilitar cualquier API. Los ejemplos de tests son solo controles negativos de schema y nunca casos personales.
