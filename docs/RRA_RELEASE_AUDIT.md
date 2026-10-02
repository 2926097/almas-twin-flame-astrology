# Auditoría de implementación · ALMAS 1.25.0 R3 · RRA 1.0

Revisión del 2 de octubre de 2026 sobre la base `73caa8c7356139f4da87a97cbf91f4005ce1840c`. Se implementan las diez fases técnicas del plan R3 como extensión `FROZEN_EXPERIMENTAL`. El cierre técnico no equivale a validación externa de correspondencias relacionales, que conserva `NOT_PERFORMED`.

## Auditoría, corpus y congelación

La auditoría corregida reconoce el solver de perfecciones preexistente y distingue búsqueda exacta, carta y activación. El corpus registra material efectivamente consultado, pasajes, clases A–E, prácticas de ubicación y la diferencia entre revolución mensual solar medieval y retorno lunar longitudinal moderno. Las extensiones compuesta, Davison, dracónica, SSAR y evento son hipótesis E. Siete políticas, contratos y un manifiesto verificable fijan cuerpos, tolerancias, aspectos, orbes, ubicaciones, ventanas, dependencia y controles antes de analizar casos personales.

## Motor, overlays y dependencia

El solver conserva cruces, tangencias estacionarias y pasadas directas y retrógradas. Moira 6.8.2 exige un kernel local verificado y registra capacidades y procedencia. Las cartas emplean ubicaciones explícitas; la incertidumbre natal o ubicación ausente bloquea ángulos. Los overlays sólo se anclan a raíces core M17 existentes y elegibles; los significadores SSAR requieren cualificación previa. Los derivados requieren padres y método, sin reconstrucción independiente de cartas aportadas. La conjunción obligatoria con la referencia no aporta geometría nueva.

El grafo agrupa dependencias heredadas, variantes, ubicaciones y alias documentales. Las unidades efectivas y R6 describen recurrencia de hechos deduplicados; no acreditan independencia estadística de fuentes. Una activación no crea raíces ni altera índices, IAT, gates, discriminadores u ontología.

## Recurrencia, robustez, negativos e informes

Se separan instante exacto, delta del evento y ciclo activo, con incertidumbre, cobertura y censura derecha explícitas. Los controles de desplazamiento de secuencias, permutación y fechas fijadas conservan universo y presupuesto; su excedencia Monte Carlo es exploratoria. Las cartas de evento que requieren recálculo en el control bloquean ese ámbito. Ocho ablaciones examinan orbe, ángulos, capas derivadas y cuerpos; se registra sensibilidad de longitudes natales, eventos y ubicación. No se fabrica `CONTRADICTED` sin una hipótesis previa con contradictor operacional.

El informe consume resultados canónicos y expone estructura, retorno, contactos, eventos, recurrencia, robustez, controles, negativos y alcance interpretativo. M30 valida el anclaje y M31 conserva las rutas de autoría. Un canónico histórico no recibe cálculos silenciosos: RRA exige una ejecución nueva y SSAR activo. El CLI `almas-returns` permite solicitud, snapshot, configuración de backend, salida y texto de informe mediante archivos.

## Evidencia de verificación

Las 19 pruebas originales RRA aprobaron cálculo exacto, wrap angular, tres pasadas, tangencia, overlays, cualificación, incertidumbre, ubicaciones, deduplicación, controles, manipulación, recurrencia y pipeline M00–M31. Una prueba adicional comprueba que el texto de informe expone contactos, identidad obligatoria, ablaciones, control y negativos. Las nueve pruebas de aislamiento público aprueban tras registrar el nuevo fixture sintético y actualizar su recuento a 33; no se relajan reglas de privacidad.

`validate_public_contract.py`, `validate_ssar_release.py` y `validate_ssar_baseline.py` aprobaron. La regresión conserva salidas deterministas y archivos core protegidos idénticos; los metadatos de versión legacy se informan por separado. `validate_return_runtime.py` reprodujo tres casos astronómicos ficticios y cinco pasadas con DE440s y contraste Skyfield 1.55 a tiempo TT común, tolerancia de dos segundos de arco y comprobación de relocalización. El recibo está en `validation/returns/runtime-receipt.json`.

La prueba independiente de instrucciones confirmó que SSAR desactivado exige ejecución nueva y que un retorno no aumenta IAT ni resuelve origen monádico. La batería completa y los workflows por commit se consultan en la PR #85. El primer pase local empezó antes de actualizar el manifiesto; su fallo de cobertura se corrigió y las pruebas afectadas se repitieron con éxito. El resultado remoto del commit final es el criterio de cierre de integración.

## Límites y publicación

Los overlays suministrados, la precisión física de referencias y la independencia documental no quedan certificados por un hash o por aprobar schemas. El muestreo no garantiza exhaustividad para proveedores arbitrarios que oscilen más rápido que su paso. Retornos de cuerpos secundarios sin efemérides o cualificación conservan bloqueo. La validación externa con relaciones y eventos ajenos al diseño queda pendiente; ningún caso personal se usó para fijar políticas.

La revisión se integra mediante PR #85 y conserva la identidad pública 1.25.0 con sufijo documental R3. La etiqueta `v1.25.0`, ya publicada para SSAR, no se mueve ni se vuelve a publicar. El workflow de release termina sin error cuando esa etiqueta pertenece a otro commit, preservando el artefacto original.
