# ALMAS Web — Explorador local de evidencias (solo lectura)

Esta interfaz permite inspeccionar **exclusivamente en el navegador** un
`canonical_analysis.json` previamente generado por ALMAS y autorizado para
el propio usuario. No añade endpoints ni formularios HTTP de carga.

## Alcance y contrato

- Importación local con `File.text()`, limitada a 5 MiB; la estructura se
  comprueba mediante `structuralPreflight` **parcial**.
- Visualización de registros `evidence` de M17: ID de raíz, estado de fuerza
  (`CALCULATED_CORE`, `CALCULATED_SUPPORT_ONLY`, `NOT_EVALUABLE`),
  fuerza original, elegibilidad core, familias de dependencia y número
  descriptivo de contactos. El usuario puede filtrar por estado y buscar
  identificador/familia (sin cambiar el valor de origen).
- Visualización de `counterevidence`: ID, modelo AF/KA/AG/LG,
  tipo, familia, severidad **original** (incluido `null`), criterio
  `essential` y número de referencias. El campo arbitrario `note`
  no se presenta para minimizar datos potencialmente sensibles.
- Vista de limitaciones declaradas, sin reinterpretación ni resúmenes
  automáticos. Máximo 80 registros visibles por tabla y apartado
  (proyección hasta 100 desde helpers), indicando el total; no existe
  truncamiento silencioso.
- Las celdas se crean mediante `createElement`/`textContent`. Ningún
  dato importado se introduce con `innerHTML`, ni se transmite mediante
  `fetch`. El archivo se libera de memoria al pulsar **Borrar sesión**
  o al importar otro. Los lectores de archivos pendientes quedan
  invalidados por `loadEpoch`.

## Interpretación

El número de raíces, contactos y familias **no** representa una muestra de
observaciones estadísticamente independientes ni prueba exclusividad
metafísica. La fuerza `strength` se muestra de 0 a 1 exactamente como la
entrega el motor, sin convertirla a un índice nuevo. Los valores `null`
**no** se sustituyen por cero.

Esta interfaz no calcula ni modifica posiciones, aspectos, evidencia,
puntuaciones, IEM/IDD/IRC/IAT/ICC/ICE, regresiones ni ontología.
Atacires permanece SHADOW/NO-GO. El visor no certifica por sí mismo
JSON Schema Draft 2020-12, M30/M31 ni validez externa.

La demostración **remota** M30/M31, situada en un panel independiente,
sigue operando **solo sobre fixtures públicos sintéticos** y jamás
recibe este archivo.

## Pruebas

```bash
node --test apps/almas-web-preview/test/local-inspection.test.mjs
```

Las pruebas comprueban filtrado, fuerza nula frente a cero, orden
determinista, límites, integridad del objeto original, omisión de notas
arbitrarias y tratamiento de texto no confiable como texto literal.
