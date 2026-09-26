# Fases 13–15 · Protocolo de validación externa y preregistro

## 1. Finalidad

La validación externa de ALMAS no pretende convertir una ontología metafísica en una verdad experimental mediante un conjunto de etiquetas humanas.

Valida propiedades metodológicas observables:

- reproducibilidad;
- estabilidad;
- especificidad;
- resistencia a ablación;
- separación entre modelos;
- tasa de sobreclasificación;
- independencia respecto de autoetiquetas;
- trazabilidad doctrinal;
- capacidad de conservar `INSUFFICIENT` cuando no existe discriminador;
- generalización fuera de los casos usados para construir reglas.

## 2. Principio de separación desarrollo/validación

Todo caso usado para:

- descubrir una regla;
- definir una cláusula;
- elegir un umbral;
- modificar un peso;
- crear un discriminador;
- introducir una nueva técnica;

queda marcado `DEVELOPMENT_ONLY` para esa versión metodológica.

Un caso `DEVELOPMENT_ONLY` no puede convertirse posteriormente en evidencia de validación externa de la misma regla.

Los casos privados de desarrollo no se publican ni se identifican en el repositorio.

## 3. Estados de validación

- `DEVELOPMENT_ONLY`: intervino en descubrimiento o ajuste.
- `INTERNAL_REPLICATION`: caso nuevo ejecutado con reglas congeladas, pero dentro del mismo entorno investigador.
- `EXTERNAL_HOLDOUT`: caso seleccionado antes de ejecutar resultados y no usado en desarrollo.
- `FROZEN_CONFIRMATORY`: ejecución sobre holdout con versión, entradas, endpoints y criterios preregistrados.
- `RETIRED`: caso retirado por contaminación, calidad insuficiente o pérdida de independencia.
- `NOT_EVALUABLE`: datos insuficientes.

## 4. Congelación previa

Antes de abrir un holdout confirmatorio congelar:

1. versión ALMAS;
2. commit SHA;
3. schemas;
4. pesos y orbes;
5. lista de técnicas;
6. políticas de dependencia;
7. discriminadores;
8. reglas de estados;
9. endpoints;
10. criterios de éxito/fallo;
11. variables documentales permitidas;
12. lista de casos y criterio de inclusión.

No modificar estos elementos después de observar los resultados del holdout.

## 5. Cohortes mínimas

La validación debe incluir, cuando existan datos públicos y verificables suficientes:

### C1 · Relaciones estables de larga duración
Comprueba si ALMAS evita convertir estabilidad en ontología espiritual superior.

### C2 · Relaciones separadas o cerradas
Comprueba si la metodología puede reconocer función/transformación sin convertir la ruptura en contraevidencia ontológica automática.

### C3 · Vínculos no románticos profundos
Amistad, parentesco, maestro/alumno u otros vínculos públicos adecuados.

Objetivo: impedir que raíces de profundidad, karma o misión sean tratadas como exclusivamente románticas.

### C4 · Controles relacionales ordinarios
Pares con datos adecuados pero sin una historia pública excepcionalmente intensa.

Objetivo: medir sobreclasificación y especificidad.

### C5 · Casos emic soulmate/twin-flame
Sólo si datos y narrativa ya son públicos y verificables.

La autoetiqueta se registra como `D_CONTEMPORARY_USAGE`; nunca constituye verdad de referencia ontológica.

### C6 · Controles sintéticos
Pares artificiales, barajados o generados bajo modelos nulos.

Objetivo: probar el pipeline, falsos positivos y sensibilidad.

## 6. Blindaje narrativo

Siempre que sea posible, ejecutar dos pasos:

### Paso A · Ejecución estructural ciega
El motor recibe datos natales/eventuales permitidos, pero no la narrativa relacional ni la autoetiqueta.

Produce y congela:

- raíces;
- IEM;
- ontología;
- contrato;
- ablation;
- robustez;
- incertidumbre.

### Paso B · Apertura documental
Sólo después se incorporan hechos públicos preregistrados para evaluar:

- concordancia funcional;
- temporalidad retrospectiva;
- viabilidad;
- reciprocidad;
- cumplimiento;
- contraevidencia.

La narrativa nunca puede modificar retrospectivamente los cálculos del Paso A.

## 7. Endpoints primarios

### EV1 · Reproducibilidad
Misma entrada + misma versión → misma salida canónica dentro de tolerancias declaradas.

### EV2 · Tasa de sobreclasificación ontológica
Frecuencia con que el sistema asigna `SUPPORTED` a categorías fuertes cuando los discriminadores no están validados.

Objetivo normativo: categorías con discriminadores `NOT_VALIDATED` no pueden alcanzar `SUPPORTED`.

### EV3 · Preservación de ambigüedad
Proporción de casos en que el sistema conserva `INSUFFICIENT` cuando dos modelos permanecen observacionalmente equivalentes.

### EV4 · Supervivencia de núcleo
Qué conclusiones sobreviven AB0–AB8 y perturbación horaria.

