# Protocolo de síntesis interpretativa · ALMAS

## Finalidad

Este protocolo gobierna la transición entre el análisis canónico y una lectura astrológica desarrollada. No añade técnicas, scores, discriminadores ni ontologías. Su función es evitar que una ejecución rica en capas termine convertida en un inventario de aspectos, índices o advertencias metodológicas.

La unidad de sentido no es el aspecto aislado. Es la **arquitectura relacional** que emerge cuando varias capas describen una misma dinámica desde perspectivas distintas.

La secuencia interpretativa preferente es:

`configuración → patrón → dinámica → función evolutiva → correspondencia metafísica/doctrinal → diferencial → síntesis`.

La metodología cuantitativa interviene para graduar confianza, independencia y estabilidad. No ocupa el centro narrativo salvo que el usuario solicite una auditoría técnica.

## Arquitectura antes que etiqueta

Antes de valorar AF, KA, AG, LG o cualquier categoría multiaxial, la lectura debe poder explicar en lenguaje ordinario qué clase de vínculo describen las cartas.

Una buena síntesis debe responder, antes de etiquetar:

- qué hace que las dos cartas se reconozcan o se activen;
- qué patrones crean afinidad, tensión, espejo, transformación o continuidad;
- qué parte de la dinámica pertenece a los individuos y qué parte emerge sólo en la relación;
- qué motivos reaparecen en familias técnicas independientes;
- qué función evolutiva parece organizar el conjunto;
- qué dimensión metafísica puede compararse con fuentes concretas;
- qué alternativas continúan explicando la misma firma.

La categoría final resume esa arquitectura; no la sustituye.

## Lectura por capas

### 1. Sustrato individual · M02

La carta natal se interpreta primero como **estructura preexistente**. Debe identificar temas que cada sujeto trae antes del encuentro: necesidades relacionales, ejes de desarrollo, tensiones, recursos, patrones saturninos, plutonianos, quirónicos, nodales o de misión cuando sean relevantes.

Para la autoría posterior a M31, usar `canonical_analysis.natal_context` cuando esté disponible. Esta ruta proyecta el contexto ya calculado —signos de puntos, nodos, ángulos, casas, colocaciones y regencias— sin copiar fechas/horas natales ni recalcular la carta. Si la ruta no existe en un análisis importado o degradado, declarar el sustrato natal como no disponible en vez de reconstruirlo silenciosamente desde otros datos.

Aplicar `reference/natal-substrate-hermeneutics.md`: `función planetaria → signo/modo → casa natal/campo → regencia declarada/conexión → tema individual`. La sinastría se redacta después como activación de esa estructura previa, no como origen retroactivo de ella.

Pregunta interpretativa:

> ¿Qué tema ya existía en cada persona antes de que apareciera la otra?

Este paso es esencial para distinguir tarea individual de función específicamente diádica y para evitar atribuir a la pareja todo aquello que ya estaba inscrito en cada carta.

### 2. Geometría interpersonal · M03–M06

La sinastría, nodos, ángulos, casas, regencias, declinaciones y antiscios describen **cómo una estructura entra en el campo de la otra**.

La lectura debe desarrollar:

- contactos entre luminarias y personales como lenguaje de afinidad, reconocimiento y respuesta emocional;
- nodos y sus regentes como ejes de dirección, memoria simbólica o continuidad cuando forman redes y no señales aisladas;
- ángulos y casas como zonas de encarnación concreta del vínculo;
- Saturno, Plutón, Quirón, Urano y Neptuno según la función real que desempeñen en las raíces;
- paralelos/contra-paralelos como refuerzo de resonancias que pueden no ser evidentes por longitud;
- antiscios/contra-antiscios como simetrías complementarias o de contraste, sin elevarlos por sí solos a prueba ontológica.

Fuentes técnicas registradas:

