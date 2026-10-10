# ALMAS Web — vista experimental aislada

Esta carpeta es una web estática de inspección **read-only** de JSON canónico. Ningún cálculo se ejecuta ni se envían archivos a servidores. El módulo `validator.mjs` es **solo un preflight estructural parcial**, NO un validador completo de JSON Schema Draft 2020-12 y nunca sustituye M30/M31. Los test fixtures son mínimos y no pretenden validar el esquema oficial completo.

Comprobación local (Node 20+):

```bash
node --test apps/almas-web-preview/test/validator.test.mjs
```

Desplegar únicamente `index.html`, `app.mjs`, `validator.mjs` a la aplicación Vercel aislada con Vercel Authentication activada. No conectar a Render ni usar casos privados como fixtures. Mantener Atacires SHADOW/NO-GO y sin alterar los índices productivos. La rama es experimental y no debe fusionarse sin revisión.
