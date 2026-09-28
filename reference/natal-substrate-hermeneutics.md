# Hermenéutica del sustrato natal · ALMAS 1.20

## Finalidad

Este documento interpreta `canonical_analysis.natal_context` como la estructura que cada sujeto trae **antes del encuentro**.

No añade posiciones, aspectos, dignidades, regencias, casas, scores ni raíces. Lee exclusivamente datos ya calculados por M02/M04:

- `subjects.<id>.point_signs`;
- `subjects.<id>.nodes`;
- `subjects.<id>.angles`;
- `subjects.<id>.house_cusps`;
- `subjects.<id>.house_placements`;
- `subjects.<id>.rulerships`.

La pregunta central es:

> ¿Qué patrón individual existe antes de que la otra persona lo active?

La secuencia base es:

`función planetaria → signo/modo → casa natal/campo → regencia declarada/conexión → tema individual`.

Sólo después:

`tema individual → contacto de la otra persona → geometría → superposición → raíz → motivo relacional`.

Fuentes de método:

- `astrodienst_zodiac_sign`;
- `astrodienst_element`;
- `astrodienst_quality`;
- `astrodienst_sign_ruler`;
- `astrodienst_house_ruler`;
- `astrodienst_intro_houses`;
- `astrodienst_personal_planet`;
- `astrodienst_jupiter`;
- `astrodienst_saturn`;
- `astrodienst_uranus`;
- `astrodienst_neptune`;
- `astrodienst_pluto`.

---

# I. Principio fundamental · planeta, signo y casa no son sinónimos

Astrodienst resume una distinción metodológica esencial:

- el **planeta** representa una función;
- el **signo** indica cómo o de qué manera opera;
- la **casa** localiza el campo de vida donde esa función se expresa;
- la **regencia** enlaza un campo o signo con la posición de su planeta regente.

En ALMAS esta distinción es obligatoria.

No redactar:

> «Venus en Escorpio significa relaciones intensas.»

como una etiqueta cerrada.

Descomponer:

1. Venus → valorar, vincularse, atraer, intercambiar afecto;
2. Escorpio → agua fija: intensificación emocional, concentración, persistencia y dificultad para soltar;
3. casa natal → campo donde esa forma venusina se organiza;
4. regencias disponibles → conexiones con otros campos;
5. aspectos/raíces posteriores → qué activa la relación en esa predisposición.

---

# II. Funciones planetarias

Para el significado de los planetas usar siempre:

`reference/planetary-function-hermeneutics.md`.

Resumen operativo:

- Sol → identidad, centro expresivo, dirección consciente;
- Luna → emoción, seguridad, hábito, receptividad;
- Mercurio → pensamiento, lenguaje, aprendizaje;
- Venus → valoración, vínculo, atracción;
- Marte → afirmación, deseo, iniciativa;
- Júpiter → expansión, significado, horizonte;
- Saturno → límite, estructura, tiempo, responsabilidad;
- Urano → liberación, cambio, originalidad;
- Neptuno → permeabilidad, idealización, trascendencia;
- Plutón → intensidad, poder, transformación.

El signo no sustituye esta función. La modula.

---

# III. Signo como modo de expresión

Fuente principal: `astrodienst_zodiac_sign`.

Regla:

> El signo responde **cómo** intenta operar una función, no **qué** función es.

Por ello:

- Marte en Libra sigue siendo Marte: afirmación/acción;
- Venus en Aries sigue siendo Venus: valoración/vínculo;
- Saturno en Piscis sigue siendo Saturno: límite/estructura.

Lo que cambia es la forma, ritmo y estrategia de expresión.

## Elemento

Fuente: `astrodienst_element`.

Los cuatro elementos organizan el tono general:

- **Fuego** → expresividad, impulso, vitalización, orientación hacia acción/sentido;
- **Tierra** → concretización, estabilidad, materialización, eficacia;
- **Aire** → relación mental, conceptualización, comunicación, intercambio;
- **Agua** → receptividad, sentimiento, vínculo interno, permeabilidad emocional.

Estas palabras son vocabulario hermenéutico, no mediciones psicológicas.

