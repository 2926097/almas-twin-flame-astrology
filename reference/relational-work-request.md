# Adaptador de solicitudes relacionales del panel

## Finalidad

`ALMAS_WORK_REQUEST` es una envolvente de interfaz y no sustituye a
`schemas/raw-input.schema.json`. El adaptador
`ALMAS_RELATIONAL_WORK_REQUEST_ADAPTER_V1` transforma una solicitud
`REQUEST_ONLY` en el `raw_input` que consume M00-M31.

La adaptación no calcula astrología, no crea evidencia, no modifica scoring y
no convierte una solicitud en `canonical_analysis`.

## Regla central

El adaptador distingue entre dos clases de configuración.

Las convenciones que ya están fijadas por la implementación se materializan de
forma determinista:

- compuesta: `SHORTEST_ARC` con oposición exacta
  `NOT_EVALUABLE`;
- Davison: midpoint temporal `UTC_INSTANT` y midpoint geográfico
  `SPHERICAL_GREAT_CIRCLE`;
- dracónica: `NORTH_NODE_TO_ZERO`, con ángulos y casas cuando estén
  disponibles.

En cambio, los orbes permanecen declarativos. Para los perfiles relacionales
que ejecutan el núcleo estructural deben aportarse explícitamente:

- `aspect_policy`;
- `declination_policy`;
- `antiscia_policy`;
- `relationship_chart_consonance_policy.aspect_policy`;
- `draconic_aspect_policy`.

La declaración admite dos vías mutuamente excluyentes. La primera es
`analysis_policies`, con las políticas completas inline. La segunda es
`analysis_policy_profile`, que referencia un preset versionado del registro
`ALMAS_RELATIONAL_POLICY_PRESET_REGISTRY_V1`. Elegir un preset es una
decisión explícita de entrada: no constituye un default implícito. Si se
declaran a la vez un preset y overrides inline de las familias de orbe, el
adaptador rechaza la solicitud.

No se copian valores desde fixtures, ejemplos, casos privados o lecturas
anteriores. La ausencia de estas políticas bloquea la preparación ejecutable en
lugar de producir un análisis parcialmente configurado sin advertencia.

## Flujo

`ALMAS_WORK_REQUEST → assess_relational_work_request → prepare_relational_raw_input → Orchestrator`

`assess_relational_work_request()` permite al frontend mostrar qué políticas
faltan sin ejecutar el motor.

`prepare_relational_raw_input()` funciona fail-closed por defecto. Sólo con
`require_complete=False` puede producir una vista previa incompleta; esa vista
conserva `missing_declared_policies` y no inventa orbes.

## Trazabilidad

El raw input adaptado incorpora `request_adapter_trace` con:

- identificador del adaptador;
- versión pública;
- perfil;
- políticas fijas materializadas;
- políticas declaradas recibidas;
- políticas declaradas ausentes;
- `implicit_orbs_used=false`;
- `case_fitting_used=false`.

Este bloque es metadato de procedencia y no aporta peso analítico.

## Límite epistemológico

Una solicitud preparada sigue siendo sólo entrada. El resultado canónico existe
únicamente después de ejecutar el pipeline con el backend astronómico requerido.
El adaptador no autoriza a reconstruir posiciones, raíces, pilares, IEM, IDD,
IRC, ICC, ICE o IAT fuera del motor.
