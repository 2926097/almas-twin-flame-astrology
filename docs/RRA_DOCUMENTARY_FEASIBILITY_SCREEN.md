# RRA · Primer cribado de factibilidad documental

Fecha de consulta: 3 de octubre de 2026. Vinculado al protocolo candidato 0.1 de la PR #86. Estado: **DOCUMENTARY_PILOT_ONLY**. Se han examinado cuatro vínculos públicos para comprobar la disponibilidad de documentación. Ninguno se admite en una cohorte confirmatoria ni en el holdout. No se han calculado cartas, retornos, puntuaciones o resultados astrológicos.

## Alcance, selección y resultado

Este primer panel de conveniencia comprende los matrimonios públicos examinados de Isabel II, Carlos III y Guillermo: Isabel–Felipe, Carlos–Diana, Carlos–Camilla y Guillermo–Catherine. La elección se basa en la disponibilidad de biografías institucionales y documentación ceremonial. No es una muestra aleatoria, una búsqueda exhaustiva de parejas ni una selección por firmas astrológicas. La decisión pertenece al diseño E del proyecto y este cribado no se presenta como preregistrado.

La documentación permite identificar acontecimientos y, para tres de las siete personas, horas natales declaradas en fuentes institucionales. Las fuentes examinadas no proporcionan una hora natal verificable para los otros cuatro sujetos. Una hora publicada con minutos no demuestra una incertidumbre física de medio minuto, ni sustituye el documento natal original. No se han suplido horas con mediodía, rectificación o valores de catálogos.

El panel sirve para desarrollar criterios documentales, pero no satisface las condiciones para ejecutar la validación relacional externa. Todos los candidatos quedan reservados al piloto y excluidos del holdout de la misma evaluación. Los hechos encontrados no constituyen correspondencias RRA: para ello faltan, entre otros elementos, arquitectura previa, entradas verificadas, ventanas observacionales y controles admisibles.

## Vínculos y fuentes examinadas

Para Isabel II–Felipe, la biografía oficial de Isabel señala nacimiento el 21 de abril de 1926 a las 02:40 en 17 Bruton Street, Londres. La nota oficial «50 facts about The Duke of Edinburgh», de 25 de enero de 2002, da para Felipe fecha y lugar de nacimiento —10 de junio de 1921, Mon Repos, Corfú—, sin hora en el pasaje consultado. La página oficial sobre la boda registra el anuncio del compromiso el 9 de julio de 1947 y la ceremonia a las 10:30 del 20 de noviembre de 1947, en Westminster Abbey. Se conserva la hora ceremonial declarada, no un instante acreditado de consentimiento o inscripción matrimonial. Falta verificar la hora de Felipe, los límites de precisión y la reducción temporal histórica; la boda y el anuncio son hechos distintos.

Para Carlos III–Diana, la biografía oficial del rey declara nacimiento el 14 de noviembre de 1948 a las 21:14 en Buckingham Palace. La biografía institucional de Diana documenta nacimiento el 1 de julio de 1961 en Park House, cerca de Sandringham, sin hora en el texto consultado. Ambas fuentes permiten fechar la boda el 29 de julio de 1981 en St Paul’s Cathedral; no se adopta una hora de boda no documentada en esos pasajes. La página de Diana identifica el anuncio del compromiso del 24 de febrero de 1981 y el divorcio del 28 de agosto de 1996. El anuncio de separación del 9 de diciembre de 1992 queda corroborado mediante Hansard. El encabezado del debate señala 15:30: corresponde al inicio de la declaración parlamentaria y no acredita cuándo se decidió o comenzó la separación. Falta una fuente natal horaria suficiente de Diana y una definición previa de los eventos que se estudiarían.

Para Carlos III–Camilla, las biografías institucionales documentan la boda civil del 9 de abril de 2005 en Guildhall, Windsor. La biografía de Camilla identifica nacimiento el 17 de julio de 1947 en King’s College Hospital, Londres, sin aportar hora en el pasaje examinado. La boda civil y el posterior servicio de oración y dedicación son actos distintos; no se fusionan ni se intercambian sus relojes. Esta pareja reutiliza a Carlos y no forma una unidad independiente respecto de Carlos–Diana. La ausencia de una hora de Camilla documentada en el corpus examinado sigue siendo un bloqueo, no una afirmación de que no exista ninguna fuente válida fuera del corpus.

Para Guillermo–Catherine, la biografía oficial de Guillermo declara nacimiento el 21 de junio de 1982 a las 21:03 en St Mary’s Hospital, Paddington, Londres. La de Catherine da el 9 de enero de 1982 en Royal Berkshire Hospital, Reading, sin hora en el pasaje examinado. La página oficial de la boda registra el 29 de abril de 2011 a las 11:00, en Westminster Abbey. GOV.UK publicó el 27 de abril una noticia anunciando la boda del día 29: el día de publicación no sustituye la fecha del acontecimiento. La misma página oficial distingue el anuncio del compromiso, el 16 de noviembre de 2010, del compromiso durante unas vacaciones en Kenia el mes anterior, cuyo día concreto no se documenta ahí. No se convierte el anuncio en fecha exacta del compromiso.

## Dependencia, negativos y precisión

