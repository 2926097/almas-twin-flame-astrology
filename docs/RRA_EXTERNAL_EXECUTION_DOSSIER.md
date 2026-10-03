# RRA · Expediente para ejecutar la validación externa real

Fecha: 3 de octubre de 2026. Árbol técnico de referencia: merge `a609b4c83189d014a15c21f305048bfd6603359f`. Diseño E del proyecto; **no es un preregistro ni un resultado empírico**.

## Dictamen de preparación

La validación solicitada no puede declararse completada con el material disponible. El recibo de preparación contiene cero casos reales admitidos, ninguna cohorte dimensionada, cero periodos de observación negativa verificados y ninguna inscripción externa. Las siete obligaciones continúan abiertas. Este expediente especifica qué evidencia permite resolver cada una y qué actuaciones deben preceder al cálculo. No sustituye esa evidencia.

Los siete vínculos activos del piloto, sus trece personas, los casos de desarrollo y el candidato retirado no son una muestra confirmatoria. Sus seis componentes son topológicos; no acreditan independencia estadística. No se reutilizarán para evitar la necesidad de una cohorte nueva.

## Matriz de obligaciones y evidencia de cierre

| Obligación | Evidencia disponible | Evidencia necesaria para resolverla |
|---|---|---|
| 1. Cohorte documental independiente | Dos cribados de conveniencia; `real_cases=[]`. | Marco de selección definido antes del cálculo; inventario de candidatos elegibles y excluidos con motivos; fuentes natales verificadas, incertidumbres y fuentes cronológicas; registro de exposición previa. Una persona expuesta en desarrollo/piloto excluye su componente del holdout. |
| 2. Codificación de eventos y acuerdo | No existen dos juegos independientes de codificaciones ni un recibo de acuerdo. | Dos codificadores identificables y distintos, sin resultados astrológicos; código documental congelado; sus archivos originales fechados; tabla de desacuerdos; medida y umbral fijados antes de codificar; adjudicación trazable y resultados publicados incluso si el acuerdo es insuficiente. |
| 3. Observación y controles | Inventario parcial; cero periodos negativos y cero controles admitidos. | Por vínculo: inicio/fin de cobertura, fuentes inspeccionadas y lagunas; definición de lo observable; fechas elegibles y excluidas; controles elegidos mediante algoritmo congelado sin consultar RRA; evidencia de ausencia del evento definido, estratos y registro de selección. Una búsqueda sin noticias no acredita ausencia. |
| 4. Partición por personas y dependencia | Sólo está reconstruido el grafo del piloto. | Grafo de toda la cohorte nueva, con personas compartidas, cronologías y dependencias documentales; componentes asignados íntegros a desarrollo/piloto/holdout/réplica; manifest y auditoría de cruces. La réplica necesita evidencia separada; renombrar personas no crea independencia. |
| 5. Tamaño y parada | Tamaño y número de componentes independientes nulos. | Justificación reproducible por potencia o precisión del estimando definido; supuestos de tasa basal, dependencia y pérdidas procedentes del piloto; efecto mínimo o precisión relevante motivados; objetivo de componentes evaluables, límite de reclutamiento y fecha/regla de parada antes de abrir resultados. Si la factibilidad no alcanza el objetivo, se declara insuficiencia; no se rebaja después de ver resultados. |
| 6. Intercambiabilidad y multiplicidad | Endpoint descriptivo implementado; intercambiabilidad no establecida. | Modelo nulo y población objetivo; justificación del mecanismo de controles; bloques y restricciones de reordenación, calendario, edad, temporada, selección de eventos y dependencia; simulaciones de error tipo I y sensibilidad bajo supuestos explícitos; una familia de pruebas y regla de multiplicidad congeladas. No hay p-valor confirmatorio mientras falte esta justificación. |
| 7. Preregistro verificable | Borrador GitHub; `external_registration=null`, holdout cerrado. | Inscripción completa con identificador/URL, sello temporal y copia archivada; incluye los seis expedientes anteriores, código/commit y hashes, kernel/backend, endpoint, denominadores, pérdidas, pruebas, exclusiones, tamaño y parada. Evidencia de que el registro precede al acceso a resultados del holdout y de su custodia; después, registro de apertura y desviaciones. |

## Especificación documental para la recogida

El inventario de selección debe conservar todas las inclusiones y exclusiones, no sólo parejas que parezcan prometedoras. Para cada vínculo se necesitan identificadores estables de las dos personas, fuentes públicas de nacimiento, calidad horaria y discrepancias sin rectificación por resultados, coordenadas, zona IANA y periodo documental. Los originales o copias consultadas se identifican con localizador, páginas, fecha de acceso y hash cuando proceda. Dos páginas que copian la misma noticia no cuentan como confirmación independiente.

Cada codificador debe registrar, por la misma unidad documental, tipo de acontecimiento, fecha del hecho, precisión/incertidumbre, fuente y pasaje, elegibilidad, conflicto y motivo. La fecha de publicación se conserva en una columna distinta. Ausencia de dato, desacuerdo y ausencia documentada son estados distintos. El acuerdo se calcula sobre los archivos independientes anteriores a la adjudicación; la tabla adjudicada no puede utilizarse para aparentar acuerdo inicial perfecto. Un agente, dos respuestas del mismo asistente o dos transcripciones de un archivo no acreditan esta doble codificación.

