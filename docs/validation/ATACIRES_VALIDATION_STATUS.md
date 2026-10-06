# ALMAS · Estado verificable de la integración Atacires

La capacidad incorporada es experimental en SHADOW y está desactivada por defecto. No certifica nuevas categorías ontológicas ni validez empírica de atacires. La implementación admite ciclos uniformes sobre posiciones canónicas de un mismo sujeto; sus contactos se enlazan como activaciones de extremo de raíces preexistentes o permanecen huérfanos. La salida tiene un estado propio y no cambia el estado operativo previo de M26.

Las referencias analíticas, el snapshot del oráculo, su SHA-256 y la licencia MIT se conservan en `tests/fixtures/atacires/`. La comparación diferencial ejecuta 100 casos sintéticos de semilla 20261006 sin tolerancias ocultas. La suite específica comprueba DST/fold, intervalos, sentidos, vueltas, ramas de aspectos, instantes, orbes, límites, dialectos y datos no finitos; además conserva el payload e IAT previos, valida el bloque en M30 y verifica rollback. El benchmark mide p50/p95/p99 y memoria sobre geometría sintética, sin efemérides ni datos personales.

La robustez compara muestras que el llamante ya haya recalculado con su backend y conserva la regla de muestreo y el umbral explícitos. Una muestra exacta no certifica estabilidad frente a incertidumbre; un conjunto sin contactos queda NOT_EVALUABLE. No se interpreta el número de muestras como probabilidad metafísica.

La matriz de CI incorpora `atacires-core` en Python 3.10/3.12 y conserva los shards históricos. Los recibos remotos contienen SHA de commit, digest del árbol, IDs ejecutados, fallos, omisiones y duración. El estado de un workflow sólo se acredita consultando el run correspondiente; la presencia del YAML no equivale a PASS.

| Gate | Criterio reproducible |
|---|---|
| historical_regression_pass | Unión íntegra de recibos de core/full-pipeline/returns sin errores ni fallos; omisiones opcionales declaradas |
| atacires_golden_pass | Referencias analíticas originales y 100 diferenciales exactos, snapshot íntegro |
| canonical_contract_pass | Schema estricto del bloque y análisis canónico M30; validador público PASS |
| provenance_complete | Huellas de carta/sujeto/entrada/salida, parámetros efectivos, TZif, versión, backend fuente y tiempo operativo |
| structural_invariance_pass | Payload e IAT previo idénticos; análisis canónico sólo añade temporal.atacires_shadow |
| license_gate_pass | MIT conservada y empaquetada; ausencia de nuevas dependencias Swiss/MCP en el núcleo |
| security_gate_pass | Sin llamadas de red; límites; rechazo de ambigüedad y contradicciones; diagnósticos sin datos natales |
| rollback_verified | OFF devuelve exactamente el resultado histórico del handler |

El criterio productivo global permanece NO-GO: no se ha autorizado ni implementado la promoción desde SHADOW. Una PR puede aceptar esta implementación experimental cuando sus verificaciones pasen; esa aceptación no satisface por sí misma una futura promoción ni las tareas 14–16 que el plan R1 declara DEFERRED.

## Revisión independiente del cambio completo

La revisión independiente de a547cde identificó tres hallazgos importantes y ningún hallazgo crítico: nombres de eje canónicos no enlazados, competencia de una señal SHADOW reintroducida con una señal IAT productiva y clasificación ROBUST con una sola muestra no exacta. Los tres escenarios se reprodujeron antes de corregirse. Se reutiliza AXIS_GROUPS, se excluyen las observaciones SHADOW de la selección y de los componentes productivos, y una muestra única no exacta queda NOT_EVALUABLE. Las tres regresiones y el conjunto específico actualizado pasan: 100 pruebas Atacires y 27 pruebas históricas M26 en la comprobación de corrección. La regresión final de este código pasa con 1.300 pruebas, sin errores, fallos ni omisiones. Los cuatro shards comparten commit y digest estable; el acta `ATACIRES_CIERRE_R1.md` y `atacires-local-acceptance.json` conservan el alcance y los recibos de aceptación local.

## Publicación

La revisión automática de aprobación rechazó el intento de publicar la rama, alegando que la autorización de integración local no incluye autorización explícita para divulgar el código y los documentos nuevos en el repositorio público. No se intenta publicar por otro canal. No existe una PR de esta integración ni se atribuye PASS a workflows remotos no ejecutados. El cambio se deja concretado en commits locales revisables y pendiente de esa autorización específica.
