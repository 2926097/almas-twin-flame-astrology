# Validación astronómica dorada · ALMAS 1.18

## Objeto

Este gate valida la reproducibilidad numérica del backend astronómico de producción. No añade técnicas astrológicas, scoring, pesos, discriminadores ni ontología.

La política normativa es `ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1`. Se congela antes de observar resultados procedentes de un kernel JPL real.

## Geometría común

Toda comparación de posiciones fundamentales debe respetar exactamente el contrato del backend:

- origen geocéntrico;
- zodiaco tropical;
- eclíptica y equinoccio verdaderos de fecha;
- reducción aparente;
- posiciones zodiacales no topocéntricas;
- True North Node;
- DE440 como familia de kernel del gate.

Las coordenadas geográficas se utilizan para casas y ángulos, no para desplazar topocéntricamente las posiciones zodiacales canónicas.

## Casos preregistrados

`validation/astronomy/golden-cases.v1.json` contiene seis entradas sintéticas, sin datos personales, repartidas entre 1950 y 2050 y entre hemisferios y latitudes distintas. Los inputs quedan congelados antes de producir resultados dorados.

## Tolerancias

Las tolerancias son límites de aceptación de ingeniería para detectar divergencias de implementación. No expresan incertidumbre física ni precisión observacional.

La política fija 5" para longitudes/latitudes planetarias salvo la Luna, 15"; 10" para declinación salvo la Luna, 20"; 60" para True Node, ángulos y cúspides.

No existe promedio compensatorio. Cada medida requerida debe estar presente y dentro de su tolerancia. Una sola ausencia o desviación fuera de tolerancia hace fallar el caso.

## Referencia independiente

Las posiciones planetarias deben contrastarse con software independiente usando DE440 y la misma geometría. Skyfield es la implementación preferida para posiciones fundamentales, pero el registro de ejecución debe identificar versión y procedimiento efectivos.

True Node y casas/ángulos requieren implementaciones independientes específicas. No se admite como referencia una segunda llamada al mismo código Moira.

## Estado

El gate fue ejecutado con `de440s.bsp` fingerprintado y cerró como `PASS` en Python 3.10 y 3.12. Las etapas `PLANETARY_REFERENCE`, `TRUE_NODE_REFERENCE`, `HOUSE_REFERENCE` y `COMPLETE_GATE` resultaron satisfactorias en los seis casos preregistrados.

El `COMPLETE_GATE` contiene 47 medidas obligatorias por caso, 282 por entorno. Los resúmenes de Python 3.10 y 3.12 son byte-equivalentes a nivel JSON y comparten SHA-256 `dcc6d349e6eabc22f90c6911e3fbf466579872f6b186471d822a7a892a8faa9a`. No hubo fallos ni modificación posterior de tolerancias. El máximo global observado fue 39,8903887122″ en ASC/H1 de `G06_CAPE_TOWN_2050`, por debajo del límite preregistrado de 60″.

La evidencia de cierre es `validation/astronomy/complete-stage-evidence.v1.json`, complementada por las evidencias de las tres etapas parciales. El campo `status=PREREGISTERED_NOT_EXECUTED` de la política se conserva deliberadamente como huella histórica del estado en que fueron congelados los criterios antes de observar resultados; el estado empírico posterior se registra exclusivamente en los archivos de evidencia para no reescribir el preregistro.