- `davison_synastry_1983` documenta comparación de cartas, aspectos planetarios cruzados e intercambios de casas como componentes del análisis relacional;
- `sakoian_acker_human_relationships_1976` aporta una fuente de método centrada en comparación horoscópica y combinaciones planetarias;
- `arroyo_relationships_life_cycles_1993` fundamenta el uso interpretativo de comparación de cartas y casas desde una escuela psicológica relacional;
- `astrodienst_synastry_houses` documenta directamente que la sinastría muestra dónde caen los planetas de una carta en las casas de la otra y que esa ocupación enfatiza los temas de la casa para su propietario;
- `astrodienst_intro_houses` aporta las significaciones generales de las doce casas como áreas de vida donde se expresan las funciones planetarias;
- `boehrer_declination_other_dimension` documenta el uso moderno de declinaciones, paralelos y contraparalelos como dimensión interpretativa adicional;
- `firmicus_mathesis_2_29_antiscia` aporta una fuente histórica primaria para el sistema de antiscios y su correspondencia recíproca de signos/grados.

Las fuentes de M03–M04 permiten desarrollar dinámica interpersonal, combinaciones concretas y zonas de experiencia activadas por casas. Para `house_overlays`, aplicar además `reference/house-overlay-hermeneutics.md`: el punto pertenece al sujeto fuente, la casa al sujeto receptor y la geometría de la raíz indica cómo se articula la interacción. Las fuentes de M05–M06 explican dimensiones distintas de los aspectos por longitud. Ninguna de estas fuentes convierte una técnica relacional en evidencia ontológica autónoma ni autoriza a inferir destino, reciprocidad o tipo de alma a partir de una configuración aislada.

### Funciones planetarias concretas

Cuando `canonical_analysis.evidence[].concrete_contacts` preserve planetas concretos, usar `reference/planetary-function-hermeneutics.md` antes de resumir la raíz mediante un motivo.

Cuando `relation_ids` preserve una geometría longitudinal mayor, aplicar además `reference/aspect-geometry-hermeneutics.md`. La función planetaria explica **qué** interactúa; la geometría explica **cómo**: conjunción concentra, oposición polariza, cuadratura fricciona, trígono facilita y sextil abre una vía de cooperación.

La secuencia es:

`función planetaria A → función planetaria B → geometría → casa receptora si existe → raíz → motivo`.

Esto evita que contactos diferentes terminen narrados con el mismo párrafo genérico. Por ejemplo, una raíz Venus–Plutón debe explicar primero qué ocurre entre valoración/vínculo e intensidad/poder/transformación; una raíz Mercurio–Júpiter debe explicar pensamiento/comunicación frente a expansión/significado. El motivo recurrente se formula después.

Quirón, nodos, ángulos y casas conservan sus guías especializadas.

### Extremos concretos de ejes y nodos

Cuando `canonical_analysis.evidence[].concrete_contacts` preserve ASC/DSC, MC/IC, Nodo Norte/Nodo Sur o Vertex/Anti-Vertex, usar `reference/angular-nodal-endpoint-hermeneutics.md`.

La normalización M17 evita duplicar raíces, pero la autoría debe recuperar el polo concreto:

- ASC: presencia, autoexpresión e interfaz inmediata;
- DSC: alteridad, pareja y proyección;
- IC: raíces, intimidad y fundamento privado;
- MC: dirección pública, vocación y meta;
- Nodo Sur: familiaridad, patrón adquirido o pasado simbólico;
- Nodo Norte: dirección de desarrollo o territorio emergente;
- Vertex: punto sensible de encuentro en la práctica moderna, sin convertir “fated” en hecho objetivo.

La diferencia entre polos modifica significado, no scoring ni independencia.

Pregunta interpretativa:

> ¿Qué activa cada persona en la otra y mediante qué dinámica relacional?

No limitarse a nombrar contactos. Explicar el circuito: quién activa, qué función toca y qué respuesta relacional puede simbolizar.

### 3. Campo emergente de la relación · M07–M09

