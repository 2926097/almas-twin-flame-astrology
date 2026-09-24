---
name: almas-soul-contract
description: Metaphysical research skill for reconstructing possible preincarnational soul agreements from ALMAS astrological architecture, doctrine, chronology, counterevidence and documented facts.
version: 1.0.0
author: Proyecto ALMAS
metadata:
  public_release: true
  paradigm: metaphysical_research
  depends_on:
    - almas-metaphysical-relationship-astrology
  tags: [soul-contract, preincarnation, metaphysics, astrology, hermeneutics, karma, dharma, relationships]
---

# ALMAS Soul Contract · Contrato Álmico v1.0.0

## 0. Paradigma

Esta skill trabaja explícitamente dentro del marco metafísico ALMAS.

La astrología se utiliza como **método metafísico de averiguación**. El motor contractual no parte de una objeción externa a la metafísica, sino de una pregunta interna: dado un conjunto de evidencias astrológicas, doctrinales, temporales y documentales, ¿qué arquitectura preencarnatoria explica mejor el vínculo?

Los controles metodológicos sirven para evitar sobreconteo, dependencia, ajuste retrospectivo al caso y saltos ontológicos apoyados en evidencia aislada. No constituyen una negación del paradigma metafísico.

## 1. Función de la skill

Reconstruir, cuando la evidencia lo permita, un posible **contrato, pacto o acuerdo preencarnatorio** entre dos almas.

La salida no es una quinta categoría junto a AF, KA, AG o LG. El contrato es una arquitectura transversal que puede coexistir con distintos modelos relacionales.

Preguntas nucleares:

- ¿qué finalidad metafísica parece organizar el encuentro?;
- ¿qué activa A en B?;
- ¿qué activa B en A?;
- ¿qué surge únicamente en el campo común?;
- ¿qué aprendizaje, reparación, confrontación, integración o servicio articula el vínculo?;
- ¿qué elementos son compatibles con continuidad kármica, dhármica o de vidas anteriores?;
- ¿qué condiciones indicarían desarrollo, integración, transformación o cierre de una cláusula?;
- ¿qué alternativas explicativas compiten con la lectura contractual?

## 2. Entrada principal

La entrada preferente es `astrology_to_soul_contract.json`, generado por la skill de Astrología Metafísica Relacional y conforme a:

`schemas/astrology-to-soul-contract.schema.json`

El motor contractual debe consumir, no recalcular silenciosamente:

- raíces estructurales independientes;
- dirección A→B, B→A o campo común;
- familias técnicas;
- fuerza y recurrencia;
- pilares asociados;
- ontología relacional;
- temporalidad anclada;
- robustez;
- cobertura;
- contraevidencia;
- referencias canónicas a la evidencia astrológica.

Puede añadir además:

- doctrina primaria o histórica;
- estudios académicos;
- uso contemporáneo documentado;
- cronología de hechos;
- eventos públicos o privados autorizados;
- otras técnicas metafísicas incorporadas mediante módulos definidos y trazables.

## 3. Separación epistemológica

Mantener siempre:

- `A_CALCULATED`: dato calculado o documental.
- `B_TECHNIQUE`: técnica empleada.
- `C_DOCTRINE`: doctrina explícita de una fuente.
- `D_CONTEMPORARY_USAGE`: uso contemporáneo.
- `E_PROJECT_HYPOTHESIS`: inferencia ALMAS.

Una hipótesis contractual específica puede ser plenamente metafísica y, a la vez, seguir marcada como `E_PROJECT_HYPOTHESIS`. Esa etiqueta identifica procedencia, no debilita el paradigma.

## 4. Estados

Usar:

- `SUPPORTED`
- `COMPATIBLE`
- `INSUFFICIENT`
- `CONTRADICTED`
- `NOT_EVALUABLE`

Los estados no son probabilidades metafísicas.

## 5. Direccionalidad

Separar obligatoriamente:

- `A_EN_B`: función de A sobre la arquitectura de B;
- `B_EN_A`: función de B sobre la arquitectura de A;
- `CAMPO_COMUN`: función emergente de la relación como unidad.

Reciprocidad:

- `BILATERAL`
- `PARCIAL`
- `ASIMETRICA`
- `NO_EVALUABLE`

Bilateral no significa simétrico.

## 6. Ocho cláusulas base

La taxonomía inicial utiliza ocho familias funcionales:

1. **Encuentro y reconocimiento**.
2. **Vínculo amoroso**.
3. **Herida y reparación**.
4. **Libertad y autonomía**.
5. **Comunicación y verdad**.
6. **Transformación y poder**.
7. **Integración y encarnación**.
8. **Liberación y cierre**.

Cada cláusula debe registrar:

- raíces estructurales;
- dirección;
- técnicas;
- dependencia;
- significado metafísico;
- acción simbólica;
- aprendizaje;
- sombra;
- requisito de integración;
- firma de cumplimiento;
- temporalidad;
- contraevidencia;
- alternativas;
- robustez.

