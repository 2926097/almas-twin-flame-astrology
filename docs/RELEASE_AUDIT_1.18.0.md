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
- **483 tests deterministas** por matriz del núcleo;
- `Backend astronómico 3.10`: SUCCESS;
- `Backend astronómico 3.12`: SUCCESS;
- `moira-astro: 6.8.2`;
- **12 tests específicos** del adaptador, 9 del gate dorado y 4 de la referencia Skyfield en el workflow específico;
- runtime contract: PASS.

El CI contractual no requiere un kernel. Una segunda matriz de validación descarga explícitamente el artefacto JPL/NAIF `de440s.bsp`, verifica sus fingerprints preregistrados y ejecuta la comparación planetaria independiente.

## Gate astronómico dorado cerrado

`ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1` fue congelado antes de observar resultados con seis casos sintéticos, métricas obligatorias, tolerancias, geometría y regla de decisión sin agregación compensatoria.

La validación real utilizó `de440s.bsp` con SHA-256 `c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2` y MD5 `3917ee56769db332790c751e2168843d`. Moira 6.8.2 fue contrastado con tres referencias independientes basadas en Skyfield 1.55: posiciones planetarias DE440, True Node por geometría osculadora y casas Placidus por implementación independiente de semi-arcos.

El workflow 36309678855 ejecutó y cerró satisfactoriamente `PLANETARY_REFERENCE`, `TRUE_NODE_REFERENCE`, `HOUSE_REFERENCE` y `COMPLETE_GATE` en Python 3.10 y 3.12. El gate completo contiene 47 medidas por caso y 282 por entorno; todos los casos resultaron `PASS`, no hubo fallos y los resúmenes fueron idénticos entre ambas versiones de Python.

El máximo global fue 39,8903887122″ en ASC/H1 de `G06_CAPE_TOWN_2050`, frente al límite preregistrado de 60″. Los thresholds no fueron modificados después de observar los resultados.

La evidencia canónica de cierre es `validation/astronomy/complete-stage-evidence.v1.json`, junto con las evidencias parciales planetaria, True Node y casas/ángulos.

## Contrato canónico cerrado

La superficie M30 queda sometida a `canonical-analysis.schema.json` Draft 2020-12 con raíz cerrada y trazabilidad namespace→productor documentada en `docs/CANONICAL_SCHEMA_AUDIT_1.18.md`.

El contrato exige los namespaces siempre emitidos, distingue los cuatro namespaces condicionales y compone schemas especializados mediante `$ref`. La procedencia astronómica se propaga desde M02 hasta M30; para `MOIRA_JPL_SPK` es obligatoria la procedencia completa del backend, versión y kernel.

La suite incorpora validación positiva de una salida M30 sintética y de una ejecución FULL M00–M31, además de pruebas negativas de namespace desconocido, propiedad inesperada de modelo y procedencia Moira incompleta.

La validación FULL expuso dos divergencias reales que se corrigieron en los productores/schemas propietarios sin reabrir el canonical: M28 añadía trazabilidad doctrinal no declarada y Q6 multiplicaba por 100 una segunda vez el score PX ya expresado en 0–100. El commit de producción Q6 `a91ced8891c79cf992fc666282b9fe2b3bdfb5bc` cerró con `Núcleo Python` y `Contrato público` en SUCCESS para Python 3.10/3.12.

## Registro de ejecución

M02 y M08 pasan de `BACKEND_REQUIRED` a `EXECUTABLE_HANDLER`.

La ejecución real requiere configuración explícita del adaptador y kernel verificado. La ausencia de estos recursos no activa ningún fallback.

## Estado empírico

Esta release mejora reproducibilidad del cálculo astronómico y elimina un bloqueo de software. No constituye validación científica de la astrología, no ejecuta un holdout externo real y no convierte resultados astronómicos o índices en probabilidad metafísica.
