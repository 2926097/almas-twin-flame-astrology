# ALMAS 1.18.0 · Backend astronómico de producción

## Objetivo

ALMAS 1.18.0 elimina el bloqueo arquitectónico de M02/M08 sin acoplar el núcleo obligatorio a una biblioteca astronómica.

La release introduce un adaptador de producción opcional, reproducible y fail-closed. No añade técnicas astrológicas, pesos, discriminadores ni reglas ontológicas.

## A1 · Adaptador de producción

`ALMAS_MOIRA_JPL_SPK_V1` implementa los contratos `AstrologyBackend` y `DavisonBackend` mediante `moira-astro==6.8.2`.

El extra opcional es:

`astronomy-moira = ["moira-astro==6.8.2"]`.

La instalación básica de ALMAS sigue sin depender de Moira.

## A2 · Procedencia astronómica

`ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1` congela:

- proveedor y versión;
- familia de kernel;
- obligación de archivo JPL BSP local;
- SHA-256 esperado;
- timezone IANA;
- coordenadas numéricas;
- sistema de casas explícito;
- True Node;
- ausencia de red y geocodificación durante el cálculo;
- prohibición de fallback polar.

El schema `astronomy-backend-provenance.schema.json` formaliza la procedencia y se referencia desde la carta natal canónica.

## A3 · Fail-closed

El backend de producción no inventa ni degrada silenciosamente datos.

Quedan `NOT_EVALUABLE`:

- carta sin hora;
- timezone IANA inexistente;
- hora local ambigua;
- hora local inexistente;
- ausencia de coordenadas;
- kernel ausente;
- SHA-256 incorrecto;
- sistema de casas efectivo distinto del solicitado;
- fallback polar;
- política Davison incompatible.

## A4 · Natal

El adaptador produce:

- Sol, Luna y planetas clásicos hasta Plutón;
- longitud eclíptica geocéntrica aparente en eclíptica/equinoccio verdaderos de fecha;
- latitud eclíptica bajo el mismo contrato geométrico;
- ausencia de topocentrismo en las posiciones zodiacales canónicas;
- velocidad longitudinal;
- retrogradación;
- declinación;
- True North Node;
- South Node por oposición;
- doce cúspides;
- ASC/DSC/MC/IC;
- metadatos UTC y geográficos;
- procedencia completa del backend.

## A5 · Davison

M08 fija de forma explícita:

- midpoint temporal `UTC_INSTANT`;
- midpoint geográfico `SPHERICAL_GREAT_CIRCLE`;
- recálculo final mediante el mismo pipeline natal.

No se delega una convención Davison opaca al proveedor.

## A6 · Estado de ejecución

M02 y M08 pasan de `BACKEND_REQUIRED` a `EXECUTABLE_HANDLER` en el registro de ejecución.

M23–M25 pueden reutilizar el mismo objeto backend inyectado.

## A7 · CI

La release añade el workflow `Backend astronómico`, separado del núcleo.

Ese workflow:

1. instala ALMAS con `.[astronomy-moira]`;
2. comprueba que la versión instalada sea exactamente 6.8.2;
3. verifica la API pública requerida;
4. ejecuta los tests del adaptador en Python 3.10 y 3.12.

El smoke de runtime no carga un kernel externo en CI.

## A8 · Gate dorado preregistrado

La disponibilidad del adaptador no equivale a validación astronómica independiente.

ALMAS incorpora ahora `ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1`, congelado antes de observar resultados reales. El gate fija seis casos sintéticos, la geometría común, métricas obligatorias, tolerancias en segundos de arco y una regla sin promedios compensatorios.

El evaluador `astronomy_golden_validation.py` exige que todas las medidas estén presentes y dentro de tolerancia; faltas, duplicados, métricas no registradas o desviaciones hacen fallar el caso.

La ejecución empírica permanece abierta: todavía faltan el SHA-256 de un DE440 real, resultados Moira, referencias independientes de posiciones/True Node/casas y los archivos dorados resultantes. Skyfield continúa como implementación preferida para la referencia planetaria independiente.

## Invariantes

1. El backend no altera scoring ni weighting.
2. El backend no crea evidencia ontológica.
3. El kernel forma parte de la identidad del resultado.
4. No hay descargas ocultas durante cálculo.
5. No hay geocodificación implícita.
6. No hay fallback silencioso de casas.
7. La validación de la dependencia no se confunde con validación científica de la astrología.
