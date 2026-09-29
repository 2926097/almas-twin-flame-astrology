# ALMAS · Paso 7: awakening como hipótesis biográfica

La política de `reference/awakening-operational-policy.json` impide que la astrología establezca awakening. La evaluación es por actor y solo acepta cinco criterios biográficos con evidencia: reformulación explícita, reconocimiento de un patrón previo, cambio conductual sostenido, reenganche voluntario y mayor congruencia documentada entre palabras y actos.

Para que el cambio conductual cuente como sostenido, esta convención del proyecto requiere al menos dos observaciones del actor separadas por 30 días. Si falta ese intervalo o las observaciones pertenecen a la otra persona, el criterio queda `NOT_EVALUABLE`. Los cinco criterios deben quedar apoyados para que la salida sea `SUPPORTED`; contradicción o contraevidencia impiden ese estado. La salida no demuestra awakening espiritual ni tipología twin-flame, y la congruencia no es un diagnóstico de sinceridad.

La entrada cerrada no admite tránsitos ni interpretaciones astrológicas. Las pruebas de `tests/test_awakening_assessment.py` usan registros sintéticos y verifican los cinco criterios, el intervalo, las referencias documentales y el bloqueo ante contraevidencia.
