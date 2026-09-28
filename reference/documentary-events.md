# ALMAS · Capa documental de hechos y biografía

## 1. Finalidad

Incorporar acontecimientos reales sin contaminar retrospectivamente la arquitectura astrológica o contractual.

Regla central:

`ESTRUCTURA_CONGELADA → EVENTO_DOCUMENTADO → FUNCIÓN_PROBATORIA`

Nunca:

`EVENTO_CONOCIDO → BUSCAR_ASPECTOS → INVENTAR_CLAUSULA`

## 2. Dos pasadas obligatorias

### PASADA A · Estructural
Se congelan:

- tareas previas;
- raíces;
- causas;
- roles;
- tarea común;
- cláusulas;
- firmas de integración/cierre;
- reglas temporales.

La pasada A no puede usar eventos posteriores para redefinir lo que “debía” existir.

### PASADA B · Documental
Se incorporan hechos para:

- corroborar activación;
- evaluar integración;
- aportar contraevidencia;
- determinar viabilidad real;
- determinar reciprocidad factual;
- identificar cambio de modalidad.

## 3. Calidad documental

### DQ1_PRIMARY_DOCUMENT
Documento primario verificable: acta, registro, carta fechada, documento oficial, archivo original, comunicación con metadatos disponibles.

### DQ2_DIRECT_SELF_REPORT
Relato directo de una de las personas sobre un hecho propio.

### DQ3_CORROBORATED_REPORT
Relato apoyado por más de una fuente independiente.

### DQ4_SECONDARY_REPORT
Información de segunda mano o reconstrucción posterior.

### DQ5_UNVERIFIED
Afirmación no verificada.

La calidad documental no equivale a importancia metafísica.

## 4. Tipo de evento

- FIRST_MEETING
- CONTACT
- CONVERSATION
- RELATIONSHIP_CHANGE
- COMMITMENT
- SEPARATION
- RECONCILIATION
- NO_CONTACT
- MARRIAGE
- BIRTH
- DEATH
- MOVE
- TRAVEL
- FAMILY_EVENT
- WORK_OR_SERVICE
- HEALTH_EVENT
- SPIRITUAL_EVENT
- CONFLICT
- BOUNDARY
- OTHER

El tipo es descriptivo. No contiene por sí solo interpretación.

## 5. Separación hecho / interpretación

Cada registro contiene:

- `fact_statement`: descripción mínima verificable;
- `interpretations`: cero o más lecturas;
- `source_refs`;
- `quality`;
- `date_precision`;
- `privacy_class`.

Ejemplo sintético:

`fact_statement: "A y B se conocieron presencialmente el día X"`

no:

`"el destino hizo que se reencontraran"`.

La segunda frase sería una interpretación E o C según fuente, nunca el hecho.

## 6. Precisión temporal

- EXACT_DATETIME
- EXACT_DATE
- MONTH
- YEAR
- RANGE
- APPROXIMATE
- UNKNOWN

No usar una hora inventada para construir carta de evento.

## 7. Función probatoria

Un evento puede marcarse como:

### ACTIVATION_CORROBORATION
Corrobora que una raíz/cláusula ya definida estaba activada.

### FULFILLMENT_EVIDENCE
Aporta hechos frente a una firma preregistrada.

### COUNTEREVIDENCE
Contradice una inferencia o desenlace supuesto.

### VIABILITY_FACT
Define forma real del vínculo.

### RECIPROCITY_FACT
Aporta bilateralidad/asimetría observable.

### PHENOMENOLOGY_DOCUMENT
Registra experiencia subjetiva sin convertirla en ontología.

### CONTEXT_ONLY
Contexto biográfico sin función confirmatoria.

## 8. Regla de no creación

Un evento no puede:

- crear una raíz;
- crear una cláusula;
- elevar un origen;
- convertir una sincronía en contrato;
- validar una técnica no preregistrada.

Sí puede cambiar:

- estado temporal;
- evaluación de cumplimiento;
- viabilidad;
- reciprocidad real;
- contraevidencia.

## 9. Privacidad

Clases:

- PUBLIC_VERIFIABLE
- PRIVATE_AUTHORIZED
- PRIVATE_RESTRICTED
- SYNTHETIC

GitHub sólo publica eventos PUBLIC_VERIFIABLE o SYNTHETIC.

Los casos privados nunca se exportan al repositorio público.

## 10. Versionado del ledger

El ledger es append-only para hechos.

Una corrección no borra silenciosamente el registro anterior: añade:

- supersedes_event_id;
- correction_reason;
- source_ref.

## 11. Salida

Cada evento contiene:

- event_id;
- subjects;
- event_type;
- date/date_range;
- date_precision;
- place_general cuando sea necesario;
- fact_statement;
- documentary_quality;
- source_refs;
- privacy_class;
- evidence_roles;
- linked_root_refs;
- linked_clause_refs;
- interpretations;
- counterevidence_effect;
- supersedes_event_id.
