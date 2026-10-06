# ALMAS · Plan depurado de integración Atacires, revisión R1

Fecha: 6 de octubre de 2026. Contrato rector: `ATACIRES_ALMAS_DIRECTRICES.md`. Base ALMAS: `c938e0d0032f6940eebb0e26373c051e473eeb81`. Fuente Atacires: `d0d3a4bcf315708a4bf6f7e40cf2873732819b61`. El plan recibido se conserva en `ATACIRES_PLAN_ORIGINAL.md` como antecedente, no como declaración de trabajo ejecutado.

La revisión sustituye rutas, interfaces y supuestos propuestos por las interfaces reales del repositorio. M26 ya acepta TATACIR, calcula IAT con pesos preregistrados y utiliza `ModuleContext`/`ModuleResult`; no existe el `AnalysisContext` que proponía el borrador. La importación se registra como decorador del handler vigente, conserva su payload y estado, y produce exclusivamente el namespace `atacires_shadow`, que M30 incorpora en `temporal.atacires_shadow`. M31 conserva el análisis canónico conforme a su mecanismo vigente. No se introducen señales del motor en la agregación productiva de M26.

La repetibilidad distingue resultado matemático y registro operativo. `executed_at` varía entre ejecuciones y queda fuera de la huella del resultado; TZif, fuente natal, parámetros efectivos y revisión técnica permanecen registrados. Los oráculos son sintéticos y quedan fijados por revisión y SHA-256, no por tolerancias implícitas ni por datos de José Luis o Indira.

### Tarea 1: auditoría y contrato

Congelar ambas revisiones, revisar licencias y solapamientos, verificar regresión histórica y documentar decisiones. La licencia MIT del núcleo se conserva en el paquete y en los oráculos de tests. Las dependencias ausentes del entorno se corrigen antes de atribuir un fallo al repositorio.

### Tarea 2: núcleo, adaptador e invariancia

Importar únicamente `scripts/engine.py`, sin cambiar su matemática. Construir solicitudes congeladas desde la carta canónica y el sujeto correspondiente; rechazar dialectos, coordenadas o instantes incompatibles, fuentes incompletas y hora incierta. Registrar provenance y normalizar los resultados una vez. Crear enlaces de extremo sólo contra las raíces existentes. Mantener observaciones huérfanas, deduplicar por identidad y conservar la política canónica de dependencia temporal. Feature OFF debe devolver exactamente el ModuleResult previo.

### Tarea 3: verificación técnica y CI

Portar las 55 pruebas originales, ejecutar referencias analíticas y 100 comparaciones diferenciales de semilla fija, comprobar contratos, preservación del IAT existente, ensamblado canónico, rollback, rechazo de límites y robustez de muestras ya recalculadas. Incorporar `atacires-core` a la matriz Python 3.10/3.12, conservar la exhaustividad de los shards y comprobar distribución wheel con licencia incluida. Medir el recorrido OFF real y el núcleo por separado.

### Tarea 4: revisión y cierre experimental

Realizar revisión independiente del cambio completo, corregir hallazgos importantes mediante regresiones reproducibles, ejecutar suites completas y preparar una PR revisable. Su publicación queda bloqueada por la revisión automática de aprobación hasta obtener autorización explícita de divulgación en el repositorio público. El acta distingue aceptación de la implementación experimental y promoción productiva: esta última permanece NO-GO. La fusión a main se somete al resultado efectivo de la PR y a la instrucción correspondiente, sin certificar checks remotos pendientes.

## Resolución de las 17 tareas originales

Las tareas originales 1–8 se resuelven mediante las tareas R1 1–3. La tarea 9 se cumple con comparación de muestras previamente recalculadas; no se crea un segundo motor Monte Carlo ni se desplaza una carta natal fija fingiendo perturbación astronómica. La tarea 10 añade benchmark y límites de carga. La tarea 11 incorpora CI, empaquetado y preservación de MIT. La tarea 12 declara el protocolo compatible con el backend actual y un proveedor sintético de contrato, sin habilitar técnicas futuras. La tarea 13 fija la matriz de autoridad por técnica.

La tarea 14 queda DEFERRED: la búsqueda de contactos ya existe en `temporal_perfection_solver.py`; secundaria y arco solar necesitan definir un evaluador compatible con el backend canónico y comprobar exhaustividad antes de migrar el buscador numérico Swiss de Atacires. Los retornos se mantienen bajo RRA. La tarea 15 queda DEFERRED conforme a la directriz 11: el MCP remoto sigue consumiendo su servicio actual y esta PR no cambia ese despliegue; el snapshot usa `mcp==1.18.0`, y una migración de SDK/protocolo no tiene contrato cerrado aquí. La tarea 16 queda DEFERRED conforme a su condición expresa: no se crea un extra Swiss para Atacires ni se presume resuelta la licencia de un servicio que lo incorpore. La tarea 17 emite aceptación experimental condicionada a pruebas y checks efectivos, no una promoción canónica.

## Decisiones de revisión y coste de error

Ruling: mantener los índices, incluidos IAT e IAT por componentes, fuera de las salidas generadas — M26 ya puede agregarlos y el contrato prohíbe que esta integración los cambie — una posterior promoción necesitaría especificación y pruebas propias.

Ruling: usar namespace canónico temporal adicional y conservar el estado operativo histórico de M26 — evita fingir que sus señales preregistradas ya son evaluables — el consumidor debe leer el estado del bloque sombra para conocer la ejecución del motor.

Ruling: restringir esta revisión a contactos entre puntos de una misma carta canónica — el motor fuente sólo acepta una tabla natal, sin identidad de carta destino separada — la activación de raíces relacionales se describe como extremo, no como repetición sinástrica directa.

Ruling: posponer las tareas originales 14–16 por sus condiciones no satisfechas — evita duplicar capacidades y mezclar cambios matemáticos, transporte y backend — la ampliación requiere una evolución separada; no se presenta como ya ejecutada.
