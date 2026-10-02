# SSAR · Liminalidad y Moiras · Fase 5

API optativa del desarrollo 1.25.0 R2. La versión pública permanece 1.24.1. `run_liminal_moirai` recibe posiciones, perturbaciones y raíces del núcleo ya suministradas; no calcula efemérides ni inspecciona casos personales. Su catálogo y sus reglas son hipótesis propias E en estado DEVELOPMENT, sin validación externa. El perfil genérico y S1 conservan sus políticas anteriores.

## Identidad, denominación y función

La identidad A procede de las consultas NASA/JPL registradas en la auditoría de fase 1. La denominación A se verifica por separado: Schmadel, catálogo técnico P3, o NASA Science P1 para Eris. NP1 describe la denominación mítica; no valida una función astrológica. Los antecedentes narrativos C tampoco convierten las reglas E en doctrina antigua ni en hechos de un vínculo.

| Cuerpo | Número / SPKID | Función E del plan R2 | Antecedente y límite |
| --- | --- | --- | --- |
| Hekate | 100 / 20000100 | `LIMINAL_THRESHOLD_GUIDANCE` | Teogonía y acompañamiento de Perséfone en el Himno; no prueba guía externa. |
| Persephone | 399 / 20000399 | `DESCENT_TRANSFORMATION_RETURN` | Descenso y retorno narrativos; no predice una reunión ni cambia el vínculo maternofilial por uno romántico. |
| Eris | 136199 / 20136199 | `DISCORD_EXCLUSION_RIVALRY` | Discordia y competencia, con alternativa constructiva; no acredita terceros o infidelidad. Es planeta enano. |
| Klotho | 97 / 20000097 | `THREAD_INITIATION` | Motivo del comienzo del hilo; no establece el inicio vivido de un episodio. |
| Lachesis | 120 / 20000120 | `MEASURE_DURATION_ALLOCATION` | Medida y asignación; no determina duración observada. |
| Atropos | 273 / 20000273 | `CUT_COMPLETION_IRREVERSIBILITY` | Corte y terminación; no prueba irreversibilidad más allá de una ventana observada. |
| Moira | 638 / 20000638 | `FATE_ALLOTMENT_CONTEXT` | Contexto de reparto; no establece destino metafísico. |

### Alcance de las fuentes consultadas

