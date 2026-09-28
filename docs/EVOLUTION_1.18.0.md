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

## A8 · Gate dorado ejecutado

`ALMAS_ASTRONOMY_GOLDEN_VALIDATION_V1` fue preregistrado antes de observar resultados y conserva los seis casos sintéticos, geometría común, métricas obligatorias, tolerancias en segundos de arco y regla sin promedios compensatorios.

La ejecución real se realizó con el `de440s.bsp` preregistrado y tres referencias independientes: `ALMAS_SKYFIELD_DE440_PLANETARY_REFERENCE_V1`, `ALMAS_SKYFIELD_DE440_TRUE_NODE_REFERENCE_V1` y `ALMAS_SKYFIELD_PLACIDUS_REFERENCE_V1`.

Las cuatro etapas —`PLANETARY_REFERENCE`, `TRUE_NODE_REFERENCE`, `HOUSE_REFERENCE` y `COMPLETE_GATE`— son `PASS` en Python 3.10 y 3.12. El cierre completo valida 47 medidas por caso, 282 por entorno, con cero fallos y resúmenes idénticos entre versiones. El máximo global observado es 39,8903887122″ en ASC/H1 de `G06_CAPE_TOWN_2050`, dentro del límite preregistrado de 60″.

La evidencia consolidada se fija en `validation/astronomy/complete-stage-evidence.v1.json`. Ningún threshold, técnica, peso, score, discriminador u ontología fue alterado como consecuencia de los resultados.

## A9 · Contrato canónico endurecido

`canonical-analysis.schema.json` queda alineado con la superficie real emitida por M30. La raíz declara 22 namespaces y rechaza cualquier namespace no registrado mediante `additionalProperties=false`; 18 campos siempre emitidos son obligatorios y los cuatro namespaces condicionales permanecen explícitamente opcionales.

Se cierran las superficies propias de M30 para modelos AF/KA/AG/LG, índices, IDD por pares, cobertura, robustez, evidencia M17, contraevidencia M20, estado ICE, ensamblaje, perfil y trazabilidad del backend astronómico. Cuando `backend_id=MOIRA_JPL_SPK`, la procedencia completa de `astronomy-backend-provenance.schema.json` es obligatoria.

La composición especializada reutiliza schemas propietarios para doctrina, temporalidad, modelos nulos, sensibilidad horaria, discriminación ontológica, componentes de robustez y el nuevo `semantic-motif-graph.schema.json`. El pipeline FULL se valida con JSON Schema Draft 2020-12 mediante `jsonschema==4.26.0`, además de pruebas negativas para namespaces desconocidos, campos de modelo inesperados y procedencia astronómica incompleta.

Durante esta validación se detectó y corrigió un defecto real de escala en Q6: `PX_PILLAR_SCORE` estaba multiplicándose dos veces por 100. M24 conserva ahora la escala canónica 0–100 y falla cerrado ante valores fuera de rango. El fix de producción `a91ced8891c79cf992fc666282b9fe2b3bdfb5bc` pasó la suite completa y el contrato público en Python 3.10 y 3.12.

La matriz de propiedad namespace→productor→schema queda documentada en `docs/CANONICAL_SCHEMA_AUDIT_1.18.md`. No se añadieron técnicas, pesos, thresholds, scores, discriminadores ni ontología.

## Invariantes

1. El backend no altera scoring ni weighting.
2. El backend no crea evidencia ontológica.
3. El kernel forma parte de la identidad del resultado.
4. No hay descargas ocultas durante cálculo.
5. No hay geocodificación implícita.
6. No hay fallback silencioso de casas.
7. La validación de la dependencia no se confunde con validación científica de la astrología.
