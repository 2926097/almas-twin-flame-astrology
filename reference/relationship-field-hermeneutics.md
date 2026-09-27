# Hermenéutica del campo relacional · ALMAS 1.20

## Finalidad

Este documento interpreta `canonical_analysis.relationship_field`, producido por M09 como contexto exclusivo de autoría.

El campo relacional responde una pregunta distinta de la sinastría:

> ¿Qué patrón aparece cuando la relación se considera como una unidad simbólica propia?

La cadena completa queda:

`sustrato de A + sustrato de B → activación sinástrica → campo relacional → recurrencia → función evolutiva`.

Fuentes de método registradas:

- `townley_composite_charts_2000`;
- `davison_synastry_1983`.

Estas fuentes sustentan el uso interpretativo de cartas relacionales. No validan científicamente la astrología ni convierten la compuesta o el Davison en prueba de alma gemela, contrato o llama gemela.

---

# I. Tres niveles que no deben confundirse

## 1. Individuo

`natal_context`

Pregunta:

> ¿Qué trae cada persona antes del encuentro?

## 2. Interacción

raíces sinástricas, casas cruzadas, declinaciones, antiscios y demás contactos.

Pregunta:

> ¿Qué activa una persona en la estructura de la otra?

## 3. Campo

`relationship_field`

Pregunta:

> ¿Qué organización emerge al considerar la relación como una unidad?

Una lectura madura debe poder distinguir los tres.

---

# II. Carta compuesta · organización simbólica interna

M07 construye la compuesta mediante puntos medios geométricos bajo una policy explícita.

Townley es la fuente metodológica registrada para esta técnica.

En ALMAS la compuesta se utiliza para describir:

- tono central del vínculo;
- funciones que adquieren centralidad dentro del campo común;
- tensiones y facilidades internas del sistema relacional;
- modo en que las funciones de la relación se organizan entre sí.

No representa literalmente a una tercera persona.

## Datos disponibles

`relationship_field.composite.positions`

Incluye:

- longitud;
- signo;
- grado dentro del signo.

`relationship_field.composite.internal_contacts`

Incluye aspectos internos calculados con la misma `aspect_policy` declarada para M09.

`relationship_field.composite.angles`

Puede conservar ángulos de punto medio si M07 los produjo.

## Contactos con ángulos

`relationship_field.composite.angle_contacts` cruza los `point_ids` seleccionados por M09 con los ángulos que M07 ya calculó. No crea una nueva técnica ni una nueva raíz: aplica la misma `aspect_policy` del campo a coordenadas ya disponibles.

La gramática es de campo:

- planeta/función → qué opera;
- ángulo → dónde se organiza el campo;
- aspecto → cómo interactúan.

Ejemplos:

- Sol compuesto conjunto ASC compuesto → la función identitaria/central del vínculo queda muy próxima a su modo de presencia o emergencia;
- Venus compuesto aspecto MC compuesto → vínculo, valor o atracción se articulan con dirección, proyección o propósito visible del campo;
- Saturno compuesto aspecto IC compuesto → estructura, límite o responsabilidad tocan la base privada/sostenedora del vínculo.

ASC/DSC y MC/IC forman ejes complementarios. Si aparecen contactos geométricamente equivalentes con ambos extremos, no narrarlos como dos confirmaciones independientes; elegir el extremo que exprese mejor la geometría concreta y conservar el otro como contexto del mismo eje.

## Casas

M07 declara:

`houses_calculated=false`.

Por tanto:

> **no interpretar casas de la compuesta**.

No estimarlas, no importarlas de otra herramienta y no trasladar casas Davison a la compuesta.

---

# III. Davison · relación situada en espacio y tiempo

M08 construye la carta Davison mediante el backend astronómico de producción sobre el punto espacio-temporal definido por la técnica.

La fuente metodológica registrada es `davison_synastry_1983`.

En ALMAS se utiliza para explorar:

- cómo se encarna o sitúa el campo relacional;
- qué funciones adquieren forma en una carta fechada y localizada;
- qué casas y ángulos organizan la manifestación del vínculo cuando el backend los calcula.

## Datos disponibles

`relationship_field.davison.positions`

`relationship_field.davison.internal_contacts`

`relationship_field.davison.angles`

`relationship_field.davison.house_cusps`

`relationship_field.davison.house_placements`

A diferencia de la compuesta, el Davison puede disponer de casas calculadas. Cuando existen las doce cúspides, M09 deriva además la casa de cada punto Davison antes de la autoría; la redacción debe consumir `house_placements` y no recalcular la pertenencia a casas.