La compuesta y el Davison se leen como dos perspectivas de un **campo relacional emergente**. No deben narrarse como confirmaciones totalmente independientes entre sí, pero sí compararse hermenéuticamente.

La compuesta ayuda a describir la organización simbólica interna del vínculo. El Davison sitúa esa relación en una carta espacio-temporal. La consonancia entre ambas permite preguntar qué temas sobreviven al cambio de construcción.

Fuentes de método registradas:

- `townley_composite_charts_2000` fundamenta el uso moderno de la carta compuesta como técnica de relación y su lectura integrada con natal y sinastría;
- `davison_synastry_1983` documenta la comparación de cartas y el `Relationship Horoscope` como carta única de la relación.

Estas fuentes respaldan el método y su vocabulario interpretativo. No convierten la familia `RELCHART` en prueba de origen compartido, contrato álmico, alma gemela o llama gemela. Compuesta y Davison deben conservar sus diferencias de construcción aunque ALMAS las agrupe en una misma familia de dependencia para no inflar independencia.

Pregunta interpretativa:

> ¿Qué existe en la relación que no se explica sólo por sumar las dos cartas individuales?

Cuando un motivo sinástrico reaparece en la familia RELCHART, desarrollar el significado de esa continuidad: el patrón no sólo conecta a los individuos, también organiza el campo conjunto.

Para autoría posterior a M31, usar `canonical_analysis.relationship_field` cuando exista y aplicar `reference/relationship-field-hermeneutics.md`. Distinguir tres niveles: `sustrato individual → activación sinástrica → campo emergente`. Los aspectos internos de `field_context` son contexto de autoría y no nuevas raíces. La compuesta no tiene casas en M07; el Davison puede exponer `house_placements` cuando M08 produjo doce cúspides válidas; la autoría consume esa asignación y no la recalcula.

### 4. Reencuadre nodal y capa dracónica · M10–M12

La dracónica se interpreta como **reencuadre nodal** de la carta, no como prueba automática de vidas pasadas, contrato o identidad del alma.

Para autoría posterior a M31 usar `canonical_analysis.draconic_context` cuando exista. Esta ruta es una proyección de M10–M12 ya calculados: `authoring_projection_only=true` y `creates_additional_evidence=false`.

Fuentes de método registradas:

- `crane_draconic_astrology_1987`: fuente moderna identificada para uso interpretativo de cartas dracónicas;
- `blaquier_draconic_astrology_2017_2021`: fuente primaria verificada para el procedimiento que lleva el Nodo Norte tropical a 0° Aries y desplaza el resto de posiciones por el mismo arco.

#### M10 · carta dracónica individual

`draconic_context.individual` conserva para cada sujeto las posiciones ya transformadas, su signo y grado dentro del signo, además del `source_longitude` tropical. No recalcular la dracónica durante la autoría.

Leer:

`función natal → desplazamiento nodal → signo dracónico → diferencia/repetición respecto del patrón tropical → tema evolutivo`.

La pregunta no es «¿cuál es la verdadera carta?», sino:

> ¿Cómo cambia el énfasis simbólico de una función cuando la carta se reordena tomando el Nodo Norte como origen?

Una repetición entre tropical y dracónica puede intensificar hermenéuticamente un tema; una diferencia puede mostrar otro modo de organizarlo. Ninguna de las dos situaciones prueba por sí sola una memoria preencarnatoria.

#### M11 · natal ↔ dracónica

`draconic_context.natal_cross` conserva los contactos en ambas direcciones.

La dirección es sustantiva:

- natal A → dracónica B: una función manifiesta de A toca una función reencuadrada de B;
- natal B → dracónica A: el circuito inverso y no necesariamente equivalente.

Aplicar primero función planetaria y geometría del aspecto. Después preguntar si el mismo par o motivo aparece en sinastría, campo relacional o raíces independientes.

Una formulación válida debe especificar **quién activa qué**. Evitar frases genéricas como «hay conexión dracónica» cuando los datos permiten describir el circuito concreto.