Al agrupar sólo personas reutilizadas hay tres componentes: Isabel–Felipe, los dos vínculos de Carlos y Guillermo–Catherine. Este recuento topológico no acredita tres unidades estadísticamente independientes. La pertenencia al mismo entorno familiar, institucional y documental añade un bloque común que requeriría tratamiento específico. El panel no basta para representar la diversidad de relaciones previstas por ALMAS.

Las páginas de la Casa Real constituyen una familia institucional de fuentes; varias biografías no cuentan automáticamente como corroboraciones independientes. Hansard acredita el acto parlamentario que registra, pero reproduce un comunicado del Palacio. GOV.UK acredita que existió una noticia prospectiva de la boda, sin convertir esa noticia en registro del instante en que se formalizó el matrimonio.

Los horarios citados se conservan como datos locales declarados por las fuentes. No se han asignado offsets, coordenadas numéricas, márgenes de incertidumbre o instantes UTC. Una referencia geográfica nominal no es una coordenada geocodificada. Una fecha sin hora debe mantenerse como intervalo hasta aplicar una política temporal explícita; no se ha serializado como medianoche ni como una observación exacta.

Ninguna de las páginas examinadas proporciona una cronología continua que permita afirmar ausencia de acontecimientos relacionales en todas las fechas control propuestas. Los calendarios ceremoniales y las agendas públicas no equivalen a observación completa de la vida relacional. Por ello no se ha generado una muestra de controles negativos, ni se han definido fechas «sin evento» por ausencia de noticias.

Las búsquedas devolvieron también agregadores astrológicos, con afirmaciones horarias. No se abrieron sus cartas ni se adoptaron sus horarios como datos acreditados. Se registra esa exposición bibliográfica incidental sin afirmar un cegamiento absoluto: no se han inspeccionado posiciones, aspectos, clasificaciones o resultados de estos vínculos. La comprobación local de nombres en el repositorio no encontró un expediente de desarrollo de estas parejas; esa búsqueda no certifica ausencia de exposición histórica en otros sistemas.

## Consecuencia para el protocolo

El resultado es un cribado documental útil y una cohorte confirmatoria todavía no identificada. Los cuatro vínculos son `SCREENED_PILOT_ONLY`, con `holdout_eligible=false`. No se eliminan los bloqueos de muestra, controles, intercambiabilidad, acuerdo entre codificadores, runner o preregistro.

Antes de buscar el holdout habrá que concretar la política para horas faltantes, fechas con precisión de día y acontecimientos anunciados, con análisis de sensibilidad y sin ajustar reglas a estas parejas. Si se permite un perfil sin hora, ese perfil necesita definición y validación propias; no se autoriza seleccionarlo después de conocer qué variante genera una correspondencia.

La siguiente fase debe ampliar el cribado a un marco documental distinto, definido antes del cálculo, con diversidad relacional y de fuentes. Las parejas de este piloto permanecerán fuera de la evaluación reservada. Este avance no acredita eficacia empírica ni habilita un análisis confirmatorio.

## Registro bibliográfico

S01. Royal Household, «Early life and education», apartado inicial de nacimiento; publicación sin fecha identificada; lectura del pasaje HTML el 3-10-2026: https://www.royal.uk/the-queens-early-life-and-education.

S02. Royal Household, «50 facts about The Duke of Edinburgh», 25-01-2002, hechos 1 y 3; lectura HTML: https://www.royal.uk/50-facts-about-duke-edinburgh.

S03. Royal Household, «70 facts about The Queen and The Duke of Edinburgh’s Wedding», apartados A Royal Engagement y The Wedding Day, hechos 2 y 3; lectura HTML: https://www.royal.uk/70-facts-about-queen-and-duke-edinburghs-wedding.

S04. Royal Household, «The King», Biography/Early Life y Family and Married Life; lectura de los pasajes HTML: https://www.royal.uk/the-king.

S05. Royal Household, «Diana, Princess of Wales», Childhood and teenage years y Marriage and family; lectura de los pasajes HTML: https://www.royal.uk/diana-princess-wales.

S06. UK Parliament, Hansard, «Prince And Princess Of Wales», House of Commons, 9-12-1992, encabezado 15:30 y declaración inicial de John Major; lectura HTML: https://hansard.parliament.uk/Commons/1992-12-09/debates/ecfacae4-f52c-461c-b253-d7c04a299735/PrinceAndPrincessOfWales.

S07. Royal Household, «The Queen», About, nacimiento y matrimonio civil; lectura de la variante accesible: https://www.royal.uk/the-queen?os=v.

S08. Royal Household, «The Prince of Wales», Early Life; lectura del pasaje HTML: https://www.royal.uk/the-prince-of-wales-0.

S09. Royal Household, «The Princess of Wales», Early Life y Family Life; lectura de los pasajes HTML: https://www.royal.uk/the-princess-of-wales.

S10. Royal Household, «The wedding of Prince William and Miss Catherine Middleton», The wedding day y The engagement; lectura HTML: https://www.royal.uk/wedding-prince-william-and-miss-catherine-middleton.

S11. Foreign & Commonwealth Office, GOV.UK, «Royal Wedding details announced», publicado el 27-04-2011; lectura de fecha editorial y primer párrafo: https://www.gov.uk/government/news/royal-wedding-details-announced.

Las fuentes institucionales se clasifican P1 para sus afirmaciones documentales específicas. Esa prioridad no acredita el documento natal original, precisión cronométrica, independencia estadística o exhaustividad de observación. No se ha descargado ni publicado una copia integral de las páginas.
