# ALMAS · Auditoría transversal de preparación externa (30-10-2026)

**Propósito:** localizar contradicciones entre los cuatro manifiestos existentes sin crear una segunda política de selección, scoring o inferencia. El nuevo preflight es exclusivamente `SHADOW_READ_ONLY`, no accede a holdouts privados ni autoriza el comienzo de una ejecución confirmatoria.

**Comando:** `python scripts/report_external_validation_readiness.py`. Imprime un informe JSON agregado por stdout; no escribe archivos. `NOT_READY` significa que los cuatro manifiestos públicos son internamente coherentes pero carecen de cohortes admitidas. `REVIEW_REQUIRED` aparece cuando se declaran filas nuevas: la presencia de una fila o referencia no acredita consentimiento, procedencia independiente, potencia, cegamiento o preregistro; el resultado sigue bloqueado. `CONTRACT_VIOLATION` (salida 2) señala una contradicción de estados, cambios de gate o estructura. Ningún resultado de esta herramienta es `READY`.

| Fuente existente | Campo observado en este corte | Estado verificable |
|---|---|---|
| `manifests/validation-cohort-manifest.json` | `real_cases=[]` | Infraestructura C1–C6; no holdout poblado |
| `manifests/pair-identity-validation-manifest.json` | `real_cohorts=[]` | `INFRASTRUCTURE_ONLY_NO_EMPIRICAL_HOLDOUT`; objetivos 40/120/120 no son casos reclutados |
| `validation/holdouts/manifest.json` | `artifacts=[]` | No existe un artefacto público admitido |
| `validation/returns/external-validation-readiness.json` | `real_cases=[]`; 7 `blockers` | `DRAFT_NOT_PREREGISTERED`, `NOT_PERFORMED`, sin apertura del holdout |

El preflight **no verifica externamente** la integridad o validez de los datos declarados en los manifiestos. La coherencia de sus indicadores no prueba independencia de cohortes, intercambiabilidad de modelos nulos, no contaminación de resultados ni definición adecuada del endpoint. Tampoco genera probabilidades, p-valores, nuevos índices, cambios de elegibilidad o promoción L3.

Las siete obligaciones RRA registradas en `docs/RRA_EXTERNAL_EXECUTION_DOSSIER.md` siguen siendo el contrato material de preparación. El protocolo general `docs/EXTERNAL_VALIDATION_PROTOCOL.md` y el de identidad diádica `docs/PAIR_IDENTITY_BLIND_VALIDATION_PROTOCOL.md` deben mantenerse separados en endpoints: cronología observada y díada declarada no son la misma variable de respuesta.

**Gates reales previos a una validación:** (i) criterio observable y plan analítico preregistrados; (ii) cohorte pública elegible o custodia privada conforme a `ALMAS_PUBLIC_DATA_ISOLATION_V1`; (iii) partición independiente por personas, sin reutilizar desarrollo/piloto; (iv) cegamiento y doble codificación cuando corresponda; (v) periodos de observación y controles negativos justificados; (vi) potencia/precisión, intercambiabilidad y multiplicidad; (vii) evaluación sobre holdout sellado con resultado y limitaciones, seguida de replicación independiente si se pretende promover un método. Ninguno de estos gates se completa mediante este preflight.

La CI ejecuta los tests adversariales mediante discovery en el shard `core`. La incorporación de este script no modifica `VALIDATION_STATUS.md`, M00–M31, políticas congeladas, registries de promoción, schemas, índices ni algoritmos productivos. Se conserva `NO-GO` hasta aportar la evidencia externa indicada en [issue #120](https://github.com/2926097/almas-twin-flame-astrology/issues/120).
