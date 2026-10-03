# Puente ALMAS_WORK_REQUEST → raw_input

## Finalidad

El panel puede capturar datos de caso en una envolvente `ALMAS_WORK_REQUEST`,
pero el orquestador M00–M31 consume el contrato técnico de
`schemas/raw-input.schema.json`. El puente
`src/almas_tfa/work_request.py` separa ambas superficies y evita que una
solicitud de interfaz se confunda con una ejecución canónica.

El puente no calcula astrología. Tampoco convierte `REQUEST_ONLY` en un
resultado ni crea `canonical_analysis`.

## Regla de versión

`request.public_version` debe coincidir exactamente con la versión instalada
del paquete. Una discrepancia falla cerrado antes de cualquier cálculo.

## Perfiles

El adaptador resuelve `analysis_profile` mediante
`ALMAS_ANALYSIS_PROFILES_V1`. La revisión 1.0.0 del puente sólo declara
`execution_ready=true` para `FULL_ASTROLOGY`, porque es el único perfil cuya
frontera de entrada está completamente modelada aquí. `TEMPORAL`,
`SOUL_CONTRACT` y `FULL_MULTIDISCIPLINARY` fallan cerrado hasta disponer de
sus contratos de entrada completos.

Para `FULL_ASTROLOGY`, las políticas estructurales relevantes son M03, M05,
M06, M07, M08, M09, M10 y M11.

## Convenciones que pueden completarse automáticamente

Sólo se completan convenciones ya fijadas por la implementación de producción y
que no contienen valores de orbe:

- `composite_policy.midpoint_mode=SHORTEST_ARC`;
- `composite_policy.opposition_tie_break=NOT_EVALUABLE`;
- `davison_policy.time_midpoint=UTC_INSTANT`;
- `davison_policy.geographic_midpoint=SPHERICAL_GREAT_CIRCLE`;
- `draconic_policy.node_id=NORTH_NODE`;
- `draconic_policy.transform=NORTH_NODE_TO_ZERO`;
- `draconic_policy.include_angles=true`;
- `draconic_policy.include_houses=true`.

Estas convenciones derivan del contrato ejecutable vigente. No se ajustan al
caso.

## Políticas que no pueden inventarse

ALMAS mantiene `ALMAS_DECLARED_ORB_CONTRACT_V1`: no existen orbes
implícitos. Por ello el panel debe enviar un `analysis_policies` versionado
con `policy_bundle_id` y, cuando el perfil los requiera, declarar
explícitamente:

- `aspect_policy`;
- `declination_policy`;
- `antiscia_policy`;
- `relationship_chart_consonance_policy.aspect_policy`;
- `draconic_aspect_policy`.

Los valores usados en fixtures sintéticos no son defaults de producción.

## Estados del puente

`assess_work_request(...)` devuelve un diagnóstico sin ejecutar astronomía:

- `execution_ready=true` sólo cuando las políticas requeridas están presentes
  y superan validación básica;
- `missing_policies` enumera contratos ausentes;
- `policy_errors` conserva errores de versión, cabecera o valores;
- `implicit_orbs_used=false`;
- `case_fitting_used=false`.

`build_raw_input_from_work_request(...)` falla cerrado por defecto si
`execution_ready=false`. Puede usarse con
`require_execution_ready=false` únicamente para inspección o depuración; esa
salida no debe lanzarse como análisis FULL.

## Frontera con el backend astronómico

Superar el puente no implica que M02/M08 sean ejecutables. La ejecución real
sigue requiriendo el backend de producción configurado:

`MoiraProductionBackend + moira-astro 6.8.2 + kernel JPL local fingerprintado`.

El puente valida la solicitud. El backend produce astronomía. M30 ensambla y
valida la salida canónica. Ninguna de esas capas sustituye a las demás.

## Privacidad

Las pruebas del puente utilizan exclusivamente sujetos sintéticos. No deben
incorporarse casos privados a `tests/` ni a `examples/`.
