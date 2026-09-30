# Baseline previo al motor de fases dinámicas

Fecha de congelación: 29 de septiembre de 2026. Esta es la ejecución del paso 1 del plan de fases y polaridades; no activa el motor de fases ni modifica el núcleo cuantitativo.

## Identidad de las referencias

El documento de arranque presupone que la versión actual es 1.21.x. La rama `main` ya publica 1.22.0 en `VERSION` y `pyproject.toml` y tiene el commit `3899add29d20e09574e9eb7c2336d2d923063d7b`. Su auditoría de release está en `docs/RELEASE_AUDIT_1.22.0.md`. El cierre funcional 1.21.0 fue `4cd6e3980b9d8c72fc1a545ffea59efeed196a9d`; la referencia cuantitativa 1.21.0 utilizada por esa auditoría fue `88623bbec1bcb9e8d7fd621235e6c7ee6996094b` (Paso 3A). Esas referencias no son intercambiables: 1.22.0 incorporó Shapley V3, agrupación por dependencia de IRC e ICE autónomo con completitud explícita.

Para el desarrollo siguiente se congela el **comportamiento vigente de 1.22.0** como contrato de regresión y se conserva el commit cuantitativo 1.21.0 como comparación histórica. Ningún resultado anterior a 1.22.0 puede sustituir silenciosamente una expectativa actual. Los nombres de referencia `baseline/quantitative-1.21.0` y `baseline/dynamic-phase-1.22.0` están creados como tags anotados en el checkout de trabajo; sus SHAs de destino anteriores identifican las referencias incluso si los tags aún no se han publicado en GitHub.

## Superficie inspeccionada y congelada

El fixture `tests/fixtures/dynamic_phase_quantitative_baseline_1.22.0.json` contiene resultados de seis raíces **sintéticas**, sin datos de personas reales. `tests/test_dynamic_phase_baseline_regression.py` vuelve a ejecutar el código de producción y compara: PA, PK, PE, PR, PX, PT, PS y PU; recurrencia y raíces por pilar; jugadores y cuotas Shapley; IEM_pre, IEM_final y gate de AF/KA/AG/LG; IDD; IAT con política de pesos prerregistrada; ICC; IRC agrupado y R_min; ICE autónomo deduplicado y ausencia de pilar esencial. Las tolerancias numéricas se limitan a diez decimales; claves, estados y decisiones son exactos.

Las definiciones normativas permanecen en `src/almas_tfa/core.py`, `src/almas_tfa/data/model-attribution-policy.json`, `manifests/quantitative-policy-manifest.json`, `src/almas_tfa/pillar_attribution.py`, `src/almas_tfa/temporal_handlers.py`, `src/almas_tfa/canonical_assembly.py`, `src/almas_tfa/robustness_index_handlers.py` y `src/almas_tfa/counterevidence_handlers.py`. Las pruebas existentes cubren perturbaciones, deduplicación, missingness, modelos nulos, autoría y contrato público. El nuevo fixture añade una comparación transversal concreta antes de introducir estados dinámicos.

El fixture congela una muestra controlada del comportamiento, no todos los valores posibles ni una validación empírica. No se han recalibrado pesos, thresholds, fórmulas, ontología ni índices. Las señales temporales sintéticas prueban solamente el cálculo de IAT y la prohibición de crear raíces; no predicen hechos ni estados subjetivos. El ICE del fixture presupone de forma explícita una evaluación completa; un conjunto incompleto sigue sin producir ICE autónomo.

## Regla para cambios posteriores

Cualquier desviación de este snapshot exigirá identificar el campo afectado, el motivo técnico, la diferencia respecto de 1.21.0 y 1.22.0 y una aprobación metodológica documentada en el cambio. No se actualizará el fixture sólo para hacer pasar una prueba. Los casos José–Indira no intervienen en estos criterios. El siguiente paso permitido es diseñar el modelo de estados A/B/relación, sin inferencia automática.
