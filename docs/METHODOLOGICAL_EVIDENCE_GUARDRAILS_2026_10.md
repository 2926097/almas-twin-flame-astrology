# ALMAS · Cortafuegos metodológico experimental (30-10-2026)

**Base auditada:** `ca01a5483dfaa76bfee34e338f6b3cfba4be45e6` (`main`, 30-10-2026).

**Alcance:** `SHADOW_READ_ONLY`. No modifica orquestador M00–M31, schemas, score, índices IEM/IDD/IRC/IAT/ICC/ICE, ontología, pesos, política congelada, backend astronómico ni contratos de promoción. No utiliza datos personales.

## Qué existe y qué comprueba

`M22` entrega la batería AB0–AB8 de supervivencia estructural y explícitamente no asigna clases contractuales. La nueva auditoría exige nueve corridas únicas, partición completa de las raíces de AB0 y fracciones consistentes; **no** confunde supervivencia estructural con utilidad predictiva.

`M23` entrega sensibilidad temporal. Se comprueba el contrato `robustness_component_eligible` frente a `robustness_component`; un componente no acredita por sí mismo la fiabilidad documental de la hora ni validez externa.

`M24` entrega corridas nulas preregistradas y `structural_frequency`, no valores p confirmatorios. Se comprueban IDs, referencias de congelación, conteos y frecuencias; no se calcula `p` ni se presume intercambiabilidad. Antes de cualquier test inferencial se requieren estadístico y cola preregistrados, población objetivo, generador nulo válido, control de dependencias y multiplicidad, cohorte independiente y protocolo de reproducibilidad.

`M21` puede entregar Shapley por raíces independientes. Se comprueba que los motivos derivados no figuren como jugadores y se comunica el máximo residuo de eficiencia, sin reinterpretarlo como importancia causal.

La verificación **computacional** exige un recibo completo de CI vinculado al SHA exacto. La **validación estadística** necesita controles metodológicamente válidos. La **validación empírica** exige variables observables independientes, holdout predefinido y resultados fuera de muestra. La **hipótesis metafísica** permanece `NOT_EVALUABLE` por estas técnicas. No hay promoción automática entre niveles. Los estados epistemológicos originales permanecen inalterados.

## Ejecución

- Tests sintéticos: `python -m unittest discover -s tests -p 'test_methodological_evidence_audit.py' -v`.
- Diagnóstico local: `python scripts/audit_methodological_evidence.py /ruta/privada/canonical_analysis.json`.

El diagnóstico sólo genera agregados por stdout, sin copiar la entrada ni crear puntuaciones relacionales. La ausencia de estructuras produce `NOT_EVALUABLE` y nunca se interpreta como contraevidencia. Un incumplimiento de invariantes devuelve código 2.

## Criterio de integración y limitaciones

Fusionar únicamente si las pruebas nuevas pasan en Python 3.10/3.12, la suite histórica no presenta regresiones atribuibles al cambio, los workflows relevantes culminan en `success` sobre el SHA exacto de la PR y el diff confirma invariancia productiva.

**No ejecutado aquí:** cohorte externa, preregistro de hipótesis externas, test de intercambiabilidad, inferencia confirmatoria, calibración predictiva, validación de constructo o discriminación ontológica. La CI verde no modificaría esos estados. El informe metodológico original sólo sirve de contexto; ninguna publicación reciente se usa como justificación de un resultado empírico de ALMAS.
