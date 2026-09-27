# Método de tránsitos · TTRANSIT · ALMAS 1.20

## Finalidad

Este documento delimita la familia temporal `TTRANSIT` dentro de ALMAS.

Su función es establecer una base de método documentada para calcular y narrar, en un bloque posterior, contactos entre posiciones planetarias en movimiento y factores natales o estructurales ya existentes.

No implementa todavía el generador de tránsitos. Tampoco fija nuevos orbes, ventanas, pesos o reglas de agregación.

Fuentes de método:

- `astrodienst_transit`;
- `hand_planets_in_transit_2002`.

## Definición operativa

La estructura mínima de un tránsito en ALMAS es:

`factor en tránsito → aspecto → factor objetivo ya calculado → raíz existente → ventana temporal`.

Astrodienst define el tránsito como la relación angular que forma un planeta en movimiento con un factor de la carta natal y utiliza expresamente el lenguaje de activación o trigger cuando el aspecto alcanza exactitud.

Robert Hand sistematiza los cinco aspectos mayores de planetas en tránsito respecto a planetas natales y a factores angulares como Ascendente y Medio Cielo.

ALMAS adopta esa lógica como método técnico, no como validación científica de los significados astrológicos.

## Factores transitantes

El alcance inicial de TTRANSIT se limita a los cuerpos ya disponibles en el backend astronómico de producción y de uso ordinario en la fuente técnica:

- Sol;
- Luna;
- Mercurio;
- Venus;
- Marte;
- Júpiter;
- Saturno;
- Urano;
- Neptuno;
- Plutón.

La incorporación futura de otros factores requiere una justificación técnica separada.

## Factores objetivo

La primera implementación autónoma podrá comparar el factor transitante con:

- planetas natales ya calculados;
- Ascendente;
- Medio Cielo;
- otros puntos únicamente cuando exista una ruta canónica inequívoca y una regla técnica declarada.

No se reconstruyen posiciones natales desde texto narrativo ni desde eventos.

## Geometrías

El alcance inicial se restringe a los cinco aspectos mayores ya documentados por ALMAS:

- conjunción;
- sextil;
- cuadratura;
- trígono;
- oposición.

La geometría debe reutilizar el contrato de aspectos existente y no crear una segunda tabla de orbes.

Para interpretación usar `reference/aspect-geometry-hermeneutics.md`.

## Funciones planetarias

La función simbólica de cada planeta se resuelve mediante:

`reference/planetary-function-hermeneutics.md`.

Por tanto, un tránsito no se interpreta a partir del nombre de la familia `TTRANSIT`, sino de:

`función transitante → geometría → función objetivo → raíz activada`.

Ejemplo:

`SATURN → SQUARE → VENUS`

se lee como interacción temporal entre estructura/límite/tiempo y vínculo/valor, modulada por una cuadratura, dentro del tema de la raíz a la que la señal esté anclada.

No se traduce automáticamente como separación, compromiso, pérdida o duración.

## Relación con M26

El futuro generador TTRANSIT debe producir señales compatibles con M26.

Cuando el contacto concreto esté disponible, debe conservarse en:

`trigger_context`.

Campos mínimos:

- `trigger_point`;
- `target_point`;
- `relation`.

Campos contextuales cuando existan:

- `source_layer`;
- `target_layer`;
- `source_subject`;
- `target_subject`;
- `orb`;
- referencias técnicas adicionales.

M26 no recalcula estos datos y no utiliza `trigger_context` para cambiar fuerza, elegibilidad, deduplicación o IAT.

## Anclaje estructural

TTRANSIT no crea arquitectura.

Una señal sólo adquiere valor sustantivo en M26 cuando puede anclarse a una raíz estructural ya existente.

La dirección es:

`raíz existente → contacto de tránsito → activación temporal`.

No:

`tránsito llamativo → creación retrospectiva de una raíz`.

## Orbes y ventanas

Este documento no fija orbes ni duración de ventanas.

La implementación debe reutilizar políticas declaradas y versionadas. Si una regla de ventana u orb todavía no existe para TTRANSIT, el generador no debe inventarla silenciosamente.

La exactitud del contacto puede conservarse como dato técnico, pero una mayor exactitud no equivale a mayor probabilidad de un hecho real.

## Interpretación temporal

Una señal TTRANSIT puede indicar que un tema astrológico se vuelve más saliente en una ventana determinada.

Puede redactarse:

> Durante esta ventana, Saturno en tránsito activa mediante cuadratura la función venusina contenida en la raíz R..., concentrando temas de límite, estructura, valoración y vínculo.

No debe redactarse:

> Saturno cuadratura Venus hará que la pareja se separe.

El tránsito describe activación simbólica. Los hechos reales pertenecen a M27 cuando están documentados.

## Diferencia con otras familias

Este contrato sólo fundamenta `TTRANSIT`.

No debe extrapolarse automáticamente a:

- `TPROG` — progresiones secundarias;
- `TDIR` — arco solar u otras direcciones;
- `TECLIPSE`;
- `TREL`;
- `TATACIR`.

Cada familia requiere su propio método y fuentes antes de disponer de un generador autónomo.

## Límite epistemológico

Las fuentes registradas sostienen el método astrológico de tránsitos y su interpretación dentro de las escuelas citadas.

No sostienen:

- validación científica de los significados astrológicos;
- causalidad física demostrada entre tránsito y evento;
- predicción determinista;
- reciprocidad;
- consentimiento;
- decisión de otra persona;
- destino relacional;
- identificación automática de alma gemela, vínculo kármico o llama gemela.

El objetivo es más concreto: permitir que ALMAS calcule en el futuro una señal TTRANSIT reproducible y explique qué función temporal activa qué factor de una raíz ya existente.