Para las fechas control, el registro debe permitir reconstruir la población de fechas candidatas y la selección. No basta una lista final de fechas. Se documentan cobertura, lagunas, tipo de evento cuya ausencia puede sostenerse, estrato, criterio de emparejamiento, exclusiones y semilla si existe selección aleatoria. Los eventos de calendario o aniversarios requieren una regla previa defendible. Los controles de cronologías incompletas se rechazan en vez de etiquetarse negativos.

Los materiales privados permanecen fuera del repositorio público conforme a la política de aislamiento existente. Los manifiestos públicos sólo pueden contener información ya pública y verificada o referencias externas opacas autorizadas con agregados no identificables.

## Especificación analítica que debe congelarse

El candidato actual mide un indicador binario por fecha: existencia de al menos un contacto no tautológico, anclado en arquitectura estructural previamente cualificada, dentro de la ventana exacta. Conserva nulo si la fecha no es evaluable, excluye referencias EVENT y exige cobertura de búsqueda que incluya la incertidumbre y las ventanas completas. Calcula tasa evento menos tasa control por vínculo, media por componente y media entre componentes evaluables, con denominadores y pérdidas. Véase `RRA_EXTERNAL_RUNNER.md`.

Antes del holdout debe decidirse si esa regla es el endpoint primario definitivo y cómo afecta la pérdida de componentes al estimando. Deben fijarse el tratamiento de fechas solapadas, raíces elegibles y multiplicidad de cuerpos, aspectos, ventanas y análisis secundarios. No se escogerá el subconjunto con mejor resultado. Si se mantiene un único contraste agregado primario, los análisis por cuerpo, técnica o subgrupo quedan explícitamente secundarios/exploratorios; si se vuelven confirmatorios, deben incorporarse a la familia y su ajuste antes de abrir.

La justificación muestral debe operar sobre componentes realmente independientes, no sobre el total de contactos o fechas. Debe incorporar las pérdidas de evaluabilidad y la dependencia dentro del componente. Una simulación sintética permite evaluar un diseño bajo supuestos; no proporciona por sí sola la tasa basal de la población real ni establece intercambiabilidad. Los valores propuestos de alfa 0,05 y 9.999 simulaciones siguen siendo candidatos, no decisiones preregistradas ni política calibrada.

El mecanismo inferencial debe examinar que sus reordenaciones sean válidas bajo la hipótesis nula. Emparejar por edad o desplazar fechas uniformemente no demuestra ese requisito. Si no puede defenderse, el estudio sólo podrá reportar resultados descriptivos y limitaciones. No se activará el modo confirmatorio por cambiar una bandera del runner.

## Orden de ejecución y registros

1. Formar la cohorte nueva y el inventario documental sin calcular su astrología; resolver calidad, elegibilidad y dependencia.
2. Obtener las dos codificaciones independientes y su adjudicación; acreditar periodos de observación y generar controles mediante reglas previas.
3. Justificar tamaño/parada e inferencia con un piloto separado del holdout. Si se inspeccionan resultados de un caso durante esta preparación, excluir todo su componente de la evaluación reservada de esta versión.
4. Congelar el paquete completo: manifests de selección y partición, código documental, controles, plan analítico, código y dependencias, recursos RRA, hashes del kernel y políticas. Registrar externamente el paquete antes de abrir resultados.
5. Auditar el registro y la custodia. Ejecutar la estructura ciega, guardar su hash y después abrir el documental permitido. Ejecutar el análisis conforme al plan; publicar pérdidas, negativos, desviaciones y limitaciones.
6. Hacer una réplica independiente para cualquier promoción que la exija. El informe empírico y la eventual promoción versionada del motor son decisiones distintas.

La inscripción requiere un responsable real y acceso a la plataforma elegida; la codificación requiere dos actuaciones independientes; el corpus requiere los datos originales admisibles. No hay recibos que acrediten estas actuaciones en el repositorio examinado. No se asignan identidades, firmas, cuentas ni DOI ficticios. La trazabilidad GitHub de este expediente no acredita que se haya ejecutado ninguna de ellas.

## Cierre y resultado

Resolver las siete obligaciones habilitaría la preparación de una ejecución; no demostraría todavía una asociación. El cierre empírico exige además el informe de la ejecución real con el alcance registrado. Un resultado nulo o desfavorable puede cerrar un estudio válido. Un estudio sin datos suficientes puede finalizar como no evaluable, pero no como validación completada. En el estado actual se conserva **NOT_PERFORMED**, `confirmatory_execution_allowed=false` y `holdout_opened=false`.

## Fuentes metodológicas comprobadas

- Center for Open Science, documentación oficial de registros, consultada el 3-10-2026: https://help.osf.io/article/330-welcome-to-registrations. Distingue borrador, envío, archivo y aprobación; un borrador local no es una inscripción completada.
- Winkler et al. (2014), DOI 10.1016/j.neuroimage.2014.01.060, resumen y extractos indexados: https://pubmed.ncbi.nlm.nih.gov/24530839/. La inferencia por permutación requiere intercambiabilidad y restricciones apropiadas; la referencia no certifica el diseño RRA.
- Lakens (2022), DOI 10.1525/collabra.33267, resumen institucional y extractos indexados: https://research.tue.nl/en/publications/sample-size-justification/. La justificación puede basarse en potencia o precisión, entre otras vías explícitas; esta referencia no aporta un tamaño adecuado para una cohorte todavía inexistente.
