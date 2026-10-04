# Depuración posterior a auditoría · 4 octubre 2026

Base: `main` 38102c82525bd80a09ccf1853e9365fcc90f9e64, versión pública 1.26.0. La revisión es de mantenimiento contractual, distribución, trazabilidad y reporting. Conserva fórmulas, pesos, thresholds, discriminadores y resultados core; VED tiene efecto numérico cero. No se implementa una validación empírica externa ni se promueven ontologías a partir de símbolos.

| Hallazgo | Cambio y control | Alcance de cierre |
|---|---|---|
| H01 · recursos del wheel | Registros doctrinales, políticas congeladas y schema VED empaquetados; `importlib.resources`; paridad byte a byte; wheel cargado fuera del checkout | Corrección técnica y gate aislado |
| H02 · envolvente incompleta | Validación explícita de schema y coherencia en pipeline, attach y reporte; hashes, IDs, referencias, recuentos e intervalos | Rechazo contractual; no certificación astronómica |
| H03 · orbe booleano | Validador común de número finito, tipo y rango | Regresión en sinastría y eventos |
| H04 · documentación desfasada | Censo y snapshots reproducibles; registros de releases separados del estado actual | Actualización del estado y límites de evidencia |
| H05 · detalle VED omitido | Modelo canónico con todas las features, ubicaciones, dependencias, geometría, daśā, tránsitos, sensibilidad y bibliografía; CLI sin recálculo | Texto y JSON; integración automática DOCX/PDF/frontend pendiente |
| H06 · suite completa | Shards disjuntos, duración por test, recibo terminal y matriz Python 3.10/3.12 | Resultado sólo con recibos completos; caída nativa documentada |
| H07 · corpus | Identidad y pasaje seleccionado de 19 PDF, OCR de cuatro escaneados, 18 familias de obra, seis gaps de localizador | Revisión parcial declarada; no lectura doctrinal íntegra ni promoción automática al router |
| H08 · limitaciones | IVED nulo, Aṣṭakūṭa no evaluable, dependencia no demostrada, eficacia externa no ensayada | Limitaciones preservadas, no tratadas como funciones implementadas |

## Informe y fronteras

`build_vedic_report_model` parte únicamente de la envolvente ya calculada y conserva rutas al dato y cobertura de entrada/salida. Cada ficha distingue geometría A, regla simbólica B, laguna de doctrina C, uso D no documentado e hipótesis relacional E. Las posibilidades de semejanza, complementariedad o espejo no se distinguen automáticamente ni prueban llamas gemelas. D9 y Arudhas por signo no reciben longitudes físicas inventadas. Los campos no disponibles se mantienen ausentes. La recurrencia se agrupa por dependencia y no se contabiliza como observaciones independientes.

La validación VED ahora requiere el extra `schema-validation`; su ausencia es un error explícito, también con VED desactivado. Los comandos de carta precomputada siguen disponibles sin backend astronómico. El validador no recalcula una carta recibida ni autentica recibos externos de retorno anual.

## Verificación

El repositorio base terminó 1.153 tests en 759,220 s, sin errores. Los nueve controles nuevos de depuración pasan, al igual que las 44 pruebas VED, el contrato público, el ejemplo VED con eventos/sensibilidad y el wheel aislado. La primera ejecución completa con instrumentación periódica de traceback terminó con código 139 durante una integración SSAR; no emitió recibo y no se contó como PASS. La causa nativa no se atribuye al código de aplicación sin evidencia. El traceback periódico queda optativo; la captura de fallos permanece activa. Se repite la batería completa para obtener evidencia terminal, con estados y tiempos en los recibos de CI.

Los gates de núcleo, distribución, contrato, astronomía y publicación constituyen verificaciones distintas. Un PASS técnico no valida eficacia científica ni probabilidades metafísicas. La matriz remota debe evaluarse sobre el SHA de esta rama. `external_validation=NOT_PERFORMED`, origen `INSUFFICIENT`, IVED nulo y efecto VED cero permanecen vigentes.
