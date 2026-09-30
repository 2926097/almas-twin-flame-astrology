# Capas temporales e IAT — pasos 11 y 12

Las señales M26 conservan el `IAT` global heredado. ALMAS añade cuatro compartimentos de trazabilidad: `IAT_REL`, `IAT_A`, `IAT_B` e `IAT_CROSS`. Sólo se asigna una señal a un compartimento cuando la entrada declara explícitamente `iat_scope`; una señal sin ese dato no se adjudica por inferencia.

Cada señal temporal declara `layer=TEMPORAL`, su `target`, `root_id` si existe, `technique` si se informó y `dependency_cluster`. La raíz y el grupo de dependencia sirven para deduplicar o describir recurrencia; no se cuentan como observaciones independientes nuevas.

Los compartimentos nuevos exponen referencias de señal pero permanecen `NOT_EVALUABLE` y sin valor numérico. No existe aún una política preregistrada de agregación por compartimento. Esta decisión evita dividir el IAT global con pesos improvisados, crear un score prematuro o alterar el contrato 1.21.x/1.22.0.