#### M12 · dracónica ↔ dracónica

`draconic_context.draconic_cross` permanece `corroborative_only=true`.

Sirve para observar afinidades o tensiones dentro de dos marcos ya reencuadrados nodalmente. Puede enriquecer una recurrencia previamente establecida, pero no cuenta como confirmación astronómicamente independiente ni crea una raíz adicional por sí sola.

Pregunta interpretativa:

> ¿Qué patrón tropical o relacional reaparece, cambia de forma o se profundiza cuando ambas cartas se leen desde el eje nodal?

La secuencia recomendada es:

`tropical individual → sinastría → M10 reencuadre → M11 dirección natal↔dracónica → M12 corroboración → raíces/motivos → función evolutiva`.

Sólo después de explicar esta arquitectura puede abrirse un comparandum metafísico —continuidad, memoria simbólica, contrato, misión— y siempre dentro del techo de la fuente doctrinal correspondiente.

### 5. Lotes y capas simbólicas secundarias · M13–M14

M13 y M14 no cumplen la misma función y no deben narrarse con el mismo peso.

#### M13 · Fortuna y Espíritu/Daimon

Cuando exista `canonical_analysis.lots_context`, consumir la salida ya calculada de M13. La proyección conserva fórmula, secta, longitud, signo, grado dentro del signo, casa natal, fuente principal y fuente corroborativa.

La baseline `ALMAS_HELLENISTIC_LOTS_V1` utiliza únicamente Fortuna y Espíritu porque son los lotes cuya fórmula y genealogía están fijadas en el corpus.

Fuentes históricas:

- `paulus_alexandrinus_introductory_matters_ch23`: fórmula de Fortuna/Espíritu con inversión por secta;
- `vettius_valens_anthology_lots`: uso histórico de ambos lotes y distinción interpretativa entre ellos.

En Valens:

- Fortuna informa sobre asuntos corporales y trabajo de las manos;
- Daimon/Espíritu y su regente informan sobre asuntos intelectuales/espirituales y actividades de dar y recibir;
- signo/lugar y regentes cualifican la forma concreta de la actividad y la fortuna.

La secuencia de lectura es:

`lote → significado histórico documentado → signo → casa → resonancia con sustrato natal → posible eco en arquitectura relacional`.

El signo describe el modo cualitativo y la casa el campo de experiencia. No convertir automáticamente:

- Espíritu/Daimon → alma superior;
- Espíritu/Daimon → misión preencarnatoria;
- Fortuna → destino inevitable;
- una coincidencia de lote → contrato o tipo de alma.

Un lote merece entrar en S10 sólo cuando aclare un motivo ya desarrollado. En caso contrario permanece en S04/S05 o en fuentes/anexos como contexto histórico.

Pregunta interpretativa:

> ¿El lugar donde se sitúan Fortuna o Espíritu ayuda a comprender un tema individual que después la relación activa o reorganiza?

#### M14 · capa simbólica secundaria

M14 ya entra en M15 como familia `SECONDARY` con `support_only=true`. No necesita una segunda proyección canónica para autoría.

Asteroides u otros puntos secundarios sólo deben aparecer cuando:

1. el contacto sobrevivió como apoyo de una raíz/motivo principal;
2. su significado está documentado por una fuente identificada;
3. añade un matiz que no puede expresarse mejor desde planetas, nodos, ángulos o cartas relacionales.

Pregunta interpretativa:

> ¿Qué matiz aporta esta capa a una arquitectura que ya existe sin depender de ella?

No convertir lotes, asteroides, atacires u otras técnicas auxiliares en el centro de la interpretación si las capas estructurales no sostienen el mismo motivo.

### 6. Raíces y motivos recurrentes · M15–M18

Éste es el punto donde la lectura deja de ser una colección de técnicas y se convierte en **arquitectura**.

Cada raíz independiente debe traducirse a una frase de significado. Después, los motivos recurrentes deben explicar qué tema reaparece en familias distintas sin confundir recurrencia semántica con multiplicación artificial de evidencia.

