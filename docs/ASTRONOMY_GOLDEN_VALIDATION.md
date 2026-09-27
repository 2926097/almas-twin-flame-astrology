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

El gate permanece `PREREGISTERED_NOT_EXECUTED` hasta que se incorporen:

1. SHA-256 del kernel DE440 real utilizado;
2. resultados del backend;
3. resultados de las referencias independientes;
4. archivos de resultado conformes a `astronomy-golden-result.schema.json`;
5. ejecución satisfactoria del evaluador para todos los casos.

Hasta entonces ALMAS puede considerar implementado el adaptador, pero no cerrado el frente de validación astronómica dorada.
