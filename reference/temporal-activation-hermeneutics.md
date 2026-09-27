# Hermenéutica de activación temporal · M26–M27

## Finalidad

La temporalidad en ALMAS no descubre la arquitectura del vínculo. La activa.

M26 recibe señales temporales ya declaradas y las ancla a raíces estructurales existentes. M27 registra hechos documentales y puede enlazarlos con esas señales. La autoría debe respetar esa dirección:

`raíz estructural → activación temporal → proceso simbólico → hecho documentado si existe`.

Nunca invertirla como:

`evento intenso → por tanto existía una raíz`.

M26 declara expresamente:

- `structural_score_modified=false`;
- `structural_roots_created=false`;
- `real_world_event_prediction_made=false`.

## Fuente canónica

En autoría usar:

- `canonical_analysis.temporal.activation` para M26;
- `canonical_analysis.temporal.events` para M27;
- `canonical_analysis.evidence` para recuperar la raíz activada.

No reconstruir activaciones desde fechas, efemérides o eventos después de M31.

## Orden de lectura de una señal

Para cada señal temporal seleccionada:

1. localizar `root_id`;
2. recuperar la raíz y su significado estructural;
3. leer `activation_class`;
4. leer `temporal_family` como procedencia técnica, no como significado automático;
5. si existe `trigger_context`, resolver disparador → geometría → objetivo;
6. calibrar con `effective_strength` y `exactitude_orb`;
7. situar `window_status` y `date_or_period`;
8. comprobar `event_refs`;
9. distinguir activación simbólica de hecho documentado.

La frase debe comenzar por la raíz:

> La raíz X, que describe [...], entra en una ventana de activación [...].

No comenzar por el índice IAT ni por el nombre de la técnica.

## Clases de activación

### DIRECT_REPETITION

Coeficiente M26: `k=1.00`.

La señal repite de forma directa la estructura de la raíz. Hermenéuticamente es la forma más literal de reactivación dentro del modelo M26.

Puede redactarse como:

> El patrón central reaparece con una geometría temporal que reproduce directamente la raíz ya existente.

No significa que deba ocurrir un hecho externo equivalente.

### RELATIONAL_ROOT_ACTIVATION

Coeficiente M26: `k=0.90`.

La señal activa la raíz relacional como unidad, sin requerir identidad literal completa con la configuración original.

Puede redactarse como:

> La ventana temporal reactiva el tema relacional contenido en la raíz, haciendo más disponible o visible su dinámica.

No implica reciprocidad, contacto o decisión conjunta.

### ENDPOINT_ACTIVATION

Coeficiente M26: `k=0.70`.

La señal toca uno de los extremos relevantes de la raíz. Puede movilizar una función del circuito sin repetirlo entero.

Puede redactarse como:

> La activación alcanza uno de los puntos que sostienen la raíz; por ello moviliza una parte del patrón más que reproducir su arquitectura completa.

Evitar narrarla como confirmación equivalente a DIRECT_REPETITION.

### UNANCHORED

`k=0.0`.

No dispone de raíz canónica resoluble. M26 la excluye de IAT y la marca `UNANCHORED`.

No debe entrar en la lectura sustantiva del vínculo. Puede aparecer en anexos metodológicos como señal no anclada.

## Disparador astrológico concreto · `trigger_context`

Cuando una señal M26 conserva `trigger_context`, la autoría puede explicar **qué factor temporal activa qué factor de la arquitectura y mediante qué geometría**.

Campos mínimos:

- `trigger_point`: factor temporal ya calculado por la técnica de origen;
- `target_point`: punto objetivo ya calculado;
- `relation`: geometría/aspecto declarado.

Campos opcionales:

- `source_layer` y `target_layer`;
- `source_subject` y `target_subject`;
- `orb`;
- procedencia adicional conservada literalmente por el productor upstream.

M26 no calcula ni reconstruye estos datos. Sólo preserva el objeto recibido. Su presencia o ausencia no altera `strength`, `effective_strength`, `iat_eligible`, deduplicación, IAT ni la existencia de la raíz.