## Modalidad

Fuente: `astrodienst_quality`.

- **Cardinal** → inicia, activa, pone en marcha;
- **Fija** → conserva, intensifica, estabiliza, sostiene;
- **Mutable** → adapta, redistribuye, concluye, transforma una forma en otra.

La modalidad indica dinámica; no valor.

---

# IV. Matriz de los doce signos

La matriz combina elemento + modalidad. Astrodienst ofrece precisamente esta organización como forma de diferenciar los doce signos.

| Signo | Elemento | Modalidad | Verbo hermenéutico base |
|---|---|---|---|
| Aries | Fuego | Cardinal | iniciar / impulsar |
| Tauro | Tierra | Fija | estabilizar / consolidar |
| Géminis | Aire | Mutable | conectar / diversificar |
| Cáncer | Agua | Cardinal | proteger / iniciar vínculo emocional |
| Leo | Fuego | Fija | irradiar / sostener expresión |
| Virgo | Tierra | Mutable | discriminar / adaptar / perfeccionar |
| Libra | Aire | Cardinal | relacionar / equilibrar / negociar |
| Escorpio | Agua | Fija | intensificar / profundizar / retener-transformar |
| Sagitario | Fuego | Mutable | ampliar / orientar / buscar sentido |
| Capricornio | Tierra | Cardinal | estructurar / construir / responsabilizar |
| Acuario | Aire | Fija | organizar ideas / diferenciar / reformular |
| Piscis | Agua | Mutable | permeabilizar / integrar / disolver límites |

Estos verbos no son predicciones de conducta. Sirven para modular una función planetaria.

---

# V. Composición planeta × signo

## Regla

`función + modo`.

No describir el signo primero.

### Ejemplo · Venus en Aries

- Venus → valoración/vínculo;
- Aries → fuego cardinal → inicia e impulsa.

Lectura:

> La función de vínculo tiende a buscar expresión directa, activa e iniciadora; valora aquello que moviliza y puede necesitar sentir que la relación está viva y en movimiento.

No concluir:

> «ama impulsivamente»

si el resto de la carta no lo sostiene.

### Ejemplo · Luna en Capricornio

- Luna → necesidad/emoción;
- Capricornio → tierra cardinal → estructura/construye.

Lectura:

> La regulación emocional tiende a buscar forma, control, responsabilidad o una estructura suficientemente fiable para sostener la vulnerabilidad.

No reducir a:

> «persona fría».

### Ejemplo · Mercurio en Piscis

- Mercurio → pensamiento/lenguaje;
- Piscis → agua mutable → permeabiliza e integra.

Lectura:

> El pensamiento puede procesar mediante asociaciones, imágenes, sensibilidad contextual y conexiones menos lineales; necesita mecanismos de discriminación cuando la permeabilidad aumenta.

No convertir en diagnóstico cognitivo.

### Ejemplo · Marte en Libra

- Marte → afirmación/acción;
- Libra → aire cardinal → inicia relación/negociación.

Lectura:

> La acción tiende a organizarse atendiendo al otro, a la comparación de posiciones o a la necesidad de restablecer equilibrio; la afirmación puede expresarse mediante negociación tanto como mediante confrontación.

---

# VI. Casa natal como campo propio

Fuente: `astrodienst_intro_houses`.

`house_placements` responde:

> ¿En qué área de la propia experiencia tiende a expresarse esta función?

No confundir con `cross_house_placements`:

- **casa natal** → dónde la función pertenece a la estructura del propio sujeto;
- **superposición sinástrica** → dónde la función de otra persona entra en la experiencia del receptor.

La diferencia es crucial.

Ejemplo:

> Venus natal de A en casa 8 describe un campo propio en el que vínculo/valor se asocian a intimidad, intercambio profundo, vulnerabilidad o recursos compartidos.

Si después Venus de B cae en la casa 8 de A:

> B activa desde fuera un campo que ya tenía significado interno para A.

La superposición no crea ese campo; lo toca.

---

# VII. Vocabulario de casas para sustrato natal

La misma semántica general de casas utilizada en las superposiciones se aplica aquí con gramática interna:

