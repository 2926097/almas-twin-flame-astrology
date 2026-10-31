# ALMAS · Paquete operativo de captación externa y preregistro (borrador, 30-10-2026)

**Referencia:** issues [#120](https://github.com/2926097/almas-twin-flame-astrology/issues/120) (validación externa) y [#123](https://github.com/2926097/almas-twin-flame-astrology/issues/123) (captación/custodia). **Estado:** `DRAFT_RESEARCH_OPERATIONS / NO-GO`. Este documento es un instrumento de preparación, **no** una aprobación ética, un dictamen jurídico, un preregistro ni un estudio ejecutado. No se han captado participantes, obtenido consentimientos, codificado observaciones ni abierto holdouts.

## Elección de la pregunta antes de obtener datos

La investigación debe identificar por escrito **un estudio y un endpoint primario**, sin confundir:

- **RRA temporal:** asociación descriptiva o inferencial, conforme a un diseño precongelado, entre fechas de acontecimientos documentados y el indicador exacto no tautológico del motor RRA frente a fechas control con cobertura equiparable. Referencia: `docs/RRA_EXTERNAL_VALIDATION_PROTOCOL.md`, `docs/RRA_EXTERNAL_RUNNER.md`; el borrador propone alfa 0,05 y 9.999 permutaciones, **no** están aprobados ni prueban intercambiabilidad.
- **Identidad diádica declarada:** clasificación de parejas declaradas `DECLARED_MATCHED_DYAD` frente a pares cruzados `CROSS_DYAD_OPPOSITE_POLARITY` en una población objetivo previamente delimitada. Referencia: `docs/PAIR_IDENTITY_BLIND_VALIDATION_PROTOCOL.md`; los objetivos 40/120/120 son planificación, no muestra obtenida. Una etiqueta declarada nunca es verdad ontológica.

Una misma cohorte no se debe convertir en dos éxitos confirmatorios cambiando retrospectivamente endpoints, subgrupos o fechas. La investigación no puede demostrar ontología espiritual; un posible resultado solo se interpreta respecto del observable preregistrado. No utilizar parejas de desarrollo o casos examinados al diseñar reglas como confirmación de las mismas.

## Responsabilidades y segregación operativa

| Función necesaria | Actuación y prueba esperada |
|---|---|
| Dirección científica real | Definir población, endpoint, estimando, plan muestral, stop rule, desviaciones; firmar protocolo y declarar conflictos |
| Responsable del tratamiento/custodia | Determinar base jurídica del tratamiento y transparencia; seguridad, acceso, conservación, supresión, transferencias; custodiar identificadores y correspondencias **fuera de GitHub** |
| Selección documental | Aplicar criterios de inclusión/exclusión sin conocer aspectos astrológicos ni salidas del motor; conservar denominador de cribados |
| Codificador documental A y B | Dos personas realmente distintas, sin resultados astrológicos y con codificaciones independientes fechadas de fechas, cobertura, fuentes e incertidumbre |
| Curación/adjudicación | Revisar discrepancias **después** de conservar ambos juegos originales; aplicar criterio congelado y publicar acuerdo sin inferir concordancia perfecta |
| Operador estructural | Ejecutar cartas/retornos con inputs permitidos, sin narrativa ni etiqueta declarada; congelar hashes de salidas antes de revelar documentación |
| Auditor independiente | Comprobar no contaminación entre cohortes, tiempos de preregistro, controles, logs, hashes, privacidades y desviaciones, sin autorizar promoción ontológica |

Estas responsabilidades deben materializarse en personas/equipos y registros reales. **No** se atribuyen ficticiamente a herramientas, respuestas de IA ni actores inventados; una segunda ejecución de ChatGPT no constituye doble codificación independiente.

## Puerta de captación y privacidad

Vía prospectiva: participantes mayores de edad, información comprensible sobre finalidad, procedimiento, diarios, eventuales efectos de expectativas, uso de datos natales e históricos y derechos; captación sin condicionar resultados ni reclutar por sinastría. Registrar tanto invitaciones como rechazos y abandonos solo mediante agregados públicos no identificativos. Los documentos de nacimiento, identidades, consentimientos y diarios se conservan exclusivamente en un sistema de investigación autorizado, separado del repositorio y del pipeline estructural ciego.

Vía retrospectiva: `Astro-Databank` puede servir para construir un marco de nombres, **no** como certificado de hora, independencia estadística o cobertura de negativos. Transcribir las fuentes primarias de hora (y divergencias) y de acontecimientos; no convertir ausencia de noticias en «no evento». El cribado ya documentado en `docs/RRA_REPLACEMENT_COHORT_SEARCH_2026_10_03.md` es piloto y no se incorpora al holdout.

En España, el responsable de tratamiento debe determinar antes de captar datos qué base jurídica concreta es aplicable conforme a los arts. 5, 6 y, cuando corresponda, 9 del RGPD y a la normativa nacional; el consentimiento informado de investigación y la base legal RGPD **no son automáticamente equivalentes**. Si se usa consentimiento como base, debe ser libre, específico, informado, inequívoco, demostrable y revocable; valorar expresamente categorías especiales, transferencias internacionales, minimización y control de accesos. El presente texto **no** sustituye la revisión jurídica y, cuando proceda, ética institucional. No publicar consentimientos ni formularios cumplimentados en GitHub.

Fuente oficial de orientación de consentimiento: [AEPD](https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0211-segun-el-rgpd-como-debe-solicitarse-el-consentimiento-de-los-interesados-para-tratar-sus-datos-personales).

## Corpus, cobertura temporal y observaciones negativas

Para cada vínculo elegible, el custodio debe conservar fuera del repositorio una ficha de procedencia con origen de ambos nacimientos, calidad horaria y desacuerdos sin rectificación orientada al resultado; prueba documental del vínculo, tiempo de observación, fuentes disponibles, periodos ausentes, incidencias y exposición previa del caso en el desarrollo. Cada evento requiere `fact_key`, tipo definido, fecha o intervalo del **hecho** (distinta de la fecha de publicación), incertidumbre, fuente/pasaje y codificación A/B.

La observación temporal debe permitir distinguir formalmente `EVENT_OBSERVED`, `NO_EVENT_VERIFIED_WITH_COVERAGE`, `NOT_OBSERVED` y `AMBIGUOUS`. Solo el segundo estado puede alimentar un control negativo admisible, y únicamente cuando el mecanismo de seguimiento hace defendible la ausencia del **evento definido**, no de cualquier experiencia íntima. `NOT_OBSERVED` y `AMBIGUOUS` permanecen `NOT_EVALUABLE` para el indicador correspondiente; **nunca** se codifican como 0. Un diario incompleto no implica un día negativo.

Congelar antes del análisis los periodos de observación, ventanas, reglas de muestreo de días control, calendario, estaciones, aniversarios, edad, lagunas, solapamientos y precisión de fecha. Las fechas de control deben elegirse sin consultar coincidencias astrológicas. Igualar solo número de fechas sin igualar cobertura temporal o de fuentes puede introducir sesgo.

## Partición independiente, cegamiento y freeze

Cada sujeto y cronología compartida pertenece a un solo componente conexo. Asignar **componentes completos**, no filas ni vínculos individuales, a `DEVELOPMENT_ONLY`, piloto, holdout y replicación; deduplicar personas, hechos y fuentes. La pertenencia se congela antes de abrir resultados. Un caso cuyo desarrollo o exposición previa se descubra después pasa a `RETIRED` o `DEVELOPMENT_ONLY`; no se sustituye oportunistamente.

La secuencia formal es:

1. Congelar definición del resultado observable, población, inclusión, exclusiones, grafo de dependencia, tamaño/parada, faltantes, controles y plan estadístico.
2. Designar custodio, responsables, dos codificadores independientes, operador ciego y revisor; documentar habilitación legal, origen de datos y separación de acceso.
3. Preparar un paquete de preregistro **sin datos personales** con SHA del código, recursos RRA, backend/efemérides, hashes del plan, tablas de decisión, nulls, AB0–AB8, perturbación horaria, multiplicidad, niveles alfa, criterio de rechazo y plan de negativos. Incluir la justificación del tamaño muestral por potencia o precisión, con hipótesis y pérdidas previstas, y el plan de atribuciones Shapley agrupadas por raíces o familias dependientes, con criterios de estabilidad fijados antes del análisis y sin postselección.
4. Depositar un registro prospectivo con identificador comprobable y sello temporal **antes** de acceder al resultado del holdout. Conservar recibo de inscripción, estado aprobado/embargado y copia fechada. Un documento local y una PR no son un preregistro externo. La plataforma [OSF Registries](https://help.osf.io/article/770-registrations) mantiene registros; los servicios `OSF Projects` están en transición y no deben asumirse disponibles para crear nuevos proyectos.
5. Ejecutar el componente estructural en ciego, congelar hashes y recibos. Después, y solo conforme a reglas previas, abrir documentación del resultado; calcular estadísticas con controles realmente intercambiables o limitarse a descripción sin p-valor confirmatorio.
6. Informe con denominadores, pérdidas, CI, falsos positivos, intervalos, resultados negativos, desviaciones y archivos de auditoría no identificativos. Replicación independiente para cualquier promoción metodológica que la requiera.

La aprobación legal o de tratamiento, el preregistro y una cohorte válida son **puertas distintas**. Ninguna de ellas implica por sí sola `PASS_OPERATIONAL_GATE`, `L3_VALIDATED` ni categoría ontológica demostrada.

## Evidencias de cierre del issue #123, no del #120

El issue #123 puede considerarse `COHORT_READY_FOR_PREREGISTRATION` solo si existe evidencia realmente examinada de selección ex ante, permisos/custodia, fuentes de nacimiento, doble codificación independiente, cobertura temporal y grafo de sujetos por partición, con tamaños y pérdidas registradas. Si no se obtiene, el resultado correcto es `INSUFFICIENT_DATA` y un inventario negativo. El issue #120 solo se resolvería tras un preregistro válido y una evaluación externa fuera de muestra, con sus límites; un resultado empírico negativo puede ser un resultado científico válido, no evidencia de ontología.

En el corte documentado de `main` no hay cohortes reales admitidas (`real_cases=[]`, `real_cohorts=[]`, `artifacts=[]`), RRA mantiene siete bloqueos sin resolver y la validación externa `NOT_PERFORMED`. **No se deben actualizar estos campos por la mera incorporación de este dossier.**