### EV5 · Especificidad contractual
Diferencia entre:
- tarea individual;
- karma/continuidad;
- catálisis;
- contrato funcional;
- acuerdo bilateral literal.

El motor no debe elevar niveles R3/R4 por intensidad o recurrencia genérica.

### EV6 · Independencia de autoetiqueta
La clasificación estructural no cambia al revelar después una etiqueta emic.

### EV7 · Exactitud de atribución doctrinal
Toda afirmación C o D debe pasar el Gate doctrinal y apuntar a fuentes compatibles.

### EV8 · Estabilidad de temporalidad
Fechas y eventos no deben crear cláusulas ausentes en el análisis estructural congelado.

## 8. Endpoints secundarios

- distribución de IEM por cohorte;
- distribución de IAP/ITP/IAA/IRCo/ICCo/IVC/IRCT;
- IDD entre modelos;
- porcentaje de raíces dependientes eliminadas;
- porcentaje de cláusulas degradadas por ablación;
- sensibilidad a hora natal;
- frecuencia de `NOT_EVALUABLE`;
- cobertura documental;
- tasa de correcciones tras auditoría.

No interpretar estos endpoints como probabilidades metafísicas.

## 9. Métricas de error metodológico

Registrar:

- `FALSE_SPECIFICITY`: se afirmó una categoría más específica de lo permitido.
- `DEPENDENCY_INFLATION`: evidencia dependiente se contó como independiente.
- `NARRATIVE_LEAKAGE`: información biográfica influyó en el análisis estructural.
- `DOCTRINAL_OVERREACH`: una fuente fue usada más allá de lo que sostiene.
- `TEMPORAL_CREATION`: una técnica temporal creó una cláusula estructural.
- `LABEL_LEAKAGE`: la autoetiqueta afectó la clasificación.
- `CASE_FITTING`: una regla cambió después de observar el holdout.
- `PRIVACY_BREACH`: material no público fue incorporado al corpus público.

Cualquier `CASE_FITTING` invalida el estatus confirmatorio de la ejecución afectada.

## 10. Criterios para promover una regla

Una regla puede pasar de `EXPERIMENTAL` a `CONFIRMATORY_ELIGIBLE` sólo si:

1. está preregistrada;
2. tiene definición reproducible;
3. tiene test sintético;
4. no fue ajustada al holdout;
5. sobrevive al menos una replicación independiente;
6. no depende exclusivamente de capas support-only;
7. tiene contraevidencia definida;
8. su discriminador está explícitamente evaluado;
9. mantiene resultados aceptables en controles negativos;
10. su atribución doctrinal supera el Gate doctrinal.

`CONFIRMATORY_ELIGIBLE` no significa ontología demostrada.


### Registro canónico de promoción

Una promoción metodológica sólo adquiere autoridad ejecutable cuando queda incorporada al registro canónico:

`src/almas_tfa/data/discriminator-promotion-registry.json`.

La entrada debe fijar el alcance por pares, `promotion_ref`, fecha de promoción, versión y commit congelados, referencias de preregistro, replicación independiente, holdout externo, controles negativos y auditorías de leakage.

Una ejecución de análisis no puede modificar ni sustituir ese registro.

### Gate hacia M25

`CONFIRMATORY_ELIGIBLE` no basta para entrar en IRC como `VALIDATED_DISCRIMINATOR`.

Para que una señal ontológica pueda declararse `L3_VALIDATED` y ser consumida por M25 debe existir, además de los criterios anteriores:

1. regla congelada;
2. ejecución confirmatoria fuera del conjunto de desarrollo;
3. replicación independiente suficiente para el alcance declarado;
4. controles negativos sin falsa especificidad inaceptable;
5. ausencia de `LABEL_LEAKAGE`, `NARRATIVE_LEAKAGE` y `CASE_FITTING`;
6. alcance de validación explícito por pares de modelos;
7. `root_key` estable y trazable;
8. promoción documental previa al análisis del caso donde vaya a usarse.

M25 no realiza esta promoción. Sólo verifica que la salida canónica M21 ya presenta una raíz como L3 confirmatoria y que el componente de robustez la referencia de forma explícita.

Mientras ningún discriminador haya completado esta promoción, la infraestructura puede existir sin que haya ningún `VALIDATED_DISCRIMINATOR` real utilizable.

### Independencia astrológica del discriminador

Si un discriminador declara `uses_astrology=true`, los requisitos L3 generales no bastan. La promoción exige además un bloque `astrology_validation` con:

- criterio externo no astrológico;
- ablación de familias/features astrológicas;
- controles emparejados procesados con el mismo pipeline;
- auditoría de dependencia y pseudo-replicación;
- validación fuera de muestra;
- replicación astrológica específica.

La promoción debe declarar asimismo:

- `single_feature_prohibition_acknowledged=true`;
- `null_rarity_not_ontological=true`;
- `temporal_activation_not_origin_proof=true`.

