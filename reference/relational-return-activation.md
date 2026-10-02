# Activación relacional por retornos · RRA 1.0 · ALMAS 1.25.0 R3

Estado: **FROZEN_EXPERIMENTAL**. Política congelada el 2 de octubre de 2026. La implementación técnica y su comprobación astronómica no constituyen validación empírica de correspondencias relacionales. Ningún caso personal se empleó para seleccionar cuerpos, orbes o ventanas.

## Alcance y separación epistemológica

A son posiciones y tiempos calculados, datos documentales y fuentes de precisión. B identifica el retorno longitudinal de un cuerpo a su propia longitud de referencia. C queda limitado a los pasajes históricos efectivamente consultados. D identifica prácticas contemporáneas atribuidas a sus autores. E comprende las reglas del proyecto: overlays sistemáticos, ventanas, estados técnicos, controles y recurrencia.

El retorno no crea raíces, significadores ni complejos. No cambia AF/KA/AG/LG, IEM, IDD, IRC, ICC, ICE, IAT, gates o discriminadores. `structural_scoring_modified=false`, `ontology_effect=NONE`, `discriminator_effect=NONE`, `iat_modified=false`. R1–R6 describen integración técnica; no son intensidad espiritual ni escalas del vínculo.

## Arquitectura y entrada

`return_activation.run_return_activation` recibe una solicitud explícita, un backend por capacidades, el registro M17 de raíces y la estructura SSAR previa. `attach_return_activation` devuelve una copia del snapshot con `ssar.temporal_activation`; el ensamblador contrasta sus raíces contra M17. Los objetos antiguos siguen validándose mediante el validador SSAR congelado, sin modificar sus recursos o hashes. La extensión se valida por separado y debe conservar exactamente la estructura SSAR a la que se ancla.

En una ejecución nueva con `configured_handlers`, `return_activation_request` se procesa después de SSAR y antes del ensamblaje M30. Se exige SSAR activo. Un `canonical_analysis` ya importado conserva prioridad y no recibe cálculos añadidos silenciosamente. El CLI independiente acepta un snapshot con `independent_roots.roots` y `ssar` activo.

Cada reloj declara propietario, cuerpo, carta/punto homólogo de referencia, intervalo completo de búsqueda, variantes de ubicación, calidad natal, fiabilidad angular e incertidumbre longitudinal. Cada carta declara capa, procedencia y puntos anclados a raíces elegibles. Los puntos derivados requieren padres y método; un punto SSAR exige una aparición previamente `QUALIFIED_SIGNIFICATOR`. Declarar un método es procedencia, no verificación independiente de la carta aportada: RRA no reconstruye aquí los overlays derivados, que deben proceder de los módulos canónicos previos.

Cada evento declara tipo, hecho, `fact_key`, fuentes, fecha/offset o zona IANA, certeza, incertidumbre y si ya ocurrió. `fact_key` identifica el mismo hecho aunque se describa mediante alias; distintos hechos requieren claves distintas. Su declaración no acredita independencia de fuentes. Una fuente con varias descripciones no aumenta la recurrencia.

## Búsqueda y cartas

`find_all_return_passes` reutiliza el solver de perfecciones. Busca cruces y mínimos estacionarios, conserva todas las pasadas y exige residual ≤10⁻⁵ grados, tolerancia numérica de intervalo 0,01 segundos y límites de muestreo. La tolerancia del algoritmo no equivale a exactitud física de 0,01 segundos: ésta depende de la efeméride, el modelo temporal y la precisión de la referencia. La reducción angular evita cancelación alrededor de cero. Los pasos de muestreo se registran; no se afirma exhaustividad para un proveedor arbitrario que oscile más deprisa que el muestreo.

El backend Moira usa la versión 6.8.2 y un kernel JPL local verificado. No se sustituyen cuerpos ausentes, no se descargan efemérides durante el cálculo y no se inventan coordenadas. Las cartas de retorno y sus posiciones deben compartir procedencia. La referencia dracónica es una longitud simbólica fija; no se interpreta como posición física del cuerpo dracónico transitante.

Sol, Luna, Mercurio, Venus, Marte, Júpiter y Saturno son ordinarios. Los demás requieren cualificación SSAR previa y capacidad real del backend; ausencia de efemérides produce `blocked`. La mera catalogación de un asteroide no basta. Mercurio no recibe una prioridad interpretativa por defecto. Recurrencias de un planeta sobre un punto no homólogo, ángulos, declinaciones o antiscios quedan fuera del retorno longitudinal V1 y requieren políticas independientes.

## Activación y dependencia

Se inspeccionan todos los aspectos congelados (0°, 60°, 90°, 120°, 180°) entre posiciones de retorno y todos los objetivos habilitados. Orbe máximo inclusivo 1°; ablación 0,5°. Si orbe más incertidumbre excede el límite, el contacto se excluye. Un objetivo sensible a la hora debe declarar fiabilidad e incertidumbre. Las casas y ángulos del retorno se bloquean con ubicación desconocida o incertidumbre natal no nula; pueden conservarse posiciones planetarias.

