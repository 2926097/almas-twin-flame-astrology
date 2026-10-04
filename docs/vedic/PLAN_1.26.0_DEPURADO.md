# ALMAS 1.26.0 — Plan depurado del motor Jyotiṣa Relacional

Revisión R1, 4 de octubre de 2026. Sustituye las decisiones técnicas ambiguas del plan inicial. Su ejecución incorpora un subsistema védico observacional al paquete existente `almas_tfa`, sin alterar el backend occidental de producción, los índices canónicos, los pilares ni los discriminadores. El cierre técnico y la validación empírica son estados independientes.

## Alcance y naturaleza del resultado

La versión ejecutable comprende posiciones siderales reproducibles, los 27 nakṣatras y 108 pādas, sistemas de siete y ocho Chara Kārakas, Navāṃśa D9, Kārakāṃśa por signo, los doce Arudhas con AL/UL/A7, Bhrigu Bindu con arco declarado, once upagrahas, matriz relacional D1↔D1/D9↔D9/D1↔D9, Vimśottarī a tres niveles, temporalidad anclada a estructura, sensibilidad, controles descriptivos, ablación y atribución Shapley de cobertura. Vivāha Sahama se ofrece como cálculo condicionado a una carta anual cuyo retorno haya sido verificado por el motor de retornos o una fuente externa identificada.

El paquete usa `src/almas_tfa/vedic/`, respetando la arquitectura real del repositorio. No se crea una segunda raíz `almas/vedic/` ni se duplica el núcleo de scoring. Se añade la CLI `almas-vedic`, con entrada JSON y salidas JSON o informe textual en español. La envolvente canónica `vedic` es opcional; la función de incorporación preserva todos los campos previos y bloquea sobrescrituras.

La prioridad temporal del plan inicial se corrige: Vimśottarī y el tratamiento de eventos forman parte del cierre funcional mínimo. Las extensiones cuya documentación no permita una ejecución verificable deben devolver un estado explícito o permanecer fuera del alcance ejecutable; no se admiten archivos vacíos ni funciones simuladas como implementación.

## Separación epistemológica

Los resultados astronómicos y sus transformaciones deterministas pertenecen a A, dato calculado; el perfil y la operación pertenecen a B, técnica. C se reserva a afirmaciones efectivamente atribuidas a una fuente. D requiere identificar el uso contemporáneo y E recoge los cruces relacionales y las hipótesis de ALMAS. Que una fuente describa un significador individual o matrimonial no documenta por sí mismo la interpretación de su contacto entre dos personas.

La procedencia del método se separa de la evidencia de su aplicación relacional. Un cálculo exacto no recibe automáticamente confianza doctrinal alta ni validación empírica. Cada carta, comparación y evento conserva sus metadatos y estados. La clasificación ontológica permanece `INSUFFICIENT`; no se asignan probabilidades metafísicas ni se convierte una rareza geométrica en probabilidad de origen compartido.

## Convenciones astronómicas y control de entradas

El perfil por defecto es Lahiri, con alternativas Raman, KP y Fagan–Bradley comparativo. CUSTOM requiere época de referencia en día juliano y ayanāṃśa inicial. No se impone equivalencia entre todas las variantes denominadas Chitrapaksha. Rahu utiliza nodo medio por defecto, con nodo verdadero seleccionable; Ketu se calcula como antípoda y ambos extremos comparten una dependencia nodal.

La entrada bruta exige instante ISO 8601 con offset explícito y coordenadas finitas. Si se proporciona zona IANA, la hora civil y el offset deben coincidir con esa zona en ese instante; una discrepancia DST se rechaza. No se resuelven lugares por inferencia textual ni se inventa zona horaria. La incertidumbre horaria se declara y se conserva. La selección de datos natales debe seguir las últimas correcciones documentadas; esta implementación pública utiliza exclusivamente fixtures sintéticos y ejemplos documentales.

El motor védico puede utilizar Swiss Ephemeris/Moshier mediante dependencia opcional versionada, registrando versión, flags efectivos, día juliano y valor del ayanāṃśa. Este backend se identifica como comparativo de la capa VED y no reemplaza MOIRA/JPL del núcleo occidental. La ausencia del extra astronómico no impide utilizar las transformaciones sobre posiciones siderales precomputadas, pero esas entradas quedan expresamente sin verificación astronómica independiente.

## Tipos geométricos y límites

Una longitud física D1, una coordenada divisional D9 y un signo sin grados son objetos distintos. AL, UL y A7 son resultados por signo. Kārakāṃśa identifica el signo D9 ocupado por AK; no se le asignan grados de una supuesta posición eclíptica física. AK y DK son roles que apuntan a planetas existentes y heredan su posición, sin convertirse en nuevas raíces independientes.

