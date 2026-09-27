# Auditoría final de release · ALMAS 1.18.0

**Fecha:** 27 de septiembre de 2026  
**Rama auditada:** `evolution/1.18.0-production-astronomy-backend`  
**Base:** ALMAS 1.17.0  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** backend astronómico de producción opcional, reproducible y fail-closed para M02/M08.

## Alcance

ALMAS 1.18.0 elimina el bloqueo de implementación de M02 natal y M08 Davison mediante un adaptador de producción basado en `moira-astro==6.8.2`.

La dependencia astronómica se mantiene fuera del núcleo obligatorio y se activa sólo mediante el extra `astronomy-moira`.

La release no añade técnicas, aspectos, pesos, discriminadores ni reglas ontológicas.

## Política de backend

`ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1` congela:

- adaptador `ALMAS_MOIRA_JPL_SPK_V1`;
- provider `moira-astro==6.8.2`;
- licencia declarada MIT;
- kernel JPL local;
- SHA-256 obligatorio;
- familias DE430/DE440/DE441;
- timezone IANA;
- coordenadas numéricas;
- True Node;
- sistema de casas explícito;
- ausencia de red/geocodificación durante cálculo;
- prohibición de fallback polar.

## M02

`MoiraProductionBackend.calculate_natal` produce la superficie requerida por el pipeline actual:

- longitudes y latitudes eclípticas;
- velocidad;
- retrogradación;
- declinaciones;
- Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno y Plutón;
- `NORTH_NODE` y `SOUTH_NODE`;
- doce cúspides;
- ASC/DSC/MC/IC;
- metadatos UTC/geográficos;
- procedencia de backend/kernel.

El handler M02 convierte límites de datos/backend en `NOT_EVALUABLE`.

## M08

M08 reutiliza el mismo adaptador y fija:

- `time_midpoint=UTC_INSTANT`;
- midpoint geográfico `SPHERICAL_GREAT_CIRCLE`;
- recálculo mediante el mismo pipeline natal.

Las convenciones incompatibles quedan `NOT_EVALUABLE`.

## Procedencia

`schemas/astronomy-backend-provenance.schema.json` fija provider, versión, kernel SHA-256, sistema de casas, nodo, zodiaco y firewalls de red/geocodificación.

`schemas/natal-chart.schema.json` referencia dicho contrato.

## CI funcional confirmado

Sobre el HEAD funcional previo al cierre editorial:

- `Contrato público`: SUCCESS;
- `Núcleo Python 3.10`: SUCCESS;
- `Núcleo Python 3.12`: SUCCESS;
- **454 tests deterministas** por matriz del núcleo;
- `Backend astronómico 3.10`: SUCCESS;
- `Backend astronómico 3.12`: SUCCESS;
- `moira-astro: 6.8.2`;
- **11 tests específicos** del adaptador en cada versión de Python;
- runtime contract: PASS.

El CI específico no incluye ni descarga un kernel JPL real.

## Gate astronómico pendiente

La implementación de producción queda disponible, pero la validación astronómica dorada permanece abierta.

Para cerrar ese gate se requiere:

1. kernel JPL real identificado por SHA-256;
2. fixtures dorados independientes;
3. tolerancias numéricas preregistradas;
4. comparación independiente de posiciones planetarias y nodos;
5. validación separada de casas/ángulos;
6. reproducibilidad documentada.

Skyfield permanece como candidato de verificación independiente de posiciones fundamentales.

## Registro de ejecución

M02 y M08 pasan de `BACKEND_REQUIRED` a `EXECUTABLE_HANDLER`.

La ejecución real requiere configuración explícita del adaptador y kernel verificado. La ausencia de estos recursos no activa ningún fallback.

## Estado empírico

Esta release mejora reproducibilidad del cálculo astronómico y elimina un bloqueo de software. No constituye validación científica de la astrología, no ejecuta un holdout externo real y no convierte resultados astronómicos o índices en probabilidad metafísica.
