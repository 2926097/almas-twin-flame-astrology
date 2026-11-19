# Investigación aplicada al observatorio diario

## Qué optimizamos

La unidad de adquisición es el cielo geocéntrico a una hora UTC; la unidad de interpretación es un vínculo, una versión natal y una fecha civil. El mismo lote público de posiciones puede alimentar varios informes. Las cúspides, los datos de nacimiento, las cartas derivadas y los hechos relatados requieren procedencia específica del vínculo. Esta división reduce descargas y evita contaminar dos historias personales. La optimalidad aquí significa cumplir los requisitos documentados de ALMAS con trazabilidad y menor repetición. No se ha medido la superioridad predictiva de un sistema astrológico.

## Elección de fuentes y motores

El generador de ALMAS ya escribe dos instantes por producto, flags de retorno, marco, velocidades y huellas de archivos orbitales. El consumidor vuelve a comprobar los 19 cuerpos obligatorios. Para el contrato actual el valor 258 corresponde a Swiss más velocidad y coordenadas geocéntricas eclípticas en grados; la igualdad estricta rechaza banderas adicionales que cambiarían el marco. Verificar solo que se pidió Swiss permitiría aceptar una respuesta obtenida con otro motor. El producto local válido agiliza la segunda lectura y los días solapados sirven de contraste entre publicaciones. Una huella del producto fija qué bytes se leyeron; las huellas que declara el productor describen sus insumos. Reproducir el cálculo exige verificar además esos insumos por separado.

Fuentes: [Astrodienst](https://github.com/aloistr/swisseph), [manual de programación](https://www.astro.com/swisseph/swephprg.pdf), [generador ALMAS](https://github.com/2926097/almas-twin-flame-astrology/blob/main/tools/daily_asteroid_ephemeris.py).

Horizons permite solicitar la magnitud 31 al geocentro. Para contrastar un asteroide hay que fijar el identificador numérico, el centro, el instante, el marco eclíptico de fecha y la convención aparente. La derivada estimada mediante diferencias centradas tiene origen y precisión distintos de una velocidad Swiss. Una discrepancia exige examinar convenciones y respuesta original antes de seleccionar un aspecto de pocos minutos. La ruta JPL documenta el contraste o permite investigación exploratoria cuando la tarea lo admita; exigir Swiss para el informe diario conserva el criterio de aceptación original.

Fuente: [JPL Horizons, magnitud 31](https://ssd.jpl.nasa.gov/horizons/manual.html).

## Cómo detectar qué cambia

La distancia circular evita clasificar 359,9° y 0,1° como puntos lejanos. El orbe se mide respecto del ángulo nominal. En un tránsito a una natal el receptor permanece fijo; al comparar dos tránsitos se mueven ambos extremos. La diferencia entre el orbe de ayer y el de hoy permite seleccionar cambios. Una pasada exacta puede haber ocurrido entre las muestras y un cuerpo puede estacionar y regresar. La búsqueda de raíces necesita una función orientada y continua en el tramo; una tangencia necesita además búsqueda de mínimos. Skyfield distingue búsquedas de eventos y extremos y explica el compromiso entre coste y resolución. Lo adoptamos como criterio de refinamiento, sin mezclar sus posiciones con el producto obligatorio Swiss. El explorador entrega candidatos a partir de muestras diarias; el cálculo intradiario debe registrarse separadamente.

Fuente: [Skyfield, búsqueda temporal](https://rhodesmill.org/skyfield/searches.html).

## De la geometría a una lectura

Kerykeion distingue el cálculo por puntos medios de la compuesta y el levantamiento de una Davison en el punto medio temporal y espacial. Es una referencia adecuada para la separación de cartas y para relacionar gráficos con datos estructurados. Importar su selección predeterminada de cuerpos, cúspides u orbes cambiaría el experimento. ALMAS conserva la versión utilizada por cada tarea. La lectura puede entonces explicar por qué un mismo tránsito pesa de manera distinta en una carta natal, una compuesta y una Davison. Una configuración compartida requiere receptores conectados por geometría calculada. Una coincidencia temática entre varios asteroides no aumenta por sí sola la evidencia.

Fuente: [Kerykeion, cartas relacionales y aspectos](https://github.com/g-battaglia/kerykeion).

La lectura empieza por la figura dominante del cielo y su evolución; después incorpora el contexto de cada persona, las casas documentadas y los regentes. Para una tesis simbólica se expresa qué cuenta a su favor, qué configuración la matiza y qué explicaciones siguen abiertas. Un acontecimiento relatado se conserva con fecha y fuente. El gráfico debe permitir comprobar la argumentación viendo qué dos puntos forman cada aspecto, a qué carta pertenecen y cuánto se apartan de la exactitud. Ningún motor de efemérides proporciona evidencia sobre la intención de otra persona.

## Alcance de las pruebas

Separar tres afirmaciones: leer y validar el producto público; reproducir un cálculo desde los archivos orbitales; entregar automáticamente una lectura privada completa. Cada una necesita una prueba diferente. Una prueba sintética sirve para pasos por cero, cambios de marco o respuestas incompletas. Una ejecución con datos del repositorio comprueba compatibilidad real. Ninguna de ellas acredita por sí sola una ejecución programada ni una predicción metafísica.