Orden de lectura cuando existe:

`raíz existente → trigger_point → función del trigger → relation → target_point → función objetivo → ventana → proceso → evento si existe`.

Para las funciones planetarias usar `planetary-function-hermeneutics.md`. Para conjunción, oposición, cuadratura, trígono y sextil usar `aspect-geometry-hermeneutics.md`. Si el punto es Nodo, ángulo, Vertex o Quirón, aplicar además la hermenéutica especializada correspondiente.

Ejemplo:

> La raíz R..., ya asociada a vínculo y transformación, recibe durante esta ventana un tránsito de Saturno en cuadratura a Venus. Saturno introduce estructura, límite, tiempo y responsabilidad; Venus representa valoración y forma de vincularse; la cuadratura hace que ambas funciones se encuentren bajo fricción y necesidad de ajuste. La señal vuelve más saliente ese proceso durante la ventana indicada, pero no predice por sí sola separación, compromiso ni una decisión concreta.

Evitar:

> «Saturno cuadratura Venus significa que la relación va a terminar.»

El contexto del disparador explica **cómo** se activa la raíz; no convierte la activación en causalidad factual.

## Fuerza y exactitud

`strength` es la intensidad declarada de la señal.

`effective_strength = strength × k`.

Usar `effective_strength` como calibrador relativo dentro de M26, no como porcentaje de que ocurra un evento ni como medida de importancia metafísica.

`exactitude_orb` informa precisión de la señal bajo su técnica declarada. Una mayor exactitud no convierte por sí sola una activación en un hecho real.

## Ventanas

### RETROSPECTIVE_CONFIRMED

La ventana corresponde al pasado y dispone de corroboración bajo el registro temporal/documental aplicable.

La autoría puede comparar activación y hecho, manteniendo separados ambos niveles:

> La raíz estaba activada en el mismo período en que se documenta X.

No afirmar causalidad sólo por coincidencia.

### RETROSPECTIVE_UNCONFIRMED

La ventana pasada no dispone de corroboración documental suficiente.

Puede describirse la activación calculada, pero no narrar una manifestación concreta como si estuviera documentada.

### CURRENT_ACTIVE

La raíz se encuentra dentro de una ventana declarada como activa.

Formulación preferente:

> El período actual mantiene activa la temática de [...].

No:

> Va a ocurrir [...].

### PROSPECTIVE_ACTIVATION

Describe una ventana futura de activación potencial.

M26 fija `predicts_real_world_event=false`.

Puede formularse:

> Entre X e Y se abre una ventana en la que la raíz puede adquirir mayor saliencia simbólica.

No convertirla en predicción de encuentro, separación, reconciliación, matrimonio, viaje, mensaje, decisión, consentimiento o cierre.

### EXPLORATORY

La señal no cumple el mismo estatus preregistrado de las señales elegibles.

Debe presentarse como exploración técnica y quedar fuera de una conclusión temporal fuerte.

### UNANCHORED

No vincular a la narrativa principal.

## Recurrencia temporal

`root_activation_summary` permite saber si una misma raíz aparece activada por más de una familia temporal independiente.

Cuando:

`recurring_across_independent_families=true`

puede afirmarse que la **activación del mismo tema** reaparece en familias temporales distintas.

Esto aumenta la coherencia temporal interna del análisis, no la independencia de la raíz estructural ni la probabilidad de un hecho.

Formulación:

> La misma raíz recibe activación desde más de una familia temporal, por lo que el período concentra el tema X de forma multitécnica.

No contar cada familia como nueva evidencia estructural.

## Familias temporales

M26 reconoce:

- `TPROG`;
- `TDIR`;
- `TTRANSIT`;
- `TECLIPSE`;
- `TREL`;
- `TATACIR`.

En el corpus ALMAS 1.20 estas etiquetas identifican procedencia técnica. No atribuir a cada familia un significado psicológico o metafísico especializado salvo que exista una fuente de método registrada para esa técnica.

