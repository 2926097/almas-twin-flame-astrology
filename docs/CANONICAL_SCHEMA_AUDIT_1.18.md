# Auditoría del contrato canonical_analysis · ALMAS 1.18

## Objeto

Esta matriz fija la procedencia de la superficie producida por M30 antes del endurecimiento final de `canonical-analysis.schema.json`. No añade módulos, técnicas, pesos, scores ni inferencias. La autoridad de producción es `src/almas_tfa/canonical_assembly.py`.

## Superficie de raíz

| Namespace | Productor canónico | Fuente principal | Contrato |
|---|---|---|---|
| `schema_version` | M30 | ensamblador | const 1.0.0 |
| `analysis_mode` | M30 | política de perfiles | enum actual FULL/TEMPORAL |
| `analysis_profile` | M30 | `ALMAS_ANALYSIS_PROFILES_V1` | enum de cuatro perfiles |
| `profile_policy_id` | M30 | `ALMAS_ANALYSIS_PROFILES_V1` | const |
| `astronomy_backend` | M30 | M02 `natal.backend` | wrapper canónico; Moira exige `astronomy-backend-provenance.schema.json` |
| `evidence` | M30 | M17 `independent_roots` | proyección de ocho campos |
| `models` | M30 | M18/M19/M20/M25 | AF/KA/AG/LG; once campos por modelo |
| `indices` | M30 | M20/M21/M25/M26 + coverage | IDD/IAT/ICC/IRC/ICE |
| `pairwise_idd` | M30 | M21 | mapa de par → idd/band |
| `coverage` | M30 | estado M02–M14 | siete dominios q∈{0,0.5,1} |
| `robustness` | M30 | M25 | proyección de siete campos; componentes reutilizan schema M25 |
| `counterevidence` | M30 | M20 | proyección normalizada de contradicciones |
| `counterevidence_state` | M30 | M20 | estado ICE + contradicciones esenciales |
| `ontology` | M30 | ensamblador | placeholder vacío; la discriminación vive separada |
| `doctrine` | M30 | M28 | array de `doctrinal-claim.schema.json` |
| `temporal` | M30 | M26/M27 | wrapper `activation` / `events` |
| `limitations` | M30 | resultados M01–M29 | lista de strings trazables por módulo |
| `assembly` | M30 | ensamblador/perfil | metadata cerrada y no recalculadora |
| `semantic_motifs` | M30 opcional | M18 | `semantic-motif-graph.schema.json` |
| `ontological_discrimination` | M30 opcional | M21 | `ontological-discriminator-output.schema.json` |
| `null_models` | M30 opcional | M24 | `null-model-output.schema.json` |
| `time_sensitivity` | M30 opcional | M23 | `time-sensitivity-output.schema.json` |

## Campos siempre emitidos

M30 emite siempre todos los namespaces de la tabla salvo `semantic_motifs`, `ontological_discrimination`, `null_models` y `time_sensitivity`. Estos cuatro dependen de la existencia de sus namespaces fuente.

La raíz de `canonical-analysis.schema.json` debe permanecer cerrada mediante `additionalProperties=false`. Una ampliación futura requiere cambio explícito de contrato y actualización del validador público.

## Composición especializada

La composición directa ya exigida es:

- `doctrine[*]` → `doctrinal-claim.schema.json`;
- `temporal.activation` → `temporal-activation-output.schema.json`;
- `temporal.events` → `documentary-event-output.schema.json`;
- `time_sensitivity` → `time-sensitivity-output.schema.json`;
- `null_models` → `null-model-output.schema.json`;
- `ontological_discrimination` → `ontological-discriminator-output.schema.json`;
- `robustness.components[*]` → item de `robustness-output.schema.json`;
- `astronomy_backend.provenance`, cuando `backend_id=MOIRA_JPL_SPK`, → `astronomy-backend-provenance.schema.json`.

## Estado de endurecimiento

Cerrados en esta fase:

- superficie raíz;
- modelos;
- índices;
- cobertura;
- robustez;
- metadata de ensamblaje;
- perfil embebido;
- evidencia M17;
- contraevidencia M20;
- estado de contraevidencia;
- wrapper temporal;
- placeholder ontológico;
- trazabilidad del backend astronómico.

Pendiente fuera de la superficie propia de M30:

- cualquier apertura o desajuste heredado dentro de schemas especializados externos debe corregirse en el schema propietario y no mediante duplicación dentro de `canonical-analysis.schema.json`;
- la aceptación final depende de que la salida FULL M00–M31 valide todos los `$ref` especializados en Python 3.10 y 3.12.

## Gate de aceptación

El cierre de este frente requiere:

1. salida positiva de M30 validada con Draft 2020-12;
2. salida FULL M00–M31 validada con el mismo contrato;
3. rechazo de namespace raíz desconocido;
4. rechazo de campo de modelo inesperado;
5. rechazo de procedencia Moira incompleta;
6. Python 3.10 y 3.12 en verde;
7. contrato público en verde.