En la salida canónica, la resolución root-first parte de `canonical_analysis.evidence`: `concrete_contacts` conserva los puntos y extremos reales que produjeron cada contacto retenido; `point_ids` resume las funciones después de normalizar ejes, `relation_ids` resume la geometría, `root_key` conserva la identidad estructural deduplicada, y `dependency_families` + `independent_family_count` permiten saber si la raíz reaparece en más de una familia. `max_exactness` calibra precisión geométrica; no aporta significado por sí misma. Cuando `house_overlays` está presente, añade el **escenario experiencial** de la raíz —qué punto de un sujeto cae en qué casa del otro— y permite formular la dirección espacial del impacto sin recalcular casas durante la autoría. La casa contextualiza; no crea una segunda evidencia ni prueba reciprocidad. Dirección subjetiva, vivencia bilateral o ángulos agrupados sólo se desarrollan si están disponibles de forma inequívoca en otra ruta canónica autorizada.

Ejemplos de formulación:

- una raíz nodal-luminar puede narrarse como reconocimiento orientado a dirección vital;
- una raíz Venus–Plutón puede describir magnetismo transformativo y necesidad de regenerar el modo de vincularse;
- una raíz Saturno–Nodo puede expresar continuidad, deuda, compromiso, límite o estructuración según el resto del patrón;
- una recurrencia Sol/Luna/ángulos puede sugerir coherencia identitaria-emocional del campo relacional.

Pregunta interpretativa:

> ¿Cuál es el pequeño número de temas que explica la mayor parte de la relación?

La síntesis debe preferir tres o cuatro motivos bien desarrollados antes que veinte contactos enumerados.

Antes de llegar al motivo, cada raíz con planetas identificables debe pasar por `reference/planetary-function-hermeneutics.md`. La prueba editorial es que el párrafo deje de ser intercambiable: Venus–Plutón, Mercurio–Júpiter y Luna–Saturno deben producir dinámicas materialmente distintas.

Para desarrollar el significado de los nueve motivos primarios y sus combinaciones, usar `reference/semantic-motif-hermeneutics.md`. Ese documento no cambia la clasificación M18: traduce los motivos existentes a dinámica, función evolutiva, comparanda metafísicos y límites inferenciales.

### 7. Función evolutiva

Una vez descrita la arquitectura, inferir su **función simbólica** dentro de los techos permitidos.

Las funciones pueden incluir afinidad, aprendizaje, espejo, catálisis, reparación, iniciación, transformación, integración, servicio, liberación o cierre.

La función se deriva de la combinación de raíces, motivos y dinámica relacional; no de una etiqueta espiritual previa.

Pregunta interpretativa:

> ¿Para qué parece operar esta arquitectura en la experiencia de ambos?

Aquí la lectura puede ser evolutiva y esotérica, siempre diferenciando lo calculado de la síntesis ALMAS.

### 8. Activación temporal · M26–M27

La temporalidad responde a **cuándo y cómo se activa** una estructura previa.

Debe enlazarse explícitamente con raíces o motivos ya descritos:

`raíz estructural → activador temporal → manifestación simbólica/documental`.

Pregunta interpretativa:

> ¿Qué parte de la arquitectura está siendo activada ahora y qué proceso simboliza esa activación?

Evitar convertir una activación intensa en creación retroactiva del vínculo o en predicción obligatoria de decisiones futuras.

### 9. Hermenéutica metafísica y fuentes · M28

La doctrina entra cuando la arquitectura ya es comprensible astrológicamente.

Para cada correspondencia relevante:

1. identificar el motivo astrológico concreto;
2. identificar el concepto doctrinal comparable;
3. citar la fuente o tradición;
4. explicar qué significado añade;
5. declarar qué no establece esa fuente;
6. distinguir doctrina histórica de síntesis ALMAS.

Ejemplo de secuencia:

