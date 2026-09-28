# Auditoría final de release · ALMAS 1.17.0

**Fecha:** 27 de septiembre de 2026  
**Rama auditada:** `evolution/1.17.0-normative-manifests`  
**Base:** ALMAS 1.16.0  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** formalización normativa de técnica, orbes, dependencia, elegibilidad estructural y loading sin añadir módulos analíticos.

## Alcance

ALMAS 1.17.0 cierra el frente de manifiestos normativos identificado en el roadmap maestro. La release convierte decisiones estructurales ya existentes en 1.16 en políticas empaquetadas, schemas y un manifiesto público verificable por CI.

No se incorporan nuevas técnicas astrológicas, nuevos aspectos, nuevos valores de orbe, nuevos pesos, nuevos discriminadores ni nuevos módulos M00–M31.

## Contratos incorporados

`ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1` centraliza la taxonomía que M15 mantenía hardcodeada. Los siete bindings fuente→módulo→familia técnica/dependencia→elegibilidad se conservan sin cambios.

`ALMAS_DECLARED_ORB_CONTRACT_V1` formaliza la prohibición de orbes implícitos. Cada aspecto declara exclusivamente `angle` y `orb`; el runtime valida rangos y mantiene resolución determinista de solapamientos.

`ALMAS_STRUCTURAL_LOADING_CONTRACT_V1` enlaza `ALMAS_ROOT_STRENGTH_BASELINE_V1`, `ALMAS_ROOT_PILLAR_ATTRIBUTION_V2` y `ALMAS_SEMANTIC_MOTIF_V2` sin introducir una segunda capa de weighting.

`ALMAS_STRUCTURAL_POLICY_MANIFEST_V1` proporciona un punto público único de descubrimiento para estos contratos y congela los invariantes de no cambio analítico.

## Equivalencia funcional

M15 ya no contiene `SOURCE_SPECS` como constante local. En su lugar carga `technique-dependency-registry.json`.

La salida añade `technique_dependency_registry_id` como metadato de procedencia normativa. Permanecen invariantes:

- módulos de origen;
- familias técnicas;
- familias de dependencia;
- `support_only`;
- `core_eligible`;
- direccionalidad;
- `root_key`;
- exactitud;
- deduplicación;
- fuerza de raíz;
- atribución raíz→pilar;
- PX/PS;
- IEM/IDD/IRC;
- ontología.

Los pesos `technique_reliability` continúan en 1.0 para todas las familias registradas.

## Contrato de orbes

`schemas/aspect-policy.schema.json` exige un objeto no vacío cuyos aspectos contienen exactamente `angle` y `orb`.

`schemas/raw-input.schema.json`, `schemas/synastry-output.schema.json` y `schemas/secondary-symbolic-output.schema.json` referencian el mismo contrato.

`match_declared_aspect` valida la política antes del cálculo. No existe inferencia runtime de orbes.

## CI final

El HEAD funcional auditado obtuvo:

- `Contrato público`: SUCCESS;
- `Núcleo Python 3.12`: SUCCESS;
- `Núcleo Python 3.10`: SUCCESS;
- **443 tests deterministas** en Python 3.12;
- **443 tests deterministas** en Python 3.10;
- `ALMAS public contract validation: PASS`;
- paquete raíz: `1.17.0`;
- módulo contractual: `1.17.0`.

## Estado del roadmap

Quedan cerrados:

- manifiestos normativos de técnica/orbes/dependencia/loading;
- generación interna de universos nulos;
- perturbación horaria automática.

Permanecen abiertos como frentes de ejecución pública:

1. backend astronómico/efemérico de producción reproducible;
2. endurecimiento de `canonical-analysis.schema.json`;
3. authoring/rendering DOCX/PDF posterior a M31.

La siguiente dependencia crítica es el backend astronómico: el contrato canónico y la capa material deben poder fijar y serializar identidad, versión y procedencia del backend definitivo.

## Estado empírico

Esta release mejora reproducibilidad y trazabilidad del software. No constituye validación científica de la astrología, no ejecuta un holdout externo real y no convierte índices o rareza en probabilidad metafísica.
