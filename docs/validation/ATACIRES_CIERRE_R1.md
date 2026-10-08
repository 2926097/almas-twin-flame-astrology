# ALMAS · Acta de cierre local de Atacires R1

El núcleo experimental de ciclos uniformes queda implementado, depurado y aceptado localmente en la rama `feat/atacires-temporal-integration`. La aceptación se limita al modo SHADOW, desactivado por defecto. La promoción a producción permanece NO-GO. No se modifican pesos, ontología ni índices productivos; M30 incorpora el bloque opcional `temporal.atacires_shadow`.

## Decisiones de alcance

El plan original se depuró antes de ejecutar y se consolidó en cuatro tareas R1. Se fijaron cuatro decisiones: las observaciones SHADOW quedan fuera del IAT y sus componentes; M26 conserva su payload y estado históricos y expone el diagnóstico en un espacio separado; los contactos corresponden a una única carta natal canónica y activan extremos de raíces preexistentes, conservando los huérfanos; las tareas originales 14–16 quedan DEFERRED hasta satisfacer sus contratos y gates. Para publicar el namespace cuando M26 base sea NOT_EVALUABLE, el orquestador admite únicamente el sidecar `atacires_shadow` con `mode=SHADOW`, `scoring_enabled=false` y señales no elegibles, sin cambiar el estado operativo original de M26. La segunda técnica, la migración MCP y un nuevo proveedor Swiss no se presentan como implementados. ALMAS conserva la autoridad de sus motores históricos y consume posiciones natales ya calculadas.

## Revisión y corrección

La revisión independiente encontró tres defectos importantes y ninguno crítico. Se reprodujeron y corrigieron el enlace de nombres canónicos ASC/MC/nodos, la interferencia de una observación SHADOW reintroducida con la selección productiva del IAT y la clasificación ROBUST injustificada con una única muestra no exacta. Las regresiones específicas se observaron fallar antes de corregirse y pasar después.

## Evidencia de aceptación

El código verificado corresponde al commit `35eebe41f67687ff11b1bfdfaa6b67de55056da6`, con Python 3.12.14 y digest del árbol `7b3d5fba307029e4b555e813f56910599aa648195f54184007ed7637f9317e45`. Los cuatro recibos declaran el árbol sin cambios durante su ejecución. Su unión es exhaustiva y disjunta: 1.300 pruebas, cero fallos, cero errores y cero omisiones. Los commits posteriores de cierre sólo añaden documentación y evidencia.

| Shard | Pruebas | Duración | Resultado |
|---|---:|---:|---|
| core | 1.198 | 544,58 s | PASS |
| atacires-core | 100 | 0,43 s | PASS |
| full-pipeline | 1 | 41,22 s | PASS |
| returns | 1 | 83,38 s | PASS |

Los IDs ejecutados, la identidad del árbol y las huellas SHA-256 de los recibos originales se conservan en `atacires-local-acceptance.json`. La suite específica incluye las 55 pruebas originales y una comparación diferencial de 100 casos sintéticos; esos casos diferenciales son parte de las pruebas y no se suman de nuevo al total. El snapshot del motor, sus referencias analíticas y su licencia MIT quedan conservados. La distribución wheel se comprobó en un entorno aislado, incluyendo la licencia empaquetada. El validador público de contratos, el catálogo de fuentes y el corpus PU-M también pasaron.

Una ejecución previa de la suite monolítica con volcado periódico de pila terminó con exit 139 mientras se volcaba la pila durante las ablaciones históricas. No produjo un recibo de aceptación; la causa del fallo de proceso no se ha demostrado. La aceptación corresponde a la ejecución posterior de los cuatro shards oficiales sin volcado periódico, que completó todas las pruebas. No se ocultó ni se contabilizó como PASS la ejecución interrumpida.

La dependencia opcional pyswisseph 2.10.3.2 se instaló únicamente para ejecutar las pruebas VED preexistentes sin omisiones. No se añadió como dependencia del nuevo núcleo. Las comprobaciones de preservación, rollback, límites, schemas y procedencia pasan; esto acredita comportamiento del software, no validez empírica o metafísica.

La comparación directa del recorrido OFF con M26 del baseline `c938e0d0032f6940eebb0e26373c051e473eeb81` conserva identidad semántica. En 10.000 iteraciones sintéticas, el p95 pasa de 0,009805 ms a 0,010886 ms: incremento del 11,02 %, inferior al límite del 20 %. El recibo se conserva en `atacires-historical-off-performance.json`. Esta medición no constituye un SLA de producción.

## Estado remoto y trabajo futuro

El commit final de integración `5f3eccc88475f1cfedb943e9c2b18ccf54379883` está publicado en `main`. El workflow remoto [Núcleo Python, ejecución 37468837265](https://github.com/2926097/almas-twin-flame-astrology/actions/runs/37468837265) terminó correctamente para los ocho jobs de la matriz: `core`, `atacires-core`, `full-pipeline` y `returns` en Python 3.10 y 3.12. Los recibos de los ocho shards se conservaron como artefactos. Pasaron los validadores ejecutados en `core`, incluida la distribución wheel aislada y el contrato público; la comprobación SSAR específica de Python 3.12 también pasó. Por ello, Python 3.10 y 3.12 quedan verificados por esta matriz para este commit concreto, sin extender esa conclusión fuera de los jobs ejecutados.

El benchmark de Atacires no se ejecutó en Actions: las métricas de rendimiento citadas en esta acta son mediciones sintéticas locales y no constituyen un SLA. La rama `main` carece de protección y de checks obligatorios. El resultado remoto no cambia el alcance: SHADOW continúa desactivado por defecto y la promoción productiva sigue NO-GO. Una promoción, una segunda técnica, la migración MCP y un nuevo proveedor Swiss requieren el trabajo separado descrito en el plan R1.