`recurrencia nodal + continuidad multitécnica → modelo de continuidad → comparación con gilgul/zivug/contrato según proceda → límites de equivalencia`.

La fuente debe ayudar a **interpretar** el patrón, no aparecer como bibliografía decorativa al final.

### 10. Diagnóstico diferencial

El diferencial debe responder por qué varias ontologías pueden producir la misma firma y qué datos favorecen unas interpretaciones frente a otras.

La contraevidencia se integra aquí de forma proporcional. No debe repetirse como advertencia en cada sección.

Pregunta interpretativa:

> ¿Qué explicación describe mejor la arquitectura y qué explicaciones siguen abiertas?

Cuando no existe un discriminador válido, la conclusión puede ser rica y específica sobre función, continuidad, polaridad o misión aunque el origen último permanezca indeterminado.

### 11. Síntesis final

La síntesis final debe ser capaz de sostenerse sin cifras.

Primero expresar en prosa:

- naturaleza del vínculo;
- motivos dominantes;
- función evolutiva;
- profundidad o continuidad sugerida;
- papel de la polaridad;
- dimensión de misión o contrato si procede;
- modelo o modelos metafísicos compatibles;
- principal incertidumbre restante.

Después, si aporta claridad, utilizar IEM, IDD, IRC, ICC, ICE o IAT como calibradores secundarios.

## Gramática de transición

Para evitar párrafos fragmentarios, usar transiciones que conecten capas.

De dato a patrón:

> Este contacto no actúa de forma aislada; reaparece en...

De patrón a dinámica:

> La repetición convierte el motivo en una dinámica central del vínculo: ...

De dinámica a función:

> En términos evolutivos, esta dinámica parece operar como...

De función a doctrina:

> Este motivo puede compararse, dentro de la tradición X, con...

De doctrina a límite:

> La fuente permite interpretar X, pero no establece Y.

De diferencial a síntesis:

> Por ello, la arquitectura sostiene con mayor claridad..., mientras que... permanece compatible/no diferenciable.

## Prioridad narrativa

En una lectura general o libro, la extensión debe favorecer aproximadamente este orden de protagonismo:

1. arquitectura y motivos astrológicos;
2. dinámica relacional y función evolutiva;
3. hermenéutica metafísica y fuentes;
4. diagnóstico diferencial;
5. temporalidad cuando sea relevante;
6. método, índices y robustez como soporte.

No convertir este orden editorial en una fórmula cuantitativa rígida. Su propósito es impedir que el aparato de validación desplace el contenido que el lector busca comprender.

## Regla de profundidad

Una sección no se considera desarrollada sólo porque enumere técnicas disponibles. Debe producir al menos una **proposición interpretativa integrada** que conecte:

`evidencia astrológica → motivo → dinámica → significado`.

Cuando haya fuentes pertinentes, añadir:

`→ correspondencia doctrinal → límite de la correspondencia`.

## Relación con authored_report

Este protocolo se aplica principalmente a:

- S01 · Síntesis ejecutiva;
- S04 · Arquitectura estructural;
- S05 · Capas relacionales y cruzadas;
- S06 · Diferencial y contraevidencia;
- S07 · Activación temporal;
- S09 · Doctrina comparada;
- S10 · Síntesis final.

S02, S03 y S08 sostienen la confianza metodológica, pero no deben dominar el texto salvo en informes de auditoría.

S11 conserva trazabilidad y bibliografía. Las fuentes esenciales para comprender un significado deben aparecer también en el cuerpo interpretativo correspondiente.

## Criterio de calidad interpretativa

Una lectura ALMAS mejora cuando puede explicar una relación sin depender de una lista de aspectos ni de una etiqueta final.

La pregunta de control es:

> Si se eliminaran los nombres AF, KA, AG y LG, ¿seguiría siendo comprensible qué clase de vínculo describen las cartas, cómo funciona y qué significado metafísico puede compararse con las fuentes?

Si la respuesta es no, la autoría todavía no está suficientemente desarrollada.
