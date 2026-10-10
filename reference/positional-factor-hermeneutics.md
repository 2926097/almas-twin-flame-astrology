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

La regencia del signo sólo se resuelve a partir de `rulership_policy` declarada. Para comenzar con los domicilios de los siete planetas visibles puede cargarse `load_hellenistic_domicile_rulership_policy()` desde `almas_tfa.positional_hermeneutics`; pasar sus campos `rulers_by_sign`, `policy_id` y `source_refs` como `rulership_policy`, `rulership_policy_id` y `rulership_policy_source_refs`. Esta variante no asigna co-regencias modernas a Urano, Neptuno o Plutón. M04 registra la ubicación de los factores en las cúspides suministradas y obtiene el sistema de casas de la procedencia del backend cuando está disponible. Si hay cúspides pero no consta el sistema, el número de casa se publica con `SYSTEM_UNSPECIFIED`; si faltan cúspides, se marca `NOT_EVALUABLE`.

Para los decanatos se puede cargar `load_hellenistic_chaldean_decan_policy()`. Es una variante histórica de faces: primer decanato de Aries regido por Marte y secuencia posterior en orden caldeo descendente. Brennan la describe hacia el siglo I y advierte que su extensión interpretativa helenística es incierta (2017, pp. 279–282). `decan_rulership_policy` es optativa; activarla registra una variante elegida, no una dignidad universal. El perfil conserva `source_refs`. La propuesta de Halevi de usar subregencias cabalísticas por decanato pertenece a una escuela moderna distinta: describe Leo a 23° como tercer decanato regido por Marte y Leo a 15° como subregido por Júpiter (*The Anatomy of Fate*, 1978, p. 73). No se combina con las faces caldeas.

La ficha recorre cadenas de dispositor a partir de las reglas expresas: declara autorregencia, ciclos, falta de posición o falta de regente. Las cadenas ramificadas se conservan cuando una política asigna más de un regente. Los `ruler_profile_refs` enlazan cada regente presente con su propia posición, casa y movimiento dentro de la misma carta, para que el informe pueda explicar la condición del anfitrión y su relación con el factor alojado. Un ciclo no se presenta como una resolución ni como una prueba de recepción mutua; ésta requiere una regla aparte y datos adecuados.

Los objetos con longitud eclíptica —planetas, asteroides, nodos, lotes, ángulos y puntos calculados— pueden recibir signo y sector geométrico si la longitud y el marco zodiacal están disponibles. Esta operación geométrica no implica que todos tengan naturaleza física ni que todos compartan dignidades o significados. Lotes conservan su fórmula y variante en la fuente canónica; estrellas deben mantener identidad, época y técnica; puntos desconocidos no reciben propiedades ausentes por analogía.

## Movimiento y retrogradación

La ficha normaliza el campo calculado explícito de movimiento en `DIRECT`, `RETROGRADE`, `NOT_APPLICABLE` o `NOT_EVALUABLE`. Los ángulos no se interpretan como retrógrados. Lotes y otros puntos sólo se consideran evaluables si la carta aporta un método de cálculo identificado. Una velocidad cero no acredita una estación: `station_state` permanece `NOT_EVALUATED` hasta que exista un criterio de velocidad y ventana validado. `interpretation_state: NOT_AUTHORED` significa que el motor no ha insertado un significado doctrinal en la ficha.

Al redactar, presentar las doctrinas sobre retrogradación como interpretaciones situadas y atribuidas, indicando tradición, obra y pasaje. Brennan resume testimonios helenísticos divergentes: Valens, en contexto de profecciones, vincula la estación retrógrada con demoras de expectativas, acciones, ganancias y empresas; asocia la fase retrógrada con debilitamiento y obstáculos, mientras la estación directa remueve impedimentos. Paulus agrupa retrógrados con planetas bajo rayos o declinantes y los describe como menos potentes o eficaces. Un fragmento atribuido con duda a Petosiris interpreta algunas estaciones como intensificación temporal. Son testimonios escasos, de contextos técnicos específicos, no una regla natal universal (Brennan, 2017, pp. 206–207; Valens, *Anthologies* 4.14.4, trad. Riley, p. 82; Paulus, *Introduction* 14). Presentar variantes por separado y no inferir estados psicológicos, voluntad, intención o conducta de una persona.