Una cláusula nueva sólo puede añadirse después de definir procedencia, discriminadores, evidencia necesaria, contraevidencia y tests.

## 7. Roles preencarnatorios

Los roles son funcionales por cláusula, no identidades esenciales.

Roles iniciales:

- ACTIVADOR
- CATALIZADOR
- ESPEJO
- MEMORIA
- ESTRUCTURADOR
- LIBERADOR
- CONFRONTADOR
- PORTADOR_DE_VULNERABILIDAD
- INTEGRADOR
- MEDIADOR
- TESTIGO
- COMPANERO_DE_APRENDIZAJE

Cadena mínima:

`ARQUITECTURA_RECEPTORA → FACTOR_DEL_OTRO → RAIZ_ACTIVADA → FUNCION_METAFISICA → CLAUSULA`

Intensidad:

- `PRIMARIO`
- `SECUNDARIO`
- `CORROBORATIVO`
- `INSUFICIENTE`
- `NO_EVALUABLE`

## 8. Preexistencia y origen

El contrato puede investigar, sin forzar equivalencias doctrinales:

- origen independiente;
- familia o grupo de almas;
- origen compartido;
- continuidad kármica;
- continuidad dhármica;
- vínculo de vidas anteriores;
- modelos monádicos;
- split-soul;
- twin-soul / twin-flame / twin-ray;
- maestro/alumno;
- sacred partner / hieros gamos;
- misión o servicio compartido.

Cuando dos modelos produzcan la misma firma observable y no exista discriminador validado, usar una categoría no resuelta o `INSUFFICIENT`.

## 9. Historia preencarnatoria hipotética

La reconstrucción puede organizarse en:

`ORIGEN → ACUERDO → DESCENSO/ENCARNACION → ENCUENTRO → ACTIVACION → DESARROLLO → INTEGRACION/TRANSFORMACION/CIERRE`

No todas las fases deben estar presentes ni en ese orden.

Cada tramo debe enlazar con evidencia y fuente doctrinal cuando exista.

## 10. Temporalidad contractual

Distinguir:

### Tiempo 1 · Activación inicial
Qué raíces preexistentes pone en movimiento el encuentro.

### Tiempo 2 · Desarrollo
Qué cláusulas reaparecen mediante activaciones o hechos independientes.

### Tiempo 3 · Integración, transformación o cierre
Qué indicios muestran que la función cambia de modalidad, se integra o deja de organizar el vínculo.

Estados temporales:

- `LATENTE`
- `ACTIVADA`
- `EN_DESARROLLO`
- `INTEGRADA`
- `TRANSFORMADA`
- `CERRADA`
- `NO_EVALUABLE`

La temporalidad debe permanecer anclada a raíces estructurales.

## 11. Gramática contractual

Formato recomendado:

`ACTOR_O_CAMPO → FUNCION → OBJETIVO_ALMICO → SOMBRA → REQUISITO_DE_INTEGRACION → FIRMA_DE_CUMPLIMIENTO`

Ejemplo sintético:

`A_EN_B → activar autonomía → hacer visible la tensión vínculo/libertad → huida o control → sostener cercanía sin apropiación → la relación deja de necesitar crisis para preservar individualidad`.

## 12. Doctrina comparada

Investigar sin equiparar automáticamente:

- Platonismo/Neoplatonismo;
- Cábala;
- misticismo cristiano;
- sufismo;
- hinduismo, Vedanta y Tantra;
- budismo cuando proceda;
- espiritismo;
- Teosofía;
- Alice Bailey;
- I AM Activity;
- Summit Lighthouse;
- New Age;
- estudios académicos del esoterismo.

Para cada fuente indicar qué sostiene, qué no sostiene y cómo se relaciona con la hipótesis ALMAS.

## 13. Controles metodológicos internos

1. Una evidencia aislada no crea una cláusula ontológica.
2. Técnicas dependientes no cuentan como confirmaciones independientes.
3. La temporalidad activa arquitectura; no sustituye estructura.
4. La rareza estadística no se convierte en probabilidad metafísica.
5. No ajustar pesos, cláusulas o umbrales para obtener el resultado deseado en un caso.
6. Buscar contraevidencia activamente.
7. Diferenciar ausencia evaluada de `NOT_EVALUABLE`.
8. Una función metafísica no implica obligación conductual de otra persona.
9. Viabilidad y reciprocidad observables se registran como hechos del plano encarnado y no se sustituyen por inferencia simbólica.

## 14. Salida canónica

La salida recomendada es:

`canonical_soul_contract.json`

conforme a `schemas/contrato-almico.schema.json`.

El relato final se genera después de cerrar:

`evidencia → raíces → cláusulas → roles → temporalidad → doctrina → contraevidencia → síntesis`

Nunca al revés.

## 15. Publicación

GitHub publica reglas generalizadas, fuentes públicas, tests sintéticos y casos reales únicamente cuando los datos subyacentes ya son públicos y verificables.

El material privado no se convierte en público por haber sido usado en investigación interna.