La D9 parāśarī se obtiene por partición de 3°20′ y asignación de signo. La coordenada armónica `9 × longitud mod 360` se conserva únicamente como representación divisional; no se aplican automáticamente nakṣatras físicos ni orbes occidentales a sus grados. Los cruces entre cartas D1↔D9 se evalúan por signo y se etiquetan como hipótesis relacionales ALMAS.

Los intervalos de signo, nakṣatra y pāda son semiabiertos. Se normalizan las longitudes y se rechazan NaN, infinito y valores booleanos. Los empates en Chara Kārakas se bloquean con `NOT_EVALUABLE`, en lugar de resolverlos por un orden arbitrario. El sistema de ocho incluye Rahu con avance inverso y PiK; el sistema de siete excluye Rahu y PiK. Ketu queda fuera de ambos rankings.

## Arudhas y variantes doctrinales

La excepción se aplica al resultado bruto que cae en la primera o séptima posición desde el signo fuente; se toma la décima desde ese resultado bruto. No se limita la excepción al regente situado en la misma casa o en la séptima, porque esa formulación omite otros casos. Los tests incluyen los doce resultados del ejemplo 29 de Rao.

El perfil implementado usa los siete regentes planetarios, sin corregencias de Rahu/Ketu. Esta elección se declara como variante y no se presenta como reproducción íntegra de la regla de fuerza entre corregentes expuesta por Rao. Un perfil de corregencias aún no implementado se rechaza. UL incorpora la segunda posición desde su signo y el regente correspondiente; A7 permanece separado de UL. Las interpretaciones de unión formal y proyección relacional son hipótesis de trabajo, no equivalencias universales.

## Bindu, upagrahas y overlays

Bhrigu Bindu conserva Luna, Rahu, arco, resultado y antípoda. El perfil por defecto mide el arco zodiacal directo Rahu→Luna; el arco menor es una alternativa explícita, bloqueada cuando los extremos son antípodas. No se atribuye a ese midpoint una procedencia clásica no verificada ni se interpreta como demostración de destino compartido.

Los cinco upagrahas solares siguen fórmulas identificadas y se verifican con el ejemplo 6 de Rao. Los seis temporales requieren salida y puesta solares; el perfil Rao emplea Gulika en el centro de la fracción de Saturno y Māndi al inicio. Se admite el intercambio de convenciones como variante declarada, sin afirmar que constituye el mismo método. El día planetario empieza al amanecer; una hora civil posterior a medianoche y anterior al amanecer pertenece al día planetario anterior. Se registra la definición del evento solar: centro del disco, sin refracción y nivel del mar. Cuando no existe salida/puesta evaluable, el cálculo temporal se bloquea.

Abhijit es un overlay opcional en su intervalo tradicional, no un reparto del zodiaco en 28 sectores iguales. No altera el catálogo estándar de 27 ni Vimśottarī. Su peso canónico es cero. Prāṇapada, Yogatārās, metadatos deity/shakti/tattva sin ficha verificada y nuevas variantes se aplazan hasta contar con fórmula, catálogo y pasaje identificados. Este aplazamiento es una decisión de alcance R1, no una función implementada.

## Compatibilidad y temporalidad

La compatibilidad lunar conserva relaciones por signo y categorías Tara en ambas direcciones. Los ocho componentes de Aṣṭakūṭa existen como campos independientes. No se publica una suma de 36 puntos mientras no se hayan verificado las tablas, excepciones y orientación del perfil seleccionado. Ningún dato ausente se sustituye por cero; ningún rol conyugal se infiere desde el sexo o el nombre del sujeto.

Vimśottarī permite año de 360, 365.2425 o 365.25636 días, con 365.2425 como convención inicial explícita. Los mahā/antara/pratyantara derivan del período completo, incluido el tramo transcurrido antes del nacimiento; no se reinician las subdivisiones sobre el saldo natal. Los intervalos temporales son UTC semiabiertos. Se valida el saldo del ejemplo 50 de Rao utilizando su convención savana.

Los eventos conservan la estructura de las dos cartas por hash. Las activaciones daśā identifican los roles planetarios activos y los regentes de UL/A7. Los tránsitos, cuando se dispone de una carta del instante, sólo se relacionan con contactos estructurales previos. Alias y referencias a una misma perfección se agrupan en un contacto compartido. La temporalidad no crea raíces independientes ni predice decisiones, consentimiento, reciprocidad o un encuentro factual.

## Varṣaphala y Sahama

Vivāha Sahama exige contexto anual y día/noche verificables. El perfil Rao aplica Venus−Saturno+Ascendente de día, inversión nocturna y la corrección de 30° cuando el Ascendente no está en el interior del arco dirigido entre los términos. La política de extremos se declara. El pipeline exige referencia al recibo del retorno; su presencia es un requisito de trazabilidad, no una autenticación automática del documento externo.

No se implementa un solver anual independiente ni se vuelve a calcular la revolución al redactar el informe. Muntha, regente del año, aspectos Tājika completos y Sahamas adicionales permanecen fuera de este cierre. Se corrige la afirmación absoluta del plan inicial: que ALMAS limite esta función a la carta anual no implica que la tradición desconozca usos natales de Sahamas.

