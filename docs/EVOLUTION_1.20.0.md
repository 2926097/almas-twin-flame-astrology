# ALMAS 1.20.0 · Síntesis root-first y temporalidad trazable

## Objetivo

ALMAS 1.20.0 profundiza la fase interpretativa abierta en 1.19.0. El cambio central es metodológico: la lectura deja de organizarse como una sucesión de técnicas y pasa a construirse desde **raíces independientes y motivos semánticos** ya presentes en el análisis canónico.

La release amplía el vocabulario hermenéutico y la capacidad temporal sin crear una segunda capa de cálculo. El principio operativo permanece:

`cálculo reproducible → raíces/motivos → interpretación astrológica → hermenéutica basada en fuentes → publicación`.

Los controles técnicos determinan qué información está disponible y con qué límites; la autoría desarrolla su significado sin mutar `canonical_analysis`.

## R1 · Protocolo de síntesis root-first

La síntesis interpretativa parte de las unidades estructurales consolidadas por M17/M18 y del grafo de motivos semánticos. Una técnica concreta aporta contexto o evidencia a una raíz; no se convierte automáticamente en un capítulo independiente.

La secuencia recomendada es:

`raíz → contactos concretos → funciones simbólicas → geometría → recurrencias → contexto de campo → temporalidad → hermenéutica → contraevidencia → síntesis`.

Este orden reduce dos fallos editoriales: la enumeración plana de aspectos y la inflación de técnicas dependientes como si fueran confirmaciones independientes.

## R2 · Hermenéutica de funciones y geometría

1.20 incorpora referencias y reglas interpretativas para recuperar el significado concreto de:

- funciones planetarias;
- conjunción, oposición, cuadratura, trígono y sextil;
- extremos angulares y nodales;
- superposición de casas con procedencia explícita;
- sustrato natal necesario para contextualizar una activación relacional.

La geometría calculada sigue perteneciendo a la clase epistemológica A/B correspondiente. La síntesis evolutiva o metafísica permanece distinguible como interpretación.

## R3 · Campo relacional y capas complementarias

La autoría puede integrar, cuando el canonical las contiene:

- compuesta y Davison como campo relacional;
- contactos planeta–ángulo;
- declinaciones y antiscios;
- dracónica y cruces dracónicos como reencuadre nodal;
- Fortuna y Espíritu dentro de la baseline helenística ya registrada;
- Juno y Eros como puntos secundarios `support_only`.

Estas capas no generan por sí solas una ontología. Su función es enriquecer o matizar raíces preexistentes y motivos ya trazados.

## R4 · Motivos interpretativos desarrollados

La release amplía la hermenéutica de motivos especialmente relevantes para relaciones de alta densidad simbólica:

- continuidad kármica y memoria relacional;
- transformación, poder y profundidad transpersonal;
- Quirón y `WOUND_REPAIR`;
- polaridad erótica, magnetismo y espejo;
- coherencia, consonancia y afinidad estructural.

La recurrencia sigue sujeta a independencia de familias. Un motivo repetido dentro de una misma familia dependiente no se multiplica como evidencia nueva.

## R5 · Temporalidad M26–M27

M26 conserva ahora `trigger_context` para que la capa de autoría pueda narrar una activación concreta sin recalcularla. La superficie puede identificar:

- planeta o punto transitante;
- objetivo natal;
- relación/aspecto;
- capas fuente/objetivo;
- orbe y límite de orbe;
- longitud transitante y objetivo;
- fuentes de método.

`trigger_context` es informativo para autoría y no modifica IAT.

La regla hermenéutica temporal es estrictamente **root-first**: un tránsito activa una arquitectura previa; no la crea.

## R6 · Generador autónomo TTRANSIT

1.20 añade generación `TTRANSIT` desde posiciones geocéntricas y endpoints natales de raíces M17. El generador utiliza únicamente `aspect_policy` explícita y aspectos registrados.

Cadena:

`planeta en tránsito → aspecto declarado → endpoint natal de raíz → señal TTRANSIT → M26 → autoría`.

El generador no infiere orbes implícitos, no introduce aspectos menores por defecto y no reinterpreta endpoints de otras capas como natales.

La fuerza efectiva conserva la regla M26 existente; la generación automática no redefine pesos ni scoring.

## R7 · Fixture temporal interpretativo

`examples/temporal-reading.synthetic.json` documenta una señal completamente sintética:

`raíz Venus–Plutón → Saturno en tránsito → cuadratura → Venus natal → integración → función evolutiva → límite factual`.

El ejemplo demuestra que la lectura temporal distingue función transitante, función objetivo y geometría antes de volver a la raíz.

El límite factual es obligatorio: la señal no predice por sí sola separación, compromiso, contacto, reconciliación ni decisiones de otra persona.

## R8 · Fuentes

La ampliación 1.20 registra fuentes de método y significado para compuesta/Davison, declinaciones, antiscios, sinastría/casas y tránsito. Las fuentes aportan procedencia y lenguaje interpretativo; su mera presencia no añade puntuación.

Las correspondencias doctrinales siguen sujetas a sus propias anclas, `supports[]`, `does_not_support[]` y techo inferencial.

## Validación funcional

En el último head funcional previo al bump de release:

- Núcleo Python 3.10: 537 tests, PASS;
- Núcleo Python 3.12: 537 tests, PASS;
- Contrato público: PASS;
- Backend astronómico: PASS.

La prueba temporal enlaza el fixture editorial con la señal producida realmente por el generador M26. La comparación de `effective_strength` usa tolerancia numérica apropiada para coma flotante sin redondear ni alterar el motor.

## Invariantes

1. `canonical_analysis` sigue siendo la única verdad analítica.
2. La autoría no recalcula cartas, raíces, índices ni scores.
3. Una capa complementaria contextualiza; no crea automáticamente una raíz independiente.
4. Un tránsito activa estructura previa; no establece ontología.
5. `trigger_context` no modifica IAT.
6. TTRANSIT usa `aspect_policy` explícita y endpoints existentes.
7. No se introducen nuevos pesos, thresholds ni discriminadores activados.
8. No se afirma validación científica de la astrología ni de ontologías metafísicas.
9. La predicción de hechos o decisiones personales requiere evidencia documental independiente y no se deriva de una señal astrológica.
