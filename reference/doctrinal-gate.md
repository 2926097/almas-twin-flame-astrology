# Gate doctrinal ALMAS

## 1. Finalidad

El Gate doctrinal controla la transición entre **fuente** e **interpretación**.

Su objetivo es impedir dos errores:

1. atribuir a una tradición una afirmación que esa tradición no contiene;
2. convertir una semejanza histórica o simbólica en confirmación astrológica.

## 2. Tipos de relación con la fuente

Toda afirmación doctrinal o hermenéutica debe usar uno de estos estados:

- `DIRECT_DOCTRINE`: la afirmación aparece explícitamente en una fuente primaria identificada.
- `ACADEMIC_DESCRIPTION`: la afirmación describe un fenómeno, tradición o genealogía mediante una fuente académica.
- `HISTORICAL_ANTECEDENT`: existe un motivo anterior formalmente comparable, sin identidad doctrinal demostrada.
- `COMPARATIVE_ANALOGUE`: dos conceptos pueden compararse, pero pertenecen a doctrinas distintas.
- `CONTEMPORARY_USAGE`: vocabulario o experiencia emic documentada.
- `PROJECT_OPERATIONALIZATION`: ALMAS transforma un concepto doctrinal en una regla astrológica propia.
- `PROJECT_SYNTHESIS`: síntesis general creada por ALMAS a partir de múltiples capas.

## 3. Gate por clase epistemológica

### C_DOCTRINE

Para usar `C_DOCTRINE`:

- debe existir al menos una fuente P1 relevante;
- la afirmación debe encontrarse dentro de `supports`;
- no puede contradecir `does_not_support`;
- se registra obra y pasaje cuando sea posible.

### D_CONTEMPORARY_USAGE

Puede apoyarse en:

- estudios académicos de comunidades o experiencias;
- fuentes emic;
- autores contemporáneos identificados.

No se transforma en ontología.

### E_PROJECT_HYPOTHESIS

Puede utilizar doctrina, datos y técnica, pero:

- debe declararse explícitamente como construcción ALMAS;
- debe indicar qué parte procede de cada fuente;
- debe registrar alternativas;
- no puede citar una fuente como si ésta enseñara la operacionalización astrológica.

## 4. Gate astrológico

Las fuentes doctrinales no añaden puntos.

La astrología debe satisfacer sus propios requisitos:

`DATO → TÉCNICA → RAÍZ → RECURRENCIA → ROBUSTEZ → ESTADO`

Sólo después se interpreta la raíz usando el corpus doctrinal.

## 5. Gate ontológico

Una categoría de origen o contrato necesita dos componentes independientes:

### Base doctrinal
Debe existir una definición reproducible del modelo.

### Base astrológica
Debe existir una firma operacionalizada y evaluable.

Si existe doctrina pero no discriminador astrológico:

`DOCTRINA_DEFINIDA + FIRMA_NO_DISCRIMINANTE → INSUFFICIENT`.

Si existe una firma astrológica pero no base doctrinal clara:

`FIRMA_ESTRUCTURAL + MODELO_DOCTRINAL_AMBIGUO → E_PROJECT_HYPOTHESIS`.

## 6. Ejemplos

### Twin flame
Summit Lighthouse puede aportar `DIRECT_DOCTRINE` para su propio modelo de origen.

Corelli 1886 aporta `HISTORICAL_ANTECEDENT` o genealogía terminológica, no la misma doctrina.

### Zivug
Sha'ar HaGilgulim puede aportar `DIRECT_DOCTRINE` dentro de la Cábala luriana.

Compararlo con soulmate/twin flame es `COMPARATIVE_ANALOGUE`.

### Dracónica
Crane aporta un método identificado.

Usar natal↔dracónica para detectar continuidad preencarnatoria es `PROJECT_OPERATIONALIZATION`.

### Soul contract
Kwilecki aporta `ACADEMIC_DESCRIPTION` del uso New Age.

La gramática contractual ALMAS es `PROJECT_SYNTHESIS`.

## 7. Objeto canónico

Cada afirmación importante debe poder representarse como:

```text
claim_id
statement
epistemic_class
concept_id
source_relation
source_ids
astrological_refs
status
alternatives
limitations
```

## 8. Regla de no acumulación

Diez fuentes que repitan una doctrina no equivalen a diez evidencias astrológicas.

`N_FUENTES ≠ FUERZA_ASTROLOGICA`

La redundancia documental puede aumentar confianza en la **atribución doctrinal**, no en la presencia del fenómeno en un caso.


## 9. Claim contract v2

Toda afirmación doctrinal, técnica o metafísica importante debe poder serializarse mediante `schemas/doctrinal-claim.schema.json` versión 2.0.0.

Campos adicionales obligatorios:

- `claim_scope`;
- `source_anchor_refs`;
- `requested_conclusion`;
- `allowed_conclusion`;
- `inferential_ceiling`;
- `discriminator_id`;
- `discriminator_state`;
- `ceiling_enforced=true`.

### Regla de redacción

La frase publicada debe corresponder a `allowed_conclusion`, no a `requested_conclusion`, cuando ésta exceda el techo.

Ejemplo:

`requested_conclusion = R3_BILATERAL_AGREEMENT_MODEL`

pero

`allowed_conclusion = R2_RELATIONAL_PREINCARNATIONAL_FUNCTION`

si el discriminador R2→R3 sigue `NOT_VALIDATED`.

### Regla de fuente

Cada `source_anchor_ref` debe existir en `source-registry.json` y tener:

- `verification_anchor`;
- `verification_anchor_type`;
- `evidence_scope`.

### Regla de técnica

Un claim `B_TECHNIQUE` puede ser `SUPPORTED` respecto de un procedimiento de cálculo aunque la interpretación metafísica asociada permanezca `INSUFFICIENT`.

La técnica y la ontología son variables independientes.
