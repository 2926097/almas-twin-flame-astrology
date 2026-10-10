# Hermenéutica posicional de factores · ALMAS 1.26

## Objeto y límite

Esta guía desarrolla los perfiles posicionales emitidos por M04 cuando se solicita 
`maximum_definition_context: true`. La ficha aporta descriptores calculados y referencias para la autoría. No genera prosa automática, contactos, raíces, independencia, scores, fases ni etiquetas ontológicas.

Orden de lectura recomendado:

`factor y función documentada → zodiaco/signo → casa y sistema → grado/decanato → regente(s) declarado(s) → condición/ubicación del regente → cadena de dispositores → geometría pertinente → alternativas y límites`.

La síntesis debe conservar el factor concreto, el sujeto, la carta o capa y el sistema de coordenadas. Un decanato de carta tropical, una posición dracónica, una casa natal, una superposición en la casa del otro y una carta compuesta son contextos distintos. No se trasladan las casas entre ellos.

## Qué calcula la ficha

Toda longitud eclíptica normalizada se divide en tres sectores de diez grados dentro del signo. El resultado 
`SIGN_TEN_DEGREE_SEGMENTS_V1` identifica el sector geométrico 1, 2 o 3; por sí mismo no asigna planeta regente ni significado. La asignación de regentes requiere `decan_rulership_policy` explícita, identificada por `policy_id` y con tres nombres de regente por signo. No existe un sistema de regencia predeterminado.

La regencia del signo sólo se resuelve a partir de `rulership_policy` declarada. `rulership_policy_id` conserva la identificación de esa tabla. M04 registra la ubicación de los factores en las cúspides suministradas y obtiene el sistema de casas de la procedencia del backend cuando está disponible. Si hay cúspides pero no consta el sistema, el número de casa se publica con `SYSTEM_UNSPECIFIED`; si faltan cúspides, se marca `NOT_EVALUABLE`.

La ficha recorre cadenas de dispositor a partir de las reglas expresas: declara autorregencia, ciclos, falta de posición o falta de regente. Las cadenas ramificadas se conservan cuando una política asigna más de un regente. Los `ruler_profile_refs` enlazan cada regente presente con su propia posición, casa y movimiento dentro de la misma carta, para que el informe pueda explicar la condición del anfitrión y su relación con el factor alojado. Un ciclo no se presenta como una resolución ni como una prueba de recepción mutua; ésta requiere una regla aparte y datos adecuados.

Los objetos con longitud eclíptica —planetas, asteroides, nodos, lotes, ángulos y puntos calculados— pueden recibir signo y sector geométrico si la longitud y el marco zodiacal están disponibles. Esta operación geométrica no implica que todos tengan naturaleza física ni que todos compartan dignidades o significados. Lotes conservan su fórmula y variante en la fuente canónica; estrellas deben mantener identidad, época y técnica; puntos desconocidos no reciben propiedades ausentes por analogía.

## Movimiento y retrogradación

La ficha normaliza el campo calculado explícito de movimiento en `DIRECT`, `RETROGRADE`, `NOT_APPLICABLE` o `NOT_EVALUABLE`. Los ángulos no se interpretan como retrógrados. Lotes y otros puntos sólo se consideran evaluables si la carta aporta un método de cálculo identificado. Una velocidad cero no acredita una estación: `station_state` permanece `NOT_EVALUATED` hasta que exista un criterio de velocidad y ventana validado. `interpretation_state: NOT_AUTHORED` significa que el motor no ha insertado un significado doctrinal en la ficha.

Al redactar, presentar las doctrinas sobre retrogradación como interpretaciones situadas y atribuidas, indicando tradición, obra y pasaje. Chris Brennan resume testimonios helenísticos que asocian en ciertos autores la retrogradación con demora, debilidad o impedimento, y algunos testimonios de estación con intensificación temporal; también advierte que el material conservado es limitado y ambiguo (*Hellenistic Astrology: The Study of Fate and Fortune*, 2017, pp. 206–207). No convertir esas variantes en una regla universal ni inferir estados psicológicos, voluntad, intención o conducta de una persona.

## Regencia y condición

La tradición helenística usa la metáfora de huésped y anfitrión para examinar cómo actúa un planeta en el domicilio de otro; la condición del regente y las casas en las que se encuentra pueden modificar la lectura (Brennan, 2017, pp. 232–237, con testimonio de Firmicus). ALMAS debe exponer primero la tabla de regencias elegida, su procedencia y el estado/ubicación calculados del regente. La interpretación se redacta después y no confunde regencia de signo, regencia de cúspide, dispositor moderno, regencia de decanato o recepción mutua.

No equiparar signos con casas por analogía signo-casa como regla histórica universal. Chris Brennan documenta que las tradiciones antiguas trataron signos y lugares como sistemas diferenciados; si se emplea una correspondencia moderna, declararla como uso contemporáneo, no como doctrina helenística.

## Protocolo epistemológico y editorial

Cada afirmación de un informe se etiquetará como dato calculado, técnica, doctrina explícita, uso contemporáneo o hipótesis de ALMAS. Las doctrinas citan fuente y pasaje; las hipótesis de ALMAS se identifican como tales. Si escuelas competidoras discrepan, se presentan por separado. La intensidad o exactitud de una posición no eleva por sí sola su fuerza metafísica.

La cobertura editorial puede declarar una ficha interpretada, excluida con motivo o no evaluable. Una ficha sin fuente especializada debe decirlo; el mito asociado al nombre de un asteroide o punto no sustituye una regla técnica. Ningún perfil posicional puede, aislado, demostrar reciprocidad, compatibilidad, origen monádico, split-soul, soulmate o twin flame.

## Base documental inicial

Brennan, Chris. *Hellenistic Astrology: The Study of Fate and Fortune*. Amor Fati Publications, 2017. Para la historia de los decanos egipcios y su transformación en divisiones zodiacales de diez grados, pp. 6–9; para la doctrina de decanos/faces y el esquema de regentes, pp. 279–285; para velocidad, retrogradación y estaciones, pp. 206–207; para domicilio y relación huésped-anfitrión, pp. 232–237. La obra es síntesis histórica/técnica contemporánea; sus citas de autores antiguos deben distinguirse de los textos primarios cuando ALMAS eleve una afirmación doctrinal.

Stephen Arroyo y Liz Greene pueden fundamentar lecturas psicológicas contemporáneas sólo cuando el pasaje concreto corresponda a la afirmación. Los textos cabalísticos, védicos y esotéricos del corpus se añaden a sus propias variantes doctrinales con autor, obra, edición y pasaje. No se trasladan automáticamente a la astrología helenística.
