# ALMAS 1.17.0 · Normative Structural Manifests

## Objetivo

ALMAS 1.17.0 cierra el frente pendiente de manifiestos normativos específicos
para técnica, orbes, dependencia, elegibilidad estructural y loading.

La release no añade técnicas, familias, aspectos, pesos ni módulos analíticos.
Su finalidad es convertir decisiones que ya existían en 1.16 en contratos
versionados, descubribles y verificables por CI.

## N1 · Registro técnica/dependencia

`ALMAS_TECHNIQUE_DEPENDENCY_REGISTRY_V1` centraliza los bindings que M15
mantenía hasta 1.16 como una tabla Python local.

Para cada fuente canónica congela:

- módulo de origen;
- `technique_family`;
- `dependency_family`;
- `support_only`;
- `core_eligible`;
- direccionalidad.

La migración conserva exactamente los siete bindings previos:

- M03 · SYN;
- M05 · DECLINATION;
- M06 · ANTISCIA;
- M09 · RELCHART;
- M11 · NATAL_DRACONIC;
- M12 · DRACONIC_DD;
- M14 · SECONDARY.

M12 y M14 continúan `support_only=true` y `core_eligible=false`.

## N2 · Contrato de orbes declarados

`ALMAS_DECLARED_ORB_CONTRACT_V1` formaliza la regla ya existente de que no
hay orbes implícitos.

Cada aspecto debe declarar exclusivamente:

- `angle`;
- `orb`.

El contrato exige `angle ∈ [0,180]`, `orb >= 0` y conserva la resolución
determinista de solapamientos: menor orbe absoluto y, en empate, nombre
lexicográfico del aspecto.

La exactitud conserva la fórmula:

`F = max(0, 1 - (orb / orb_limit)^2)`.

El caso `orb_limit=0` sólo admite coincidencia exacta.

El schema `aspect-policy.schema.json` se referencia desde la entrada bruta,
la salida de sinastría y la salida secundaria simbólica. El mismo validador
runtime es consumido por `match_declared_aspect`, por lo que los módulos que
utilizan esa función comparten el contrato.

## N3 · Loading estructural

`ALMAS_STRUCTURAL_LOADING_CONTRACT_V1` no crea una nueva capa de scoring.
Enlaza explícitamente:

- `ALMAS_ROOT_STRENGTH_BASELINE_V1`;
- `ALMAS_ROOT_PILLAR_ATTRIBUTION_V2`;
- `ALMAS_SEMANTIC_MOTIF_V2`.

Mantiene:

- pesos de técnica neutrales en 1.0;
- coeficientes de aspecto neutrales en 1.0;
- incertidumbre horaria delegada a M23–M25;
- `support_only` incapaz de crear núcleo;
- rareza nula fuera del loading;
- activación temporal fuera del loading;
- PU no atribuible sin discriminador validado.

## N4 · Manifiesto público

`ALMAS_STRUCTURAL_POLICY_MANIFEST_V1` es el punto único de descubrimiento
público de los contratos anteriores y de las políticas de root strength y
root→pillar.

El manifiesto fija además que 1.17:

- no añade módulo analítico;
- no cambia scores;
- no introduce orbes implícitos;
- no permite case fitting runtime;
- mantiene la deduplicación M16 antes de la construcción de raíces M17;
- conserva la robustez horaria en M23–M25.

## Cambios de ejecución

M15 deja de leer una constante `SOURCE_SPECS` embebida en código y carga el
registro canónico empaquetado. La salida `evidence_graph` añade únicamente
`technique_dependency_registry_id` como procedencia normativa.

No cambia:

- `root_key`;
- exactitud;
- deduplicación;
- fuerza de raíz;
- pillar loading;
- PX/PS;
- IEM/IDD/IRC;
- ontología;
- V1–V5.

## Estado del roadmap

Con 1.17, el frente de manifiestos normativos queda cerrado.

El generador de nulls y la perturbación horaria ya estaban ejecutables desde
1.13, por lo que ese frente también se considera cerrado.

Permanecen como frentes principales:

1. backend astronómico/efemérico de producción reproducible;
2. endurecimiento de `canonical-analysis.schema.json`;
3. authoring/rendering DOCX/PDF posterior a M31.

La secuencia recomendada es backend astronómico → contrato canónico estricto →
capa material de publicación, porque los dos últimos deben poder fijar y
serializar metadatos reales del backend definitivo.
