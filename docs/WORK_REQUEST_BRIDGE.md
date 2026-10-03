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


## Preset relacional explícito

El puente admite el preset opt-in `ALMAS_RELATIONAL_ORB_BASELINE_V1`. No es
un default del motor: el panel debe seleccionarlo expresamente mediante:

```json
{
  "analysis_policies": {
    "schema_version": "1.0.0",
    "policy_bundle_id": "ALMAS_RELATIONAL_ORB_BASELINE_V1",
    "preset_ref": "ALMAS_RELATIONAL_ORB_BASELINE_V1"
  }
}
```

La expansión materializa en el `raw_input` todos los valores numéricos, de
modo que M03/M05/M06/M09/M11 siguen recibiendo políticas explícitas. Con
`preset_ref` se prohíben overrides inline para evitar case fitting.

La baseline fija:

- tropical mayor: conjunción 6°, oposición 6°, cuadratura 5°, trígono 5°,
  sextil 4°;
- paralelo/contraparalelo: 1°;
- antiscio/contra-antiscio: 1°;
- consonancia compuesta↔Davison: conjunción 3°;
- natal↔dracónica: conjunción y oposición 3°.

La procedencia epistemológica no es homogénea. Los cinco valores tropicales,
el grado de antiscios y los 3° de consonancia relacional son
`E_PROJECT_POLICY`: son una baseline reproducible, no una tabla doctrinal ni
una validación empírica. El grado de declinación está dentro de la recomendación
metodológica documentada por Astrodienst y la restricción dracónica
conjunción/oposición ≤3° sigue el método contemporáneo documentado y revisado
por María Blaquier. Ninguna de estas fuentes añade score por existir.

El preset conserva `external_validation_status=NOT_PERFORMED` y entra en la
perturbación Q5 de orbes. La estabilidad frente a ±5–10 % de los orbes se
evalúa después; la selección del preset nunca equivale a robustez demostrada.
