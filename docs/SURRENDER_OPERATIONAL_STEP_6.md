# ALMAS · Paso 6: surrender como criterio conductual

La política congelada en `reference/surrender-operational-policy.json` define surrender solo como hipótesis operacional del proyecto. No atribuye motivos privados ni acredita una categoría metafísica. La ventana de 30 días es una convención preregistrada, no un umbral psicológico validado externamente.

La evaluación se hace por actor y usa tres componentes: cese de persecución, afirmación de límites y descentramiento conductual. El primero requiere una línea base de dos intentos previos, oportunidad documentada, registro completo y ausencia de nuevos intentos durante la ventana. El segundo requiere evidencia directa de un límite. El tercero requiere actividades del actor en dos dominios distintos durante al menos 30 días, independientes de la respuesta de la otra persona.

Dos componentes apoyados, incluido un límite o el descentramiento, producen `COMPATIBLE` en el candidato. `SUPPORTED` para `surrender_stabilized` requiere los tres componentes, una ventana de 30 días, referencia de preregistro y ninguna contraevidencia. Persecución posterior, reapertura reiterada de conflicto, negociación del resultado o intentos de control contradicen la hipótesis. La intención estratégica asociada a silencio solo se registra con autoinforme explícito del actor. Silencio, dolor, ruptura, ausencia de contacto, bloqueo o una declaración verbal aislada no bastan.

Los schemas de entrada y salida son cerrados y `tests/test_surrender_assessment.py` utiliza exclusivamente datos sintéticos. El evaluador devuelve referencias documentales y nunca convierte falta de evidencia en evidencia afirmativa.
