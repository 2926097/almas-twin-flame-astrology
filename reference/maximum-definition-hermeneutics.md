# Extracción y definición interpretativa completa · revisión de ALMAS 1.26.0

Aplicar este protocolo a toda autoría astrológica: natal, relacional, temporal, occidental, dracónica, secundaria, Jyotiṣa y comparación doctrinal. La extensión y el formato cambian con la solicitud; la identidad de los datos, la escuela técnica y el alcance de cada afirmación permanecen. Máximo de definición significa máxima información pertinente y trazable. No significa multiplicar técnicas no solicitadas ni asignar una interpretación especializada sin fuente.

Para una ejecución nueva con preservación ampliada de movimiento y geometría, declarar `maximum_definition_context: true` en la entrada del pipeline. El adaptador de solicitudes relacionales transmite esta opción. Sin activación explícita, M04/M17 conservan la forma histórica de sus salidas. El atlas funciona en ambos modos y declara las lagunas del análisis importado sin completarlas.

## De la extracción a la lectura

Consumir `interpretive_atlas` del modelo documental personal o relacional. El atlas enumera objetos y campos disponibles mediante JSON Pointer; no copia valores, calcula cartas ni redacta conclusiones. Para un informe védico independiente, llamar `build_interpretive_atlas({'vedic': envelope})`. Para autoría en chat, utilizar la misma API o `scripts/build_interpretive_atlas.py canonical.json -o atlas.json`. No invocar efemérides para rellenar lagunas durante la escritura.

Cada entrada tiene `data_ref`, `field_refs`, `missing_dimensions` y `natal_substrate_refs`. Resolver estas últimas exclusivamente como contexto natal preexistente: un contacto dracónico no adquiere longitud o casa tropical porque su punto tenga una ficha natal enlazada. Una casa propia, una superposición en la carta del otro y una casa de Davison son escenarios distintos. Conservar siempre su propietario y su sistema.

`leaf_refs` permite recuperar todo el contenido de las rutas analíticas autorizadas, incluso campos que todavía no tienen una ficha especializada. `missing_routes` significa ausencia en ese canónico, no obligación de ejecutar todas las rutas. `missing_dimensions` significa dato ausente o nulo, no fallo ni aplicabilidad universal. Un arudha por signo puede estar completo sin longitud; una D9 no autoriza nakṣatras físicos sobre grados divisionales. Los recuentos del atlas son cobertura editorial, nunca rareza, raíces, independencia o probabilidades.

## Unidad mínima de definición

Desarrollar cada factor relevante en prosa conectando función, posición y contexto con una dinámica concreta. En un contacto, identificar los dos sujetos, los extremos reales, la técnica, la geometría, el orbe disponible y las capas. Explicar qué aporta el contacto al patrón y qué cambia respecto de otra geometría del mismo par. Incorporar manifestación constructiva, dificultad alternativa, tarea simbólica y límite inferencial. Evitar párrafos idénticos para Venus–Plutón en trígono y en cuadratura, para ASC y DSC o para Nodo Norte y Nodo Sur.

El grado exacto documenta posición o precisión. Con `maximum_definition_context: true`, M04 añade en `position_profiles` el sector geométrico de diez grados, separado de su regencia: no asigna por sí mismo símbolo, planeta regente, dignidad ni significado. La interpretación posicional sigue [Hermenéutica posicional de factores](positional-factor-hermeneutics.md), que registra por separado las variantes helenísticas de domicilios/faces y los testimonios atribuidos sobre retrogradación. El orbe describe proximidad al ángulo bajo la política declarada; no mide importancia espiritual. Aplicación y separación sólo se narran cuando están calculadas explícitamente para esa técnica. No deducirlas de velocidades incompletas ni confundir un estado temporal con aplicación geométrica.

## Definición por ámbito

En el ámbito natal, enlazar función del factor, signo, elemento y modalidad documentados, casa propia y su sistema, decanato y variante declarada, regencia explícita, dispositor(es), condición disponible y aspectos. Los perfiles detallados sólo se emiten al activar `maximum_definition_context`; la forma histórica permanece sin cambios si la opción está desactivada. Preservar latitud, declinación, velocidad y retrogradación cuando existan. Distinguir el estado calculado de su interpretación: retrogradación, estación, fuera de límites, combustión o dignidad sólo reciben significado con criterio técnico, fuente y alcance doctrinal declarados. Velocidad cero no acredita estación confirmada.

En sinastría, describir los dos sustratos natales antes de su interacción. Distinguir dirección del circuito, punto activador y escenario receptor. Las casas proporcionan el campo de experiencia; no crean reciprocidad ni segunda evidencia. Los contactos generacionales requieren revisar especificidad frente a contactos personales y angulares. Explicar recursos y fricciones de la misma arquitectura sin equiparar dificultad a karma o facilidad a origen común.

En compuesta y Davison, desarrollar posiciones, aspectos y casas efectivamente calculadas. Comparar organización interna y construcción espacio-temporal sin contar ambas como confirmaciones independientes. Si la compuesta no tiene casas en el backend vigente, declararlo y no trasladar las del Davison. En dracónica, mantener el polo nodal de referencia, el sentido natal→dracónica y dracónica→natal, y el carácter corroborativo de dracónica↔dracónica.

