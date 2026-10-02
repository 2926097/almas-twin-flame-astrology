# SSAR · Familias y díadas de desarrollo

La fase 4 añade `run_families` como API optativa de hipótesis E. Consume posiciones, perturbaciones y raíces core upstream; no calcula efemérides ni eventos. Las políticas genérica y S1, los modelos AF/KA/AG/LG, sus índices y la versión pública 1.24.1 se conservan. La integración en M14, canonical e informes corresponde a la fase 10. La cobertura completa del release y la validación externa siguen pendientes.

## Procedencia y función

El catálogo incorpora las siete entradas S1 mediante una copia de sus fuentes y reglas mínimas, con el identificador de la nueva política; no modifica S1. Añade identidades JPL ya auditadas en fase 1 y atribuciones nominales de Schmadel, Dictionary of Minor Planet Names, quinta edición, copyright 2003, edición electrónica publicada en 2007. La auditoría enlaza páginas concretas. Se utiliza como catálogo técnico P3: no se afirma consulta directa de las comunicaciones originales que cita. La identidad astronómica, la denominación y la hipótesis interpretativa son roles distintos.

La familia erótica reúne Eros, Amor y Cupido. Su pertenencia semántica no aumenta por sí sola el número de grupos efectivos. Afrodita sólo funciona como overlay a Venus: no tiene función independiente ni grupo de corroboración propio. No sustituye a Venus o a sus raíces. Las salidas conservan todos los contactos admisibles, los componentes faltantes y los bloqueados; un componente no suministrado nunca se rellena con cero.

Eros–Psyche usa como antecedente comparativo Apuleyo VI, ya consultado en fase 3. Deméter–Perséfone usa el Himno homérico a Deméter, versos 1–39, 334–403 y 445–470, traducción Gregory Nagy. Es una relación madre–hija con separación impuesta y retorno condicionado; la elección del motivo relacional es E y no convierte ese relato en una pareja romántica ni predice reencuentros. Plutarco, De Iside et Osiride 13–19, traducción Babbitt 1936, conserva búsqueda, fragmentación y versiones discrepantes. Su uso para una recomposición funcional es E; no representa un consenso de toda la tradición egipcia.

Isis queda NP4 por atribución documental ambigua. Su identidad permite calcular geometría, pero su método nominal y el complejo Isis–Osiris quedan bloqueados funcionalmente. Siva 1170 conserva su identidad y origen documentados como candidato; no se sustituye automáticamente la etiqueta SHIVA. Shakti sigue sin identidad resuelta y la variante doctrinal del complejo no está seleccionada. Parvati no es sustituto automático. Shiva–Shakti conserva esos tres bloqueos, aunque se aporten posiciones numéricas.

## Contrato operativo

Cada observación lleva un contexto explícito: sujeto A/B para SYNASTRY y RELATIONSHIP para COMPOSITE/DAVISON. Incluye la clave de evidencia upstream, geometría, búsqueda de anclaje y perturbaciones. Una unidad se crea por observación con referencia U:ID. Las aristas usan esos identificadores y las reglas de fase 2. El mismo contacto en el mismo contexto debe compartir aparición; una misma geometría en cartas distintas no se confunde por coincidencia numérica. La calidad e identidad de la raíz core suministrada se comprueban con el contrato heredado; la API no demuestra que el artefacto upstream sea auténtico.

El subperfil de apariciones mantiene conjunción/oposición de 1,5 grados, targets publicados en S1, rejilla −30/−15/0/+15/+30 minutos y conservación mínima del mismo aspecto de 0,8. Afrodita restringe el target a Venus. Las fuentes esenciales, clase E y procedencia autorizada se fijan por catálogo; no se pueden reemplazar mediante una fuente ajena del mismo nivel P.

