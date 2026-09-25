# Módulo ALMAS · Contrato Preencarnatorio · historial técnico

> Las entradas 1.0.0–1.9.0 que siguen representan **revisiones históricas internas del motor contractual**. Desde ALMAS 1.4.0 el módulo no tiene SemVer público independiente y hereda `VERSION` de la raíz. Las releases públicas posteriores se documentan principalmente en el changelog raíz.

## ALMAS 1.10.2 — 2026-09-25

- Normalización de la prosa pública al español.
- Sin cambios en fórmulas contractuales, cláusulas, gates ni `engine_revision`.
- El módulo continúa heredando la versión pública de la raíz.

## ALMAS 1.10.1 — 2026-09-25

- Mantenimiento de repositorio y CI; sin cambios en fórmulas contractuales, cláusulas, gates o `engine_revision`.
- El módulo continúa heredando la versión pública de la raíz.

> Las entradas 1.0.0–1.9.0 que siguen representan **revisiones históricas internas del motor contractual**. Desde ALMAS 1.4.0 el módulo no tiene SemVer público independiente y hereda `VERSION` de la raíz.

## ALMAS 1.4.0 — 2026-09-24

- Migra el antiguo Soul Contract a módulo interno de la única skill ALMAS.
- Conserva la revisión técnica 1.9.0 como `engine_revision`.
- Elimina el versionado público independiente.
- Mantiene intactos los motores diferenciales de las ocho etapas preencarnatorias.

## engine_revision 1.9.0 — 2026-09-24

- Añade motor diferencial de mecanismos de cumplimiento.
- Separa activación, repetición, integración, transformación y cierre.
- Exige hechos documentados para INTEGRADA, TRANSFORMADA y CERRADA.
- Añade mecanismos FM_ACTIVACION, FM_REPETICION, FM_RECIPROCIDAD, FM_CATALISIS, FM_ENCARNACION, FM_TIKKUN_REPARACION, FM_SERVICIO, FM_LIBERACION, FM_TRANSFORMACION_MODALIDAD, FM_CIERRE, FM_RUTA_ALTERNATIVA y FM_APLAZAMIENTO.
- Añade discriminadores FMD1–FMD8.
- Completa la arquitectura diferencial de las ocho etapas preencarnatorias.

## engine_revision 1.8.0 — 2026-09-24

- Añade motor de ensamblaje diferencial de cláusulas.
- Formaliza las ocho cláusulas como objetos derivados con genealogía vertical.
- Añade control de solapamiento entre cláusulas.
- Separa estado epistemológico, centralidad y estado temporal.
- Exige firma de cumplimiento preregistrada.
- Añade discriminadores CLD1–CLD8.


## engine_revision 1.7.0 — 2026-09-24

- Añade motor diferencial de tarea común.
- Exige prueba de emergencia frente a la suma de tareas individuales.
- Formaliza diez tareas comunes canónicas.
- Añade familias CTF1–CTF8 y discriminadores CTD1–CTD8.
- Controla dependencia de compuesta/Davison como una sola familia RELCHART.
- Integra common_task_differential en la reconstrucción preencarnatoria.


## engine_revision 1.6.0 — 2026-09-24

- Añade motor diferencial de tareas individuales.
- Exige identificar TAREA_A_PREVIA y TAREA_B_PREVIA antes de usar sinastría.
- Añade diecisiete tareas canónicas y ocho familias ITF1–ITF8.
- Introduce partner_removed_result como control explícito contra circularidad.
- Añade discriminadores ITD1–ITD8.
- Integra individual_tasks_differential en la reconstrucción preencarnatoria.


## engine_revision 1.5.0 — 2026-09-24

- Añade motor diferencial de condiciones de encuentro.
- Separa ventana temporal, contexto, reconocimiento, bloqueo y rutas alternativas.
- Añade ocho familias ECF1–ECF8 y discriminadores ECD1–ECD8.
- Exige anclaje estructural previo para toda condición temporal.
- Impide convertir coincidencia temporal/geográfica en prueba contractual.
- Integra encounter_conditions_differential en la reconstrucción preencarnatoria.


## engine_revision 1.4.0 — 2026-09-24

- Añade motor diferencial de selección de roles.
- Separa rol funcional, dirección, intensidad y mecanismo preencarnatorio.
- Formaliza doce roles canónicos.
- Añade ocho familias de evidencia RF1–RF8.
- Añade discriminadores RSD1–RSD8.
- Permite roles estables, alternantes o dependientes de fase.
- Impide inferir acuerdo mutuo, necesidad kármica o rol único sólo desde bilateralidad o intensidad.
- Integra role_selection_differential en la reconstrucción preencarnatoria.


## engine_revision 1.3.0 — 2026-09-24

- Añade motor diferencial del motivo del acuerdo.
- Separa motivo funcional, dirección/alcance y mecanismo preencarnatorio.
- Define catorce motivos funcionales canónicos.
- Añade ocho familias de evidencia para motivo.
- Añade discriminadores AM1–AM8.
- Distingue motivo PRIMARY, SECONDARY y CORROBORATIVE.
- Impide inferir elección mutua o asignación preencarnatoria sólo desde astrología.
- Integra Kardec, Sha'ar HaGilgulim, Myss, Newton y Schwartz como fuentes distintas, no equivalentes.
- Integra agreement_motive_differential en la reconstrucción preencarnatoria.


## engine_revision 1.2.0 — 2026-09-24

- Añade motor diferencial del origen de las almas.
- Define nueve modelos operativos de origen y una categoría explícita de origen compartido no diferenciado.
- Separa firma doctrinal de evidencia astrológica.
- Añade seis dimensiones astrológicas operativas: origen, especificidad diádica, continuidad, polaridad, tarea compartida y singularidad.
- Añade registro de discriminadores doctrinales y astrológicos.
- Impide que un subtipo de origen alcance SUPPORTED mientras sus discriminadores astrológicos sigan NOT_VALIDATED.
- Integra el motor de origen en la reconstrucción preencarnatoria v1.1.0.


## engine_revision 1.1.0 — 2026-09-24

- Añade la reconstrucción preencarnatoria en ocho etapas.
- Formaliza origen, motivo del acuerdo, selección de roles, condiciones de encuentro, tareas individuales, tarea común, cláusulas y mecanismos de cumplimiento.
- Añade grafo causal y regla de coherencia vertical.
- Añade esquema JSON `preincarnation-reconstruction.schema.json`.
- Añade mapa de fuentes por etapa.
- Integra fuentes lurianas, espiritistas y métodos modernos de planificación preencarnatoria sin tratarlos como doctrinas equivalentes.
- Introduce mecanismos de cumplimiento, transformación, cierre, ruta alternativa y aplazamiento.
- Mantiene la astrología como método metafísico de averiguación y los controles como rigor interno.

## engine_revision 1.0.0 — 2026-09-24

- Primera revisión histórica del motor contractual; su estatus independiente queda retirado desde ALMAS 1.4.0.
- Ocho cláusulas base.
- Roles preencarnatorios.
- Causa contractual.
- Temporalidad de cláusulas.
- Interoperabilidad con ALMAS Astrología Metafísica Relacional.