## Dependencia, IVED y contraevidencia

Cada comparación utiliza ID estable, familia, posiciones origen, grupo de redundancia y bundle de dependencias. Las referencias a un mismo planeta desde AK/DK, D1/D9 o dispositivos derivados se conservan como relacionadas. La cantidad de bundles no se denomina cantidad de raíces independientes y los extremos Rahu/Ketu no duplican automáticamente evidencia.

IVED se conserva como objeto sombra `UNVALIDATED`, con valor y pesos nulos. No se utiliza una media de pesos supuestamente neutros: elegir variables, escalas y denominadores ya supone un modelo. El Shapley implementado distribuye cobertura de bundles entre familias; no se interpreta como contribución causal ni como importancia metafísica. Las ablaciones retiran familias descriptivas y verifican que el delta canónico es cero. Ninguna función permite promocionar estas variables a scoring mediante una simple bandera.

Las relaciones 6/8 y 2/12 se registran para revisión, sin convertirlas automáticamente en contraevidencia factual. Una ausencia sólo puede actuar como contraevidencia de una hipótesis cuando exista previamente una regla que defina qué contacto se esperaba y por qué. Nadi, incompatibilidad matrimonial y falta de sincronización temporal no contradicen por sí mismos una categoría ontológica sin un discriminador validado.

## Secuencia de ejecución y criterios de cierre

La fase 1 fija entradas, configuración sideral y procedencia. La fase 2 implementa límites de nakṣatra/pāda. La fase 3 implementa los dos rankings kāraka y sus empates. La fase 4 incorpora D9 y Kārakāṃśa con tipos geométricos separados. La fase 5 calcula los doce Arudhas y las excepciones. La fase 6 calcula Bindu y sus dos arcos. La fase 7 implementa once upagrahas y Abhijit, manteniendo bloqueadas variantes sin respaldo. La fase 8 implementa la geometría lunar descriptiva y conserva explícitos los componentes Aṣṭakūṭa no evaluables. La fase 9 incorpora Vimśottarī y eventos. La fase 10 ofrece Sahama anual condicionado a un recibo. La fase 11 construye la matriz de sinastría. La fase 12 integra la envolvente optativa, informe y auditoría descriptiva. La fase 13 ejecuta pruebas, sensibilidad, controles, ablación y regresión del núcleo.

El cierre funcional requiere CLI operativa, JSON serializable sin NaN, schema, pruebas documentales y de límites, informe español, ausencia de cambios en los campos canónicos previos y estado por técnica. El cierre científico requiere una cohorte independiente, variables objetivo observables, unidad estadística definida, controles adecuados, preregistro y evaluación de incremento fuera de muestra. Ejecutar controles sintéticos o disponer de un algoritmo Benjamini–Hochberg no satisface esos requisitos.

La sensibilidad informa cambios en familias al muestrear ayanāṃśas y desplazamientos ±1/5/15/30 minutos; estabilidad en esos puntos no prueba estabilidad continua. Los controles del corpus se forman entre sujetos de un estrato declarado, excluyendo pares observados y autorrelaciones. El uso repetido de sujetos se consigna y no permite tratarlos como observaciones independientes. La etiqueta externa permanece `NOT_PERFORMED` incluso si el usuario denomina externo al corpus, hasta completar el contrato de evaluación.

## Entregables y procedencia

Los entregables son el paquete `src/almas_tfa/vedic/`, las fichas de `docs/vedic/`, `tests/test_vedic.py`, fixtures documentales, `schemas/vedic.schema.json`, configuración empaquetada, entrada sintética, CLI, workflow y auditoría de release. La documentación debe indicar el alcance implementado, el condicionado y el aplazado. La declaración de cierre no puede ocultar que Aṣṭakūṭa completo, Prāṇapada, Yogatārās o calibración escalar siguen sin implementación validada.

La fuente técnica principal es P. V. R. Narasimha Rao, *Vedic Astrology: An Integrated Approach* (2000), edición distribuida por su autor: capítulos 4, 6, 8, 9, 16 y 28; ejemplos 6, 16, 28, 29 y 50. Se clasifica P4, autor identificado con método, y no como edición crítica primaria del corpus sánscrito. La interfaz astronómica se documenta mediante Astrodienst, *Swiss Ephemeris Programmer’s Documentation*, versión 2.10, secciones de zodiaco sideral, cálculo UT y salida/puesta. Los ejemplos de PyJHora se emplean como contraste documental de implementación, sin incorporar su código al repositorio ni presentarlo como segundo backend astronómico independiente.

Referencias: https://vedicastrologer.org/articles/vedic_astro_textbook.pdf ; https://www.astro.com/ftp/swisseph/doc/swephprg.2.10.htm ; https://github.com/naturalstupid/PyJHora . No se incorporan los PDF de terceros al repositorio público.