- Casa 1 → presencia, autoexpresión, entrada al mundo;
- Casa 2 → recursos, valor, sostén;
- Casa 3 → aprendizaje, lenguaje, entorno próximo;
- Casa 4 → raíz, intimidad, pertenencia;
- Casa 5 → creatividad, deseo expresivo, juego;
- Casa 6 → práctica, trabajo cotidiano, cuidado funcional;
- Casa 7 → alteridad, pareja, negociación;
- Casa 8 → intimidad profunda, intercambio, vulnerabilidad, transformación;
- Casa 9 → visión, significado, creencias, horizonte;
- Casa 10 → dirección pública, vocación, responsabilidad;
- Casa 11 → redes, comunidad, proyecto compartido;
- Casa 12 → interioridad, retiro, material difícil de objetivar.

Usar `house-overlay-hermeneutics.md` para la versión relacional A→B.

---

# VIII. Regencias · conexiones, no puntuación

M04 **no impone una escuela de regencias por defecto**.

Sólo genera `rulerships` cuando `raw_input.rulership_policy` fue declarado.

Esta decisión debe mantenerse en autoría.

## Regla

Si `rulerships` está vacío:

> no inventar regentes tradicionales ni modernos.

Si existe:

1. identificar signo de la cúspide;
2. leer sólo los `rulers` declarados;
3. localizar la función de ese planeta mediante `point_signs` y `house_placements`;
4. usar la conexión para enlazar áreas.

Fuente: `astrodienst_house_ruler`.

### Ejemplo

Supuesto canónico:

- casa 7 en Capricornio;
- ruler declarado: Saturno;
- Saturno natal en casa 4.

Lectura:

> El campo de pareja/alteridad queda conectado con una función saturnina situada en el ámbito de raíz, intimidad y fundamento privado. La relación tiende así a involucrar temas de estructura, responsabilidad o límite vinculados a la seguridad de base.

No afirmar:

> «su destino matrimonial es Saturno».

## Regencia de signo y dispositor

Fuente: `astrodienst_sign_ruler`.

Puede usarse para comprender cómo una función planetaria encuentra una vía de expresión a través de otra, **si la política declarada permite esa lectura**.

No convertir cadenas de dispositores en nuevas raíces relacionales.

---

# IX. Nodos y ángulos natales

`natal_context.nodes` y `angles` describen el sustrato individual antes de su activación sinástrica.

Para significado de extremos concretos usar:

`reference/angular-nodal-endpoint-hermeneutics.md`.

Diferencia:

- Nodo Norte natal → dirección simbólica de desarrollo propia;
- contacto del otro con Nodo Norte → activación relacional de esa dirección;
- Nodo Sur natal → familiaridad/patrón propio;
- contacto del otro con Nodo Sur → activación relacional de esa familiaridad.

Lo mismo para ASC/DSC, MC/IC.

La otra persona no “crea” el Nodo, el Ascendente o el eje. Los activa.

---

# X. Arquitectura individual mínima

Antes de pasar a sinastría, la autoría debería poder resumir para cada sujeto entre tres y seis proposiciones de estructura.

Priorizar:

1. Sol — identidad y modo de expresión;
2. Luna — necesidades/regulación emocional;
3. Ascendente — interfaz y modo de entrada;
4. Venus/Marte — vínculo, valoración, deseo y afirmación;
5. Saturno/Plutón/Quirón si forman parte de raíces relacionales relevantes;
6. nodos cuando sean activados posteriormente;
7. casas/regencias que conecten esos factores.

No escribir una interpretación natal exhaustiva si no ayuda a comprender la relación.

---

# XI. Principio de selección relacional

La carta natal completa contiene más información de la que un informe de relación necesita.

Regla:

> Interpretar primero los factores natales que después participan en raíces, superposiciones o motivos importantes.

Ejemplo:

Si una raíz central es Luna–Saturno:

- describir Luna natal del sujeto correspondiente;
- describir Saturno natal del otro;
- señalar signo/casa propios;
- sólo después desarrollar el contacto Luna–Saturno.

Esto produce continuidad narrativa:

`predisposición individual → encuentro → activación → dinámica`.

---

# XII. Diferenciar predisposición de activación

## Predisposición

> «A ya trae una Luna en signo/casa que organiza la seguridad emocional de determinada manera.»

## Activación

> «El Saturno de B entra en aspecto con esa Luna.»

## Geometría

> «La cuadratura introduce fricción/presión entre necesidad emocional y límite/estructura.»

## Campo

> «Además, el punto de B cae en la casa X de A.»

## Raíz

> «La misma dinámica reaparece en otras familias y forma una raíz independiente.»

## Función evolutiva

> «La relación puede obligar a hacer consciente cómo se negocian vulnerabilidad y responsabilidad.»

Esta cadena es preferible a:

> «Es una relación kármica porque tiene Luna–Saturno.»

---

# XIII. Dignidades y grados · no inferir por defecto

`point_signs` conserva `degree_in_sign`.

No usar ese dato para:

- símbolos sabianos;
- decanatos;
- términos/bounds;
- faces;
- grados críticos;
- exaltación/caída;
- dignidades esenciales;

salvo que el perfil de análisis incorpore explícitamente la técnica, fuente y política correspondiente.

La presencia numérica del grado no autoriza una técnica nueva.

Aunque las fuentes de Astrodienst documentan domicilio/exaltación, esta guía sólo usa la regencia declarada por M04. No introducir dignidades fuera del contrato del análisis.

---

# XIV. Sin signo solar reduccionista

Astrodienst advierte que la astrología de signo solar aislado es una simplificación.

Por tanto ALMAS no debe redactar:

> «A es Piscis y B es Cáncer, por eso...»

La lectura debe conservar planeta, signo, casa y contexto.

Ejemplo:

> «La Luna de A opera de manera canceriana en casa 4 y está implicada en la raíz R...»

es metodológicamente superior a:

> «A es muy Cáncer.»

---

# XV. Síntesis individual antes de la relación

Formato recomendado:

> «Antes de considerar el vínculo, A muestra una arquitectura en la que la función X se expresa de modo Y y se concentra en el campo Z. La función W añade una segunda necesidad/tensión. El eje nodal sitúa una dirección propia hacia... Esta estructura es previa al encuentro. La relación con B se vuelve significativa porque activa precisamente X/W/eje mediante las raíces R...»

Repetir para B.

Después:

> «La relación no introduce estos temas desde cero; los organiza, intensifica, confronta o facilita mediante sus contactos.»

---

# XVI. Aplicación a relaciones metafísicas

Sólo después de describir sustrato y activación puede añadirse hermenéutica metafísica.

Ejemplo:

1. Saturno natal fuerte en un campo relacional propio;
2. Nodo Sur del otro activa Saturno;
3. la raíz reaparece en otra familia;
4. motivo de continuidad estructural;
5. comparación con doctrina de continuidad/gilgul/contrato si las fuentes lo permiten.

La doctrina ayuda a interpretar una arquitectura ya explicada.

No debe utilizarse para sustituir la lectura natal.

---

# XVII. Prueba editorial de calidad

Una lectura del sustrato natal falla si:

- podría aplicarse igual a cualquier persona con el mismo signo solar;
- enumera posiciones sin relacionarlas;
- atribuye al vínculo algo que ya estaba en la carta;
- usa regentes no declarados;
- introduce dignidades o técnicas no calculadas;
- no vuelve posteriormente a los mismos factores cuando aparecen en raíces relacionales.

Prueba positiva:

> El lector debería entender qué necesidad, recurso o tensión preexistente está siendo activada antes de leer la etiqueta del modelo relacional.

---

# XVIII. Límite epistemológico

Esta guía pertenece a método interpretativo astrológico.

No afirma:

- validación científica de signos, casas o regencias;
- causalidad psicológica;
- diagnóstico de personalidad;
- destino;
- compatibilidad;
- reciprocidad;
- ontología del alma.

Su función dentro de ALMAS es narrativa y hermenéutica:

> **separar lo que cada persona ya trae de lo que la relación activa y de lo que el campo compartido hace emerger.**
