# Fase 13 · Protocolo de validación externa y preregistro

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

La autoetiqueta se registra como `D_CONTEMPORARY_USAGE`; nunca es ground truth ontológico.

### C6 · Controles sintéticos
Pares artificiales, barajados o generados bajo modelos nulos.

Objetivo: probar el pipeline, falsos positivos y sensibilidad.

## 6. Blindaje narrativo

Siempre que sea posible, ejecutar dos pasos:

### Paso A · Blind structural run
El motor recibe datos natales/eventuales permitidos, pero no la narrativa relacional ni la autoetiqueta.

Produce y congela:

- raíces;
- IEM;
- ontología;
- contrato;
- ablation;
- robustez;
- incertidumbre.

### Paso B · Documentary opening
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

## 11. Ground truth

ALMAS no utilizará como ground truth:

- “esta pareja afirma ser twin flame”;
- “un astrólogo dice que son almas gemelas”;
- duración de la relación;
- matrimonio;
- intensidad;
- sufrimiento;
- sincronías;
- éxito o ruptura.

Los ground truths permitidos son sólo variables observables/documentales, por ejemplo:

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