Cada contacto conserva capa, raíz, grupo, geometría y orbe. La conjunción obligatoria del cuerpo retornante con su referencia se registra como `automatic_identity_contact`; no aporta geometría nueva ni apoyo documental por sí sola. Dependencias declaradas y clusters heredados se agrupan; raíces sin cluster acreditado se agrupan conservadoramente. Los derivados y variantes no son corroboraciones ontológicas independientes. Las unidades efectivas `(grupo de dependencia, fact_key)` son una medida operacional deduplicada; el sistema no acredita independencia estadística.

R1 es retorno sin contacto anclado; R2 añade contacto natal; R3, sinástrico; R4, relacional/derivado; R5, SSAR cualificado; R6, al menos dos hechos documentales diferentes sobre una misma raíz. `independent_event_count=null` mientras no haya un protocolo de independencia externo. No se suman R1–R6 a índices.

## Eventos, negativos y controles

La ventana exacta simétrica se fija por cuerpo en `return-event-window-policy.json`. Su elección es E, no doctrina ni calibración empírica. El ciclo activo va desde una pasada hasta la siguiente, o el límite derecho censurado de búsqueda. El delta exacto y la pertenencia al ciclo se mantienen separados. Una fecha fuera de cobertura, futura o con incertidumbre que cruza la frontera no puede recibir `SUPPORTED`.

`SUPPORTED` significa contacto no tautológico y correspondencia temporal evaluable; `COMPATIBLE`, contacto/ciclo compatible sin dicho apoyo; `INSUFFICIENT`, ausencia de correspondencia; `NOT_EVALUABLE`, datos o cobertura insuficientes. RRA no fabrica `CONTRADICTED`: para ello haría falta una hipótesis documental previa con un contradictor operacional. Conserva `no_return_in_window`, `no_activation`, `weak_activation`, `activation_without_event`, `event_without_activation` y bloqueos. Los resultados sobre fechas control se conservan en las réplicas del modelo nulo, no se mezclan con hechos reales.

Se ejecutan desplazamientos conjuntos de fechas, controles fijados de antemano o permutaciones. El universo completo de relojes, capas, aspectos, pasadas y ubicaciones permanece idéntico. Las posiciones de referencia permanecen fijas: es un control condicional de temporalidad. Si una carta EVENT exigiría recalcularse al mover el evento, el modelo nulo queda `NOT_EVALUABLE`; no se simula con una carta congelada como si fuera una búsqueda completa. No se prueba intercambiabilidad de la población real.

Presupuesto y semilla se fijan sin parada anticipada. `p_mc=(k+1)/(M+1)` y resolución `1/(M+1)` describen excedencia exploratoria, nunca probabilidad metafísica. Las permutaciones sin variación se identifican como no informativas. `annual_return_summary` informa densidad anual sin duplicar ubicaciones; no es una inferencia causal ni un ensayo poblacional.

## Robustez e informes

Ablaciones: medio orbe, sin ángulos, sin dracónica, sin cartas relacionales, sin SSAR, sin eventos, sin retornos rápidos y sin secundarios. Las variantes geográficas se conservan separadas. La incertidumbre longitudinal natal puede generar nuevas búsquedas ±incertidumbre; sus instantes y números de pasadas se guardan como sensibilidad, sin promoverlos a validación documental. La incertidumbre del evento se evalúa mediante intervalos.

`render_ssar_with_returns` conserva el informe SSAR previo y añade retornos, raíz activada, eventos/deltas, recurrencia, robustez, controles y resultados negativos. M31 dispone de rutas opcionales. La interpretación de una función relacional sigue dependiendo de arquitectura previa y fuentes; Venus o Marte no implican por sí mismos amor, sexualidad, matrimonio, destino o reciprocidad.

## Reproducción

```bash
pip install -e '.[schema-validation,astronomy-moira]'
almas-returns --request request.json --snapshot snapshot.json \
  --backend-config backend.json --output execution.json --report report.md
```

`backend.json` contiene los campos de `MoiraBackendConfig`: kernel local, SHA-256, familia y sistema de casas. Las entradas se validan antes de escribir. La salida conserva solicitud, raíces, estructura SSAR, policy hash, procedencia y hash astronómico. `validate_return_activation` reproduce overlays/eventos/controles desde el snapshot; con backend recalcula también efemérides. Un hash no es una firma ni acredita autenticidad externa.

Pruebas sintéticas: `tests/test_return_activation.py`. Comparación Moira/Skyfield: `scripts/validate_return_runtime.py`, recibo `validation/returns/runtime-receipt.json`. La validación relacional externa permanece `NOT_PERFORMED` y requiere una cohorte preregistrada no utilizada en el diseño.
