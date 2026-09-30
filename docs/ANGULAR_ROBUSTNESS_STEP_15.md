# Robustez angular — paso 15

El diagnóstico compara las raíces estructurales que contienen contactos angulares con las raíces supervivientes tras recalcular ambas cartas bajo desplazamientos de nacimiento de ±2, ±5, ±10 y ±15 minutos. Exige los dieciséis pares actor/offset; con muestras incompletas devuelve `NOT_EVALUABLE`.

El resultado se clasifica por la retención mínima observada en todas las perturbaciones: `HIGH` ≥ 0,80; `MEDIUM` ≥ 0,50 y < 0,80; `LOW` < 0,50. Los umbrales están congelados en `ALMAS_ANGULAR_ROBUSTNESS_V1` como diagnóstico experimental. No generan score, no se incorporan a IRC y no elevan una fase. Las muestras deben proceder de recálculos previos con las mismas políticas de carta y aspectos; este módulo valida y resume esas muestras, no recalcula efemérides.