En declinaciones y antiscios, explicar la geometría propia. No convertir paralelos en conjunciones literales ni antiscios en contactos por longitud sin identificar la transformación. Los polos normalizados para scoring deben recuperarse en el texto; los alias no crean sujetos, asteroides o posiciones nuevas.

En lotes, asteroides, estrellas y significadores secundarios, conservar identidad, fórmula o variante, secta, época y procedencia cuando estén presentes. Exponer qué matiz añaden al patrón principal. El mito de un nombre no constituye regla astrológica tradicional. Un significado especializado pendiente permanece pendiente, aun si el contacto es exacto. Una estrella requiere identificación y método; no derivar su posición desde una lista antigua sin época declarada.

En temporalidad, enlazar señal, técnica, subtipo, raíz previa, grupo de dependencia, ventana, perfeccionamiento y hecho documental disponible. Interpretar activación, no crear estructura desde el tránsito. Diferenciar retornos calculados, proximidad a un retorno y carta anual arbitraria. Mantener las alternativas de una misma ventana y declarar sensibilidad horaria cuando exista. No prometer decisiones, contactos, consentimiento o reunión.

En Jyotiṣa, desarrollar D1, D9, nakṣatra, pāda, dispositor, AK/DK, karakāṃśa, arudhas, bindu, upagrahas y períodos sólo si fueron producidos. Mantener ayanāṃśa, variante nodal, sistema de kārakas y año daśā. No trasladar automáticamente casas, aspectos, dignidades ni significados occidentales al bloque VED. Las coincidencias de signo, nakṣatra y dispositor tienen dependencias compartidas; los cruces D1/D9 relacionales siguen siendo hipótesis ALMAS cuando así los declara el motor. No reconstruir Aṣṭakūṭa completo a partir de Tara observacional.

## Comparación metafísica

Abrir la comparación doctrinal después de explicar el patrón astrológico. Identificar autor, obra, tradición, fecha y pasaje realmente consultado; distinguir método astrológico, doctrina del alma, interpretación contemporánea e hipótesis ALMAS. Una doctrina general de unidad no discrimina una pareja monádica; una narrativa de reencarnación no documenta vidas anteriores de los sujetos. Una descripción de sincronía no demuestra causalidad astrológica ni destino.

Comparar también diferencias y contra-doctrinas. No fusionar Cábala judaica, Cábala hermética, enseñanzas contemporáneas de Berg, Vedānta y psicología arquetípica. Mantener sus genealogías. En el corpus adjunto, distinguir U. G. Krishnamurti del J. Krishnamurti de `El arte de escuchar`; el nombre del archivo no basta para identificar al autor. Las traducciones de una misma obra no son fuentes doctrinales independientes.

## Cobertura, selección y formatos

En un informe completo, resolver cada entrada del atlas —incluidos `position_profile`— mediante `INTERPRETED`, `EXCLUDED` o `NOT_EVALUABLE`, con motivo. Las dimensiones no aplicables (por ejemplo, retrogradación de un ángulo) se explican como tales dentro de la ficha; los datos faltantes, sistemas no declarados y faltas de fuente se distinguen. Las duplicaciones de representación se excluyen como tales. En una lectura focal o ejecutiva, justificar la selección por la pregunta y conservar el resto para consulta; no forzar todos los factores al cuerpo narrativo. No convertir el atlas en un inventario sin síntesis.

`audit_interpretive_coverage` verifica referencias, omisiones y campos interpretativos declarados. Para `INTERPRETED`, exigir `reason`, `function`, `dynamic`, `alternative`, `limits` y `epistemic_class`; para C/D exigir `source_refs`. La API comprueba presencia de referencias declaradas, no autenticidad de citas ni calidad semántica: contrastar pasajes con el registro y el original antes de publicar. `COMPLETE` es cierre editorial de disposiciones, no validación empírica ni promoción ontológica. Un atlas manipulado o derivado de un canónico anterior se rechaza.

Usar una ficha técnica extensa en atlas/anexo; redactar en párrafos integrados para lectura personal, relacional o metafísica; seleccionar los patrones dominantes en síntesis ejecutiva; conservar referencias y alternativas en DOCX/PDF. Una versión breve puede abreviar el texto, pero no eliminar incertidumbre relevante ni cambiar la clasificación. El mismo canónico sostiene todos los formatos.

## Límites de esta revisión

La revisión preserva información antes descartada, añade extracción referencial y una auditoría editorial. Los perfiles posicionales derivan signo, sector geométrico y cadenas sólo desde longitudes y políticas declaradas; no incorporan efemérides nuevas, significados exhaustivos para cada combinación, entrenamiento de generación ni validación empírica. Los perfiles no reciben una nueva etiqueta ontológica por disponer de más campos. La profundidad final exige autoría y comprobación de fuentes, conforme al protocolo de síntesis existente.