`relationship_field.davison.angle_contacts` aplica la misma lógica posición↔ángulo a ASC/DSC/MC/IC ya calculados por M08. Esto permite describir cómo una función de la relación situada se enlaza con presencia, alteridad, fundamento o dirección del campo sin convertir el contacto en evidencia estructural adicional.

---

# IV. Consonancia compuesta ↔ Davison

M09 conserva en su salida estructural contactos entre puntos homólogos de ambas cartas.

Ejemplo:

`Sol compuesto ↔ Sol Davison`.

La pregunta no es si “dos técnicas votan lo mismo”.

La pregunta es:

> ¿Qué tema permanece reconocible cuando el mismo campo se construye mediante dos procedimientos distintos?

Esta persistencia puede reforzar hermenéuticamente una lectura del campo, pero ambas cartas permanecen dentro de una sola familia de dependencia:

`RELCHART`.

No duplicar independencia.

---

# V. field_context es autoría, no nueva evidencia

El contrato fija:

- `authoring_only=true`;
- `structural_evidence_used=false`;
- `creates_independent_roots=false`.

Los aspectos internos de compuesta y Davison:

- no llegan a M15;
- no crean nuevas raíces;
- no aumentan PA/PK/PE/PR/PT/PX/PS;
- no modifican IEM;
- no modifican IDD;
- no modifican IRC;
- no prueban ontología.

Su función es desarrollar el significado de una familia RELCHART que ya existe.

---

# VI. Cómo leer posiciones del campo

Aplicar:

`reference/planetary-function-hermeneutics.md`

y:

`reference/natal-substrate-hermeneutics.md`

con una diferencia gramatical.

En natal:

> «La Venus de A se expresa de modo...»

En compuesta:

> «La función venusina del vínculo se expresa de modo...»

En Davison:

> «La función venusina de la relación situada se expresa de modo...»

No atribuir automáticamente una posición compuesta a uno de los sujetos.

---

# VII. Cómo leer aspectos internos

Aplicar:

`reference/aspect-geometry-hermeneutics.md`.

Ejemplo:

`Venus compuesto cuadratura Plutón compuesto`.

Secuencia:

1. Venus → vínculo/valor/atracción;
2. Plutón → intensidad/poder/transformación;
3. cuadratura → fricción/presión/trabajo;
4. campo compuesto → dinámica interna de la relación.

Lectura:

> «Dentro del campo común, la función de vínculo y valoración entra en fricción con una dinámica de intensidad, poder y transformación. Esto describe una tensión interna del sistema relacional; no determina por sí misma cómo cada individuo actuará ni prueba una categoría espiritual.»

---

# VIII. Cómo leer signos en compuesta/Davison

El signo modifica el modo de expresión de una función.

Ejemplo:

`Luna compuesta en Capricornio`.

No redactar:

> «La pareja es Capricornio.»

Preferir:

> «La función emocional del campo tiende a buscar estructura, contención, responsabilidad o formas concretas de sostener la vulnerabilidad.»

Ejemplo:

`Mercurio Davison en Piscis`.

> «La comunicación del vínculo situado puede operar mediante asociaciones, intuición, imagen o permeabilidad contextual; cuando aumenta la ambigüedad necesita mayor discriminación.»

---

# IX. Casas Davison

Sólo cuando `house_cusps` exista.

La casa responde:

> ¿En qué campo experiencial se organiza una función del vínculo?

Aplicar el vocabulario de `house-overlay-hermeneutics.md`, pero en gramática de campo, no de superposición. `house_placements` se deriva exclusivamente de las cúspides M08 ya calculadas y permanece `authoring_only`; no crea raíces ni peso adicional.

Ejemplo:

> «Venus Davison en casa 8 sitúa la función vincular del campo en temas de intimidad, intercambio profundo, vulnerabilidad o recursos compartidos.»

No decir:

> «Venus de A cae en casa 8 de B».

Eso pertenece a sinastría.

---

# X. Prioridad interpretativa del campo

No hace falta narrar todos los puntos.

Priorizar:

1. Sol;
2. Luna;
3. Venus;
4. Marte;
5. Mercurio cuando comunicación sea estructural;
6. Saturno/Plutón cuando formen raíces centrales;
7. nodos/ángulos si están disponibles y tienen función interpretativa declarada;
8. Júpiter, Urano y Neptuno cuando sostengan motivos relevantes.

La selección debe responder al problema relacional real, no a exhaustividad enciclopédica.

---

# XI. Secuencia compuesta → Davison → consonancia

## Paso 1 · Compuesta

Preguntar:

> ¿Cómo se organiza internamente el vínculo?

Seleccionar:

- funciones dominantes;
- signos relevantes;
- aspectos internos vinculados a raíces/motivos.

## Paso 2 · Davison

Preguntar:

> ¿Cómo se sitúa o encarna ese vínculo en una carta relacional espacio-temporal?

Añadir:

- signos;
- aspectos;
- ángulos;
- casas cuando existan.

## Paso 3 · Consonancia

Preguntar:

> ¿Qué permanece reconocible entre ambos modelos?

No exigir identidad total.

La diferencia también aporta información:

> un tema puede ser central en la organización simbólica y menos visible en la carta situada, o viceversa.

---

# XII. Continuidad vertical con la sinastría

La lectura más valiosa aparece cuando un tema atraviesa niveles.

Ejemplo:

1. Venus–Plutón aparece en sinastría;
2. se integra en una raíz transformativa;
3. la compuesta contiene también una relación Venus–Plutón;
4. el Davison conserva una configuración equivalente o relacionada;
5. el motivo reaparece en RELCHART.

Entonces puede redactarse:

> «La transformación afectiva no queda limitada a lo que una persona activa en la otra; también organiza el campo que emerge entre ambas.»

Esto es una interpretación de continuidad.

No significa que M07 y M08 cuenten como nuevas raíces independientes.

---

# XIII. Campo que contradice la sinastría

También puede suceder lo contrario.

Ejemplo:

- sinastría con mucha afinidad Venus/Júpiter;
- campo compuesto con Saturno/Plutón tensionando luminarias.

La lectura no debe ocultarlo.

Puede formular:

> «La interacción interpersonal dispone de recursos de afinidad, pero el campo compartido introduce exigencias de estructura, límite o transformación que no se reducen a la facilidad entre individuos.»

El campo puede complejizar la experiencia sin “anular” la sinastría.

---

# XIV. Campo común y metafísica

Sólo después de interpretar la astrología concreta puede preguntarse:

> ¿Con qué doctrina o modelo metafísico es comparable este tipo de campo?

Posibles comparanda:

- misión compartida;
- catalización;
- aprendizaje relacional;
- continuidad;
- servicio;
- integración de polaridades;
- transformación.

No inferir directamente:

> «La compuesta prueba un contrato».

La doctrina entra como hermenéutica comparada de una arquitectura ya explicada.

---

# XV. No convertir la consonancia en una puntuación

M09 fija:

`consonance_score=null`

y:

`score_state=NOT_DEFINED`.

Esto es deliberado.

No inventar en autoría:

- porcentaje de consonancia;
- “compatibilidad compuesta-Davison”;
- umbral fuerte/débil;
- bonificación al modelo.

El número de contactos puede describirse, pero no convertirse en score implícito.

---

# XVI. Diferencia entre repetición y duplicación

Si un mismo motivo aparece en:

- sinastría;
- RELCHART;
- dracónica;

puede ser hermenéuticamente relevante como recurrencia multicapas.

Pero:

- compuesta y Davison siguen siendo una sola familia RELCHART;
- los aspectos internos de `field_context` no son raíces;
- la repetición narrativa no puede multiplicar el peso cuantitativo.

---

# XVII. Prueba editorial

Una lectura del campo es insuficiente si sólo dice:

> «La compuesta confirma la sinastría.»

Debe poder responder:

1. ¿qué función concreta domina el campo?;
2. ¿en qué signo se expresa?;
3. ¿qué aspecto interno la modifica?;
4. ¿qué añade el Davison?;
5. ¿qué casa Davison la localiza, si existe?;
6. ¿qué sobrevive entre ambas construcciones?;
7. ¿qué motivo sinástrico reaparece?;
8. ¿qué significa esa continuidad para la función evolutiva de la relación?

---

# XVIII. Fórmula narrativa recomendada

> «A trae X y B trae Y. La sinastría activa Z. Cuando el vínculo se considera como campo propio, la compuesta organiza esa dinámica mediante [...]. El Davison sitúa el mismo sistema mediante [...]. La persistencia/diferencia entre ambos modelos sugiere [...]. Esto amplía la función relacional ya observada, sin constituir una segunda evidencia independiente ni una prueba ontológica.»

---

# XIX. Límite epistemológico

El campo relacional pertenece a técnica astrológica.

No establece por sí mismo:

- reciprocidad real;
- permanencia;
- consentimiento;
- destino;
- contrato literal;
- origen compartido;
- alma gemela;
- llama gemela.

Su función en ALMAS es más precisa:

> **describir qué patrón adquiere la relación cuando deja de mirarse sólo como A frente a B y se estudia como una organización simbólica conjunta.**