Arroyo (1975) ofrece una síntesis astrológica psicológica contemporánea para relacionar planetas, signos y casas; su enfoque no constituye evidencia de que esa lectura pertenezca a la tradición helenística ni es fuente suficiente para doctrinas de retrogradación o significados de asteroides particulares. Greene (*Jung’s Studies in Astrology*, 2018, pp. 44–48) documenta corrientes modernas consultadas por Jung y la presencia de tablas de decanos, regentes y casas en escuelas distintas; úsese como historia de recepción, no como diccionario técnico de posiciones. Berg, Sepharial, Dobin y Halevi representan corrientes cabalísticas/esotéricas diferentes: cada obra debe citarse sólo para las reglas que efectivamente exponga. Los archivos adjuntos de Sepharial y Dobin son escaneos sin texto OCR verificable; sus tablas no se activan hasta cotejar visualmente páginas concretas. La guía no asigna significados genéricos por el nombre mitológico de un asteroide: cada cuerpo requiere una fuente interpretativa específica y se identifica como uso moderno o hipótesis cuando corresponda.

## Regencia y condición

La tradición helenística usa la metáfora de huésped y anfitrión para examinar cómo actúa un planeta en el domicilio de otro; la condición del regente y las casas en las que se encuentra pueden modificar la lectura (Brennan, 2017, pp. 232–237, con testimonio de Firmicus). ALMAS debe exponer primero la tabla de regencias elegida, su procedencia y el estado/ubicación calculados del regente. La interpretación se redacta después y no confunde regencia de signo, regencia de cúspide, dispositor moderno, regencia de decanato o recepción mutua.

No equiparar signos con casas por analogía signo-casa como regla histórica universal. Chris Brennan documenta que las tradiciones antiguas trataron signos y lugares como sistemas diferenciados; si se emplea una correspondencia moderna, declararla como uso contemporáneo, no como doctrina helenística.

## Protocolo epistemológico y editorial

Cada afirmación de un informe se etiquetará como dato calculado, técnica, doctrina explícita, uso contemporáneo o hipótesis de ALMAS. Las doctrinas citan fuente y pasaje; las hipótesis de ALMAS se identifican como tales. Si escuelas competidoras discrepan, se presentan por separado. La intensidad o exactitud de una posición no eleva por sí sola su fuerza metafísica.

La cobertura editorial puede declarar una ficha interpretada, excluida con motivo o no evaluable. Una ficha sin fuente especializada debe decirlo; el mito asociado al nombre de un asteroide o punto no sustituye una regla técnica. Ningún perfil posicional puede, aislado, demostrar reciprocidad, compatibilidad, origen monádico, split-soul, soulmate o twin flame.

## Base documental inicial

Brennan, Chris. *Hellenistic Astrology: The Study of Fate and Fortune*. Amor Fati Publications, 2017. Historia de decanos, pp. 6–9; movimiento, retrogradación y estaciones, pp. 206–207; domicilios y huésped-anfitrión, pp. 232–237; decanos/faces y esquemas de regentes, pp. 279–285. Es una síntesis histórica/técnica contemporánea; las citas de autores antiguos se distinguen de los textos primarios.

Arroyo, Stephen. *Astrology, Psychology, and the Four Elements: An Energy Approach to Astrology & Its Use in the Counseling Arts*. CRCS Publications, 1975. Fuente de astrología psicológica moderna y síntesis de factores.

Greene, Liz. *Jung’s Studies in Astrology: Prophecy, Magic, and the Qualities of Time*. Routledge, 2018. Contexto histórico para las corrientes modernas consultadas por Jung; no es un manual de delineación por decanato.

Kenton, Warren (Z’ev ben Shimon Halevi). *The Anatomy of Fate: Kabbalistic Astrology*. Rider, 1978, p. 73. Fuente de una variante moderna de subregencias cabalísticas por decanato; mantener separada de la face helenística.

Las traducciones adjuntas de Berg y las ediciones escaneadas de Sepharial y Dobin requieren que cada regla usada se cite a capítulo y página verificados. Las obras de Krishnamurti, Watts, Cayce y Dispenza, y el artículo de biología/mitocondrias, no se usan como fuentes técnicas para posiciones astrológicas.