- [Schmadel, Dictionary of Minor Planet Names, quinta edición, 2003](https://link.springer.com/referencework/10.1007/978-3-540-29925-7), [capítulo consultado](https://link.springer.com/content/pdf/10.1007%2F978-3-540-29925-7_32.pdf): entradas 97 y 100, página impresa 24; 120, página 26; 273, página 39; 399, página 48; 638, página 63. Se consultaron entradas delimitadas, no el libro completo ni los avisos originales que éste cita. El catálogo atribuye los nombres a referentes míticos. Conserva propuestas históricas de nombres y una posible asociación de Hekate con el número cien expresamente conjetural; la circunstancia histórica de la denominación de Atropos no convierte su referente en una persona. Las funciones simbólicas que recoge el catálogo no constituyen evidencia de eficacia astrológica.
- [NASA Science, Eris, sección Namesake](https://science.nasa.gov/dwarf-planets/eris/): atribución nominal a la diosa griega de discordia. Se consulta esta sección para NAME_ORIGIN; la identidad sigue documentada por JPL.
- [Hesíodo, Teogonía, traducción Evelyn-White, Loeb 57, 1914](https://www.theoi.com/Text/HesiodTheogony.html), versos 211–232, 410–452 y 901–906: Moiras y Eris, prerrogativas amplias de Hécate y otra genealogía de las Moiras. Se mantienen las genealogías de Noche y de Zeus/Temis en sus respectivos pasajes. No se unifican en una sola versión. Los pasajes no fundamentan por sí solos todas las funciones individuales del perfil.
- [Hesíodo, Trabajos y días, misma traducción](https://www.theoi.com/Text/HesiodWorksDays.html), versos 11–26: dos modalidades de Eris, una destructiva y otra asociada a competencia productiva. El motor conserva esta alternativa frente a una lectura exclusivamente negativa.
- [Himno homérico a Deméter, traducción Gregory Nagy, CHS Harvard](https://chs.harvard.edu/primary-source/homeric-hymn-to-demeter-sb/), versos 25–61, 334–403, 438–440 y 445–470: audición de Hécate, descenso/retorno y acompañamiento. La traducción señala una variante en el pasaje de Hécate; el perfil no resuelve esa variante ni deduce una modalidad romántica.

El anfitrión digital de una traducción no se presenta como autor de la obra antigua. Las verificaciones nominales nuevas son locales a este perfil: no reescriben retroactivamente los bloqueos históricos de la auditoría inicial o de otros perfiles. La auditoría legible por máquina está en `ssar-liminal-moirai-source-audit.json`.

## Reglas geométricas y cobertura

El subperfil aplica conjunción/oposición con orbe inclusivo de 1,5°, objetivos del núcleo y marco eclíptico tropical. Exige identidad y nombre verificados, fuentes por alcance, anclaje core existente y precisión declarada. Las perturbaciones suministradas usan −30, −15, 0, +15 y +30 minutos; la preservación mínima es 0,8. El motor comprueba esta información declarada, no demuestra que una efeméride o documento externos sean auténticos.

Sin geometría, precisión, malla o búsqueda de anclaje completas, el contacto queda bloqueado. Con contacto pero sin anclaje o preservación suficiente puede ser apoyo secundario. Los miembros con preservación débil no permiten cualificar un complejo. Los identificadores de sujeto A/B se reservan para sinastría; compuesto/Davison usan RELATIONSHIP. Entradas duplicadas, referencias rotas y valores no finitos se rechazan.

`MOIRAI_CLUSTER` agrupa Klotho, Lachesis, Atropos y Moira. Conserva la cobertura de cada miembro y referencias a contactos existentes. No crea unidad, raíz o evento adicional. `cluster_strength` es null: no existe aún una magnitud común congelada, por lo que no se ejecutan máximo numérico o desempates por fuerza.

| Complejo | Miembros requeridos | Contexto opcional |
| --- | --- | --- |
| `LIMINAL_TRANSITION_COMPLEX` | Hekate y Persephone | Eris |
| `FATE_PROCESS_COMPLEX` | Klotho, Lachesis, Atropos y Moira | Eris |

La cualificación exige todos los miembros con contacto y robustez suficientes, al menos un significador cualificado con raíces core, búsqueda completa y dos grupos efectivos. No existe excepción de anclaje. Una sola agrupación permite compatibilidad, no cualificación. Sinastría comparte grupo; compuesto y Davison comparten otro. Equivalencia y dependencia técnica, estadística o desconocida se colapsan globalmente y de forma transitiva antes de proyectar los miembros; superposición semántica no demuestra independencia estadística.

Eris puede conservarse como contexto de interpretación: no sustituye un miembro, no añade el segundo grupo de un complejo y su falta de contacto no contradice automáticamente un complejo. Un NO_CONTACT evaluable de un miembro requerido sí puede contradecir su geometría, incluso cuando otro miembro falta. La interpretación funcional conserva sus propios bloqueos. Ausencia de datos nunca se convierte en contraevidencia.

Perséfone puede enlazarse con un contacto declarado de `DEMETER_PERSEPHONE_SEPARATION_RETURN_COMPLEX` de fase 4. La referencia requiere coincidencia de contexto, geometría, raíces, clave de evidencia y perturbaciones. El enlace no añade evidencia y no autentica por sí mismo el artefacto upstream.

Las cuatro evaluaciones permanecen separadas: geometría estructural, interpretación funcional, activación temporal y correspondencia documental. Las dos últimas son NOT_EVALUABLE en fase 5. La cobertura y los estados de ejecución describen sólo componentes y selecciones declarados; el contenedor permanece PARTIAL o NONE, sin evaluación global. Scoring, ontología y discriminadores permanecen sin efecto.

## Contrato de eventos para futuros estudios

`run_process_study` es un contrato independiente, `STANDALONE_STUDY_CONTRACT_NOT_M27`, sin cartas o complejos como entrada. No promueve activación temporal ni correspondencia documental SSAR. Los eventos deben definirse y preregistrarse antes de inspeccionar cartas. Un booleano declarativo comprueba esa condición contractual; no certifica cuándo se realizó realmente el registro.

Los datos admitidos requieren DOCUMENT u OBSERVATION, fuente, estado VERIFIED, precisión suficiente y separación entre hecho e interpretación. SELF_REPORT e INTERPRETATION no verifican por sí solos los hechos externos de este subperfil. Las fuentes y etiquetas de verificación son metadatos suministrados: este motor no consulta ni autentica documentos externos.

| Rol / afirmación | Regla de estudio | Contradictor o límite |
| --- | --- | --- |
| START_EVENT / INITIATION_OCCURRED | Inicio fechado en ventana de episodio y sujeto definidos. | Ausencia sólo con ventana terminada y observación completa. |
| DURATION_INTERVAL / DURATION_WITHIN_BOUNDS | Continuidad observada, dos fechas y límites preregistrados; días transcurridos = fin − inicio. | Medida fuera de límites contradice; duraciones incompatibles quedan insuficientes, sin escoger la más favorable. |
| CLOSURE_EVENT / CLOSURE_PERSISTED_IN_WINDOW | Cierre y persistencia dentro de ventana terminada completamente observada. | REOPENING_EVENT posterior al cierre del mismo episodio contradice incluso en ventana abierta/incompleta. |
| TRANSITION_EVENT / TRANSITION_OCCURRED | Fecha y dos estados distintos documentados. | Estado idéntico, desconocido o interpretación sin hecho bloquean. |
| DISCORD_EVENT / DISCORD_FREE_WINDOW | Ausencia observada de discordia sólo en ventana terminada y completa. | Discordia conocida contradice incluso en ventana abierta/incompleta; no demuestra infidelidad. |

La ventana incluye ambos extremos. Un evento debe quedar dentro de ella y no ser posterior a `as_of`; los hitos tienen fecha puntual. Un intervalo requiere continuidad observada, no sólo dos endpoints. Hechos esenciales inciertos bloquean afirmaciones de ausencia o cobertura positiva; un contradicto excluyente conocido sigue visible.

La deduplicación usa `fact_key` suministrado globalmente. Los alias del mismo hecho cuentan una sola vez; sus fuentes no añaden eventos. Si los alias discrepan en papel, fechas, episodio, sujeto o estados esenciales, el hecho queda sin admisión. Un alias pendiente idéntico no elimina un registro admitido. El motor no descubre que dos claves distintas describen el mismo hecho real: esa resolución corresponde al registro documental previo.

Los contradictores se buscan en todo el registro pertinente, aunque se omitan de `event_refs`. Una declaración de cobertura completa puede sustentar una ausencia, trazada como `claim_id:observation_coverage`; no crea un evento. El cierre nunca se declara irreversible para un futuro ilimitado. La evaluación es DOCUMENTARY_PROCESS_STUDY, con efectos astrológico, documental SSAR y ontológico NONE.

## Reproducción y pendientes

Los cuatro schemas públicos remiten al mismo archivo de definiciones empaquetadas. Los validadores reproducen íntegramente resultados desde entradas, catálogo y política; no aceptan estados, huellas, grupos o efectos alterados. El ejemplo público es enteramente sintético y se comprueba mediante `scripts/validate_ssar_liminal_moirai.py`. La matriz de fase 5 registra las 51 pruebas nuevas.

Fases 6–10 pendientes: puntos calculados, lotes, integración temporal M27, controles/congelación e integración canónica. Siguen pendientes magnitud común, máximo y desempate numéricos, validación externa e integración en informes. El cierre técnico de fase 5 no cambia esos pendientes ni la versión normativa.
