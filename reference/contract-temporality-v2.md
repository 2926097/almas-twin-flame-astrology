# ALMAS · Temporalidad contractual v2

## 1. Principio

La temporalidad no crea contrato.

Orden obligatorio:

`ESTRUCTURA → CLAUSULA → ANCLA_TEMPORAL → HECHO → ESTADO_DE_CICLO`

## 2. Tres planos temporales

### T1 · ACTIVACIÓN
¿Cuándo entra en expresión una raíz contractual ya existente?

Fuentes técnicas:
- tránsitos;
- progresiones;
- arco solar;
- atacires preregistrados;
- compuesta/Davison progresada o dirigida;
- eclipses bajo reglas definidas;
- carta de evento.

### T2 · DESARROLLO
¿La misma función reaparece en ventanas/eventos independientes?

Requiere recurrencia de la misma raíz o cláusula, no sólo repetición de palabras interpretativas.

### T3 · INTEGRACIÓN / TRANSFORMACIÓN / CIERRE
¿Los hechos muestran que la función cambia de manera estable?

No se asigna desde astrología futura.

## 3. Estados temporales v2

- `LATENT`: estructura presente sin activación suficiente.
- `TRIGGERED`: una ventana anclada activa la raíz.
- `ACTIVE`: cláusula expresándose en el periodo observado.
- `RECURRING`: reaparece en más de una ventana o evento independiente.
- `INTEGRATING`: hechos sugieren cambio coherente con la firma preregistrada, aún no consolidado.
- `EMBODIED`: la integración se expresa en forma estable/documentada.
- `TRANSFORMED`: la función persiste en modalidad diferente.
- `CLOSED`: seguimiento suficiente muestra que la misma repetición ya no organiza la cláusula.
- `NOT_EVALUABLE`.

Compatibilidad con nombres históricos:
- ACTIVADA → TRIGGERED/ACTIVE;
- EN_DESARROLLO → ACTIVE/RECURRING;
- INTEGRADA → EMBODIED;
- TRANSFORMADA → TRANSFORMED;
- CERRADA → CLOSED.

## 4. Estado de una ventana

Toda ventana temporal se etiqueta:

- `RETROSPECTIVE_CONFIRMED` — fecha pasada con hechos disponibles;
- `RETROSPECTIVE_UNCONFIRMED` — fecha pasada sin hechos suficientes;
- `CURRENT_ACTIVE` — periodo actual con activación anclada;
- `PROSPECTIVE_ACTIVATION` — fecha futura calculada;
- `EXPLORATORY` — técnica/ciclo aún exploratorio;
- `UNANCHORED` — señal sin raíz estructural.

Una ventana `PROSPECTIVE_ACTIVATION` no puede por sí sola producir EMBODIED, TRANSFORMED o CLOSED.

## 5. Anclaje

Una señal temporal válida debe apuntar a:

- root_id;
- clause_id;
- structural_family;
- temporal_family;
- exactitude/orb;
- preregistered_window_rule.

Sin root_id estructural: `UNANCHORED`.

## 6. Independencia temporal

Dentro de una raíz y familia temporal conservar la señal más fuerte.

No contar múltiples fechas del mismo ciclo como familias independientes.

Familias:
- TPROG;
- TDIR;
- TTRANSIT;
- TECLIPSE;
- TREL;
- TATACIR preregistrado.

Atacires exploratorios se etiquetan EXPLORATORY y no elevan confirmación estructural.

## 7. Evento documental

Un evento puede:

- confirmar que una cláusula estaba activa;
- aportar hechos para integración;
- mostrar cambio de modalidad;
- refutar una interpretación.

No puede crear retrospectivamente la cláusula.

## 8. Regla de futuro

Prohibido inferir desde una ventana futura:

- contacto;
- mensaje;
- reconciliación;
- separación;
- decisión;
- consentimiento;
- reunión;
- cierre.

La salida correcta describe **qué raíz/cláusula estaría activada** si la técnica es válida.

## 9. Integración y cierre

### INTEGRATING
Requiere:
- firma preregistrada;
- al menos un hecho posterior compatible;
- seguimiento insuficiente para estabilidad plena.

### EMBODIED
Requiere:
- firma preregistrada;
- hechos repetidos/coherentes;
- forma estable;
- contraevidencia revisada.

### TRANSFORMED
Requiere:
- continuidad funcional identificable;
- cambio claro de modalidad;
- hechos documentados.

### CLOSED
Requiere:
- firma de cierre;
- seguimiento suficiente;
- cese de la misma repetición organizadora;
- no basarse sólo en distancia o ausencia de contacto.

## 10. Relación con IAT

IAT sigue midiendo activación de raíces preexistentes.

El módulo contractual añade:
- clause_mapping;
- window_status;
- lifecycle_state.

IAT no modifica IAP.

## 11. Salida

Por cláusula:

- structural_state;
- lifecycle_state;
- temporal_windows;
- anchored_root_refs;
- event_refs;
- fulfillment_signature;
- factual_match;
- counterevidence;
- why_not_more_advanced.