Un aspecto, asteroide, atacir, recurrencia o sincronía aislada no puede crear una categoría ontológica. La rareza bajo un modelo nulo no se interpreta como probabilidad metafísica. Una técnica temporal puede activar arquitectura previamente congelada, pero no demostrar su origen.

Validar una regla astrológica sólo valida su capacidad discriminante dentro del observable operacional y el alcance registrados. No demuestra por sí misma una ontología metafísica.


## 11. Verdad de referencia documental

ALMAS no utilizará como verdad de referencia:

- “esta pareja afirma ser twin flame”;
- “un astrólogo dice que son almas gemelas”;
- duración de la relación;
- matrimonio;
- intensidad;
- sufrimiento;
- sincronías;
- éxito o ruptura.

Las verdades de referencia permitidas son sólo variables observables/documentales, por ejemplo:

- fechas;
- duración;
- convivencia;
- matrimonio/divorcio;
- contacto/no contacto documentado;
- relación profesional/familiar;
- declaraciones públicas;
- cronología de acontecimientos.

Las categorías metafísicas permanecen hipótesis/modelos.

## 12. Publicación

Un caso real sólo puede entrar en el corpus público si:

- sus datos relevantes ya son públicos;
- la procedencia es verificable;
- cumple la política de publicación;
- no fue obtenido desde material privado;
- el caso no revela indirectamente un caso privado por perturbación o disfraz.

## 13. Resultado de fase

La Fase 13 se considera implementada cuando existen:

- protocolo;
- schema de caso;
- schema de ejecución;
- manifiesto de cohorte;
- registro de endpoints;
- fixture sintético;
- invariantes CI;
- reglas de promoción;
- al menos una ejecución sintética;
- y la infraestructura está lista para recibir holdouts reales sin modificar la metodología.


## 14. Validez discriminante cuantitativa

Toda promoción a `VALIDATED_DISCRIMINATOR` debe satisfacer la política canónica `ALMAS_DISCRIMINANT_VALIDATION_V1`.

Para cada par validado se calculan sensibilidad, especificidad y balanced accuracy a partir de TP/TN/FP/FN. ALMAS usa intervalos Wilson al 95 % y exige:

- CI95 inferior de sensibilidad ≥ 0.60;
- CI95 inferior de especificidad ≥ 0.90;
- balanced accuracy ≥ 0.75.

La métrica crítica de sobreclasificación es:

`FALSE_SPECIFICITY_RATE = errores de falsa especificidad / casos evaluables`.

No basta la tasa puntual. El CI95 superior debe ser ≤ 0.05.

En controles sintéticos/adversariales la falsa especificidad permitida es exactamente 0.

Estos valores son `E_PROJECT_POLICY`, no constantes universales. Sólo pueden modificarse mediante una nueva política versionada antes de evaluar nuevos holdouts.

Cuando la salida es categórica, calibración probabilística es `NOT_APPLICABLE_CATEGORICAL`. Si un discriminador emite probabilidades, debe superar un criterio de calibración preregistrado y aportar referencias independientes.

La validación cuantitativa demuestra rendimiento del clasificador operacional dentro de su alcance, no verdad metafísica.


## 15. Cegamiento, leakage y revelado tardío

Toda promoción a `VALIDATED_DISCRIMINATOR` debe satisfacer además la política `ALMAS_BLINDING_LEAKAGE_V1`.

La evaluación se separa en dos fases. `STEP_A_BLINDED` ejecuta y congela la arquitectura estructural sin autoetiquetas, narrativa relacional, clasificación esperada, resultado esperado ni truth/outcome del holdout. `STEP_B_DOCUMENTARY_REVEAL` abre después la documentación preregistrada para temporalidad, viabilidad, reciprocidad, cumplimiento y contraevidencia.

La entrada estructural de M21 aplica un firewall fail-closed. Si aparecen claves reservadas a etiqueta, narrativa, expectativa o outcome, la ejecución falla; no las elimina silenciosamente.

Toda auditoría L3 debe incluir `blinding_audit` con `policy_id=ALMAS_BLINDING_LEAKAGE_V1`, referencias de auditoría, fingerprints SHA-256 y evidencia de separación desarrollo/evaluación.

Los siguientes conteos deben ser exactamente cero:

- `forbidden_field_hits`;
- `label_leakage_count`;
- `narrative_leakage_count`;
- `case_fitting_count`;
- `post_holdout_rule_change_count`.

La salida estructural debe ser invariante tras el revelado documental:

`pre_reveal_output_sha256 == post_reveal_structural_output_sha256`.

Si la identidad de un caso público no puede ocultarse, se registra como `UNAVOIDABLE_PUBLIC` y se documenta el riesgo mediante `identity_risk_refs`. Esa limitación no autoriza revelar autoetiquetas, narrativas o resultados esperados durante la fase estructural.

Superar este gate demuestra resistencia operacional al leakage dentro del protocolo evaluado. No demuestra una ontología metafísica.
