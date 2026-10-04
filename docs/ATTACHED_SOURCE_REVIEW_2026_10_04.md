# Revisión de fuentes adjuntas · 4 octubre 2026

El catálogo `reference/attached-source-catalogue.json` identifica 19 archivos PDF, 18 familias de obra y un pasaje seleccionado por archivo. Conserva hash del PDF, número físico de página, hash de la extracción del pasaje, identidad bibliográfica, paráfrasis y límite inferencial. Los localizadores físicos se obtuvieron por página PDF, sin asumir que los saltos de página de una extracción concatenada reproduzcan el PDF original.

Se extrajeron los textos nativos y se ejecutó OCR sobre las 858 páginas de los cuatro archivos escaneados (03, 12, 16 y 18). Los pasajes seleccionados de esos cuatro archivos se cotejaron visualmente con las páginas originales. OCR disponible en inglés: no garantiza exactitud de toda la transcripción española. No se declara una revisión doctrinal íntegra de los libros. No se distribuyen PDF ni textos completos; los hashes de extracción documentan esta lectura local, sin pretender estabilidad entre distintos motores de OCR.

## Identidades y dependencia

U.G. Krishnamurti es Uppaluri Gopala; no es Jiddu Krishnamurti. El Reader incluye la introducción de Mukunda Rao y debe distinguirse de las palabras atribuidas a U.G. `Edgar Cayce on Reincarnation` está escrito por Noel Langley bajo la edición de Hugh Lynn Cayce. `Libro de la Sabiduría II` identifica a Harry B. Joseph. `Jung’s Studies in Astrology` es un estudio de Liz Greene, no una obra escrita por Jung. La obra de Sepharial identifica a Walter Gorn Old y un método de nombres y números. Aranegui, Berg, Dobin y Halevi representan exposiciones modernas identificadas, sin sustituir al conjunto de la Cábala ni al judaísmo.

`The Book` y `El libro del tabú` pertenecen a la misma familia de obra. Una traducción no añade una corroboración independiente. Tampoco la coexistencia de motivos comparables en distintas obras demuestra un mecanismo común o una identidad ontológica.

## Uso autorizado por la evidencia

El pasaje permite atribuir al autor una exposición, propuesta o interpretación concreta. No proporciona evidencia A de hechos de una pareja, ni transforma una correspondencia B en una doctrina C universal. Las comparaciones D y las operacionalizaciones E de ALMAS requieren etiquetado propio. Un relato sobre vidas anteriores no verifica la identidad de una encarnación; las exposiciones de cuerpos sutiles no prueban su existencia; la terminología científica usada por un autor no acredita validación científica. El efecto sobre scoring es cero, la discriminación ontológica permanece `INSUFFICIENT` y la validación empírica externa `NOT_PERFORMED`.

El catálogo es una capa de auditoría. No incorpora automáticamente estos archivos al router ni promueve su estado en el registro canónico. Una incorporación posterior exige pasajes adecuados al claim, genealogía, dependencia y revisión de contra-doctrina. Las seis entradas sin `pages`, `passage` o `verification_anchor` se registran como `LOCATOR_MISSING`; no se inventan páginas ni se modifican silenciosamente sus estados heredados.

## Control reproducible

`python scripts/validate_source_catalogue.py` comprueba identidades críticas, dependencia de Watts, límites de páginas, ausencia de efectos numéricos y paridad del listado de gaps con el registro actual. Es un control de integridad del catálogo, no una segunda lectura de los libros ni un ensayo de eficacia empírica.
