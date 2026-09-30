# ALMAS · Paso 12: prerregistro de reglas

`reference/phase-preregistration-1.22.0.json` congela el vocabulario de fases, las reglas operacionales de surrender y awakening, y el registro de secuencias con sus alternativas. El manifiesto incorpora huellas SHA-256; `verify_phase_preregistration` las verifica antes de aceptar el estado `FROZEN_BEFORE_CASE_APPLICATION`.

Quedan fijados los umbrales ya adoptados: ventana mínima de surrender de 30 días y cambio conductual de awakening observado durante 30 días en dos observaciones distintas. La coincidencia de secuencia requiere orden exacto, no infiere estados omitidos y no admite fases extra. La causalidad permanece `UNESTABLISHED`; la ontología después de una coincidencia permanece `INSUFFICIENT`. El artefacto excluye datos y ajuste específico a casos.