Especialmente:

- `TATACIR` no preregistrado se fuerza a `EXPLORATORY`;
- no equiparar eclipse con destino inevitable;
- no equiparar progresión/dirección con madurez factual;
- no equiparar tránsito con causalidad externa.

## IAT

IAT agrega señales elegibles sólo bajo una política de pesos preregistrada.

Debe aparecer después de explicar qué raíces están activadas.

Uso válido:

> El IAT resume la concentración de señales elegibles en la ventana definida.

Uso inválido:

> IAT 80 significa 80 % de probabilidad de reunión.

IAT no crea significado. Resume activación ya anclada.

## M27 · hechos documentales

M27 debe mantener separados:

- `fact_statement`;
- interpretaciones;
- rol documental;
- calidad documental;
- refs de raíces/cláusulas;
- privacidad;
- estado activo/superseded.

Un hecho puede:

- corroborar una activación;
- aportar evidencia de cumplimiento;
- actuar como contraevidencia;
- documentar viabilidad;
- documentar reciprocidad;
- documentar fenomenología;
- aportar sólo contexto.

No puede crear retrospectivamente:

- una raíz;
- una cláusula;
- un origen;
- una posición astrológica ausente.

## Enlace señal ↔ evento

Cuando `temporal_event_links` resuelve una pareja `signal_id ↔ event_id`, la autoría puede poner ambos niveles en relación.

Secuencia:

`raíz → señal → ventana → evento documentado → interpretación prudente`.

Ejemplo:

> La raíz Saturno–Nodo aparece activada en la ventana X; dentro del mismo período el ledger documenta un cambio relacional. La coincidencia permite leer el hecho como corroboración temporal del tema de estructuración/límite, sin establecer causalidad ni convertir el evento en prueba del origen del vínculo.

Si el evento está `SUPERSEDED`, utilizar la versión activa/correctiva correspondiente.

Si la referencia temporal al evento está sin resolver, no usarla como corroboración.

## Calidad documental

La fuerza hermenéutica del hecho depende de su estatus documental, no de la intensidad astrológica.

No confundir:

- señal muy fuerte + evento no verificado;
- señal moderada + hecho primario documentado.

Son ejes distintos.

Cuando M27 declare problemas de calidad, precisión temporal o trazabilidad, reflejarlos en el alcance de la conclusión, no necesariamente como advertencia repetitiva en cada párrafo.

## Proceso evolutivo

Después de describir la activación técnica, traducirla a proceso usando el significado previo de la raíz.

Ejemplos:

- raíz de transformación → período de intensificación, crisis o reorganización del patrón;
- raíz de comunicación → período de mayor saliencia del intercambio, negociación o reformulación;
- raíz de límite/estructura → período de definición, contención, responsabilidad o confrontación con límites;
- raíz de reconocimiento/nodos → período en que el eje de dirección, continuidad o elección relacional adquiere mayor centralidad simbólica.

La función evolutiva procede de la raíz y del motivo, no del nombre de la técnica temporal.

## Síntesis temporal

Una buena S07 debe poder responder:

1. ¿qué raíz se activa?;
2. ¿cómo se activa?;
3. ¿cuándo?;
4. ¿con qué intensidad relativa?;
5. ¿reaparece en más de una familia temporal?;
6. ¿existe hecho documentado enlazado?;
7. ¿qué proceso simboliza?;
8. ¿qué no puede afirmarse todavía?

Plantilla conceptual:

> Durante [ventana], la raíz [X] —que en la arquitectura describe [dinámica]— recibe una activación [clase]. La señal alcanza [fuerza relativa] y [recurre/no recurre] en familias independientes. [Si existe evento:] En el mismo período M27 documenta [hecho], que puede utilizarse como [rol documental]. En términos evolutivos, el período concentra [proceso]. Esto no predice ni obliga a [hecho futuro].

## Regla final

La temporalidad responde **cuándo se vuelve saliente una arquitectura ya demostrada**, no **qué debe ocurrir en la realidad**.
