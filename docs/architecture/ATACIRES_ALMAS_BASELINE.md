# ALMAS · Línea base Atacires

Base ALMAS: `c938e0d0032f6940eebb0e26373c051e473eeb81`. Snapshot Atacires: `d0d3a4bcf315708a4bf6f7e40cf2873732819b61`. Python local: 3.12.14. Matriz remota prevista: 3.10 y 3.12. Descubrimiento histórico: 1.200 pruebas. El núcleo fuente y sus referencias analíticas están congelados en `tests/fixtures/atacires/source-manifest.json`.

La suite local requiere instalar ALMAS y el extra `schema-validation`; invocar scripts sin instalar el paquete hace que los subprocess de CLI no puedan importar `almas_tfa`. Ese problema de preparación del entorno no debe atribuirse a la integración. Se conserva el resultado de las ejecuciones y se repiten las verificaciones afectadas después de instalar el paquete.

Comandos verificables: `python scripts/run_test_shard.py --shard all --receipt /tmp/almas-all.json` para la regresión íntegra; los shards `core`, `atacires-core`, `full-pipeline` y `returns` deben cubrir la misma unión sin duplicados. `python scripts/validate_public_contract.py` y `python scripts/validate_distribution.py` comprueban contrato y wheel aislada. `python benchmarks/atacires_benchmark.py` mide el recorrido OFF y el núcleo sintético.

Feature OFF equivale a `ALMAS_TEMPORAL_ATACIRES_ENABLED=false` o variable ausente. No añade bloque sombra. Feature ON usa exactamente `true` y añade un bloque sin scoring. Un valor distinto provoca error de configuración explícito. Las pruebas de igualdad de ModuleResult, ensamblado canónico e IAT existente fijan el rollback semántico.