Los contactos cruzados son registros distintos, con cuerpos, sujetos y longitudes explícitos. Usan conjunción/oposición de 1 grado inclusivo y la misma rejilla de robustez. Su orden es el de los componentes de la díada; A→B y B→A significan el primer cuerpo en A frente al segundo en B y su intercambio de sujetos. Son contactos distintos, no dos representaciones inversas del mismo par de endpoints. La orientación inversa del mismo contacto se deduplica. Los enlaces de anclaje deben reproducir identidad, sujeto, longitud y perturbaciones de apariciones existentes de sinastría. No crean raíces, unidades o grupos.

Un complejo funcional cualificado requiere búsqueda direccional completa, contacto robusto en ambos sentidos con endpoint enlazado a una aparición admisible y anclada, presencia admisible de ambos componentes, al menos un significador cualificado y dos grupos efectivos. Una sola raíz excepcional no exime estos requisitos. La ausencia de geometría, identidad, precisión o cobertura esencial permanece NOT_EVALUABLE; un contacto negativo evaluado sólo contradice la geometría definida. La interpretación funcional no equivale a conducta ni ontología.

Las equivalencias, dependencias técnicas, estadísticas y desconocidas permanecen distinguibles en el grafo, aunque todas estas últimas se agrupan conservadoramente por componentes conexas. SEMANTIC_OVERLAP se registra sin declarar equivalencia. SYNASTRY pertenece a TROPICAL_PAIR; COMPOSITE y DAVISON comparten RELCHART. La independencia estadística sigue sin establecerse. El grafo global fija las particiones antes de proyectarlas sobre cada familia o díada, evitando contar de nuevo un contacto compartido.

## Cuatro alcances y fuerza

Cada díada publica STRUCTURAL_GEOMETRY, FUNCTIONAL_INTERPRETATION, TEMPORAL_ACTIVATION y DOCUMENTARY_STRUCTURAL_CORRESPONDENCE. No existe estado global. La geometría robusta puede ser SUPPORTED aunque una atribución nominal ambigua bloquee la interpretación. Activación temporal y correspondencia documental quedan NOT_EVALUABLE porque esta fase no ejecuta M27 ni analiza eventos. El alcance documental es STRUCTURAL y no se confunde con correspondencia de una activación temporal futura.

La política es DEVELOPMENT, sin magnitud común de fuerza definida y congelada. Por tanto `cluster_strength=null` y `NO_RANKING_WITHOUT_FROZEN_COMMON_MAGNITUDE`: no se calcula un máximo entre números heterogéneos, no se elige un ganador y no se inventa un desempate. La prueba de contactos iguales verifica su conservación conjunta, no valida una regla numérica futura. Definir esa magnitud, su universo y desempates exigiría una política nueva y controles posteriores.

La salida genérica anidada describe exclusivamente apariciones y dependencias. No declara las capas de díadas como pendientes: el contenedor de fase 4 publica sus propios resultados, alcances y bloqueos. Los arrays genéricos `complexes` y `mythic_dyads` siguen vacíos; ningún consumidor legacy recibe complejos nuevos. El contenedor permanece PARTIAL cuando hay evaluación y NONE cuando no se suministran datos. Las familias vacías sólo documentan componentes faltantes, sin afirmar una búsqueda negativa.

## Reproducción

`build_families_request` materializa fuentes y apariciones; `run_families` aplica las políticas empaquetadas; `validate_families_result(result, request=request)` reproduce la salida completa, incluida la huella SHA-256 del catálogo. La desactivación no exige jsonschema ni inspecciona históricos. Los contratos estrictos rechazan campos, cuerpos o contextos no declarados y fijan ausencia de efectos en scoring, ontología y discriminadores.

`examples/ssar-families.synthetic.json` contiene un caso geométrico artificial de Eros–Psyche, independiente de casos privados. La suite incluye negativos, ambigüedades, dependencias, duplicados, overlays y manipulación de resultados. Las pruebas conservan el núcleo mediante `validate_ssar_baseline.py` y el contrato público.
