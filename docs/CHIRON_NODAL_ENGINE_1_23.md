# ALMAS 1.23.0 · Chiron–Nodal Integration Engine

## Propósito

La versión 1.23 añade una capacidad personal para describir arquitectura Venus–eje nodal–Quirón, activación temporal, secuencias y resultados biográficos M27. Se implementa como extensión optativa del canonical personal. El canonical 1.22.0 que no contiene `personal_temporal_complexes` sigue siendo válido.

La capa no altera IEM, IDD, IRC, ICC, ICE, PX, PS, M18 `WOUND_REPAIR`, discriminadores, contratos relacionales ni IAT. Sus salidas preservan `structural_scoring_modified=false` y `ontological_category_created=false`.

## Nodos duales

La posición natal y de tránsito conserva `NORTH_NODE`/`SOUTH_NODE` de True Node y añade `MEAN_NORTH_NODE`/`MEAN_SOUTH_NODE`. Mean Node se calcula mediante `MEEUS_MEAN_ASCENDING_NODE_1998_47_7`, evaluado con JD TT; el Nodo Sur es el antipodal del Norte. La procedencia declara simultáneamente `node_variants=[TRUE,MEAN]`, y cada entrada conserva el método, variante y eje `LUNAR_NODE_AXIS`.

`build_dual_node_layer()` conserva ambas longitudes en un solo eje. `classify_nodal_variant_concordance()` solo evalúa convergencia o dominancia cuando el llamante declara objetivo, aspecto y orbe. Sin esos datos devuelve `NOT_EVALUABLE`. La interpretación Mean=estructura / True=modulación queda expresamente como hipótesis E sin validar.

## Complejo personal y solicitud

Se activa al incluir `chiron_process` en `personal_report_request`, con `aspect_policy` y `aspect_policy_ref`. El pipeline calcula contactos Venus–Quirón, Venus–True/Mean Node y Quirón–True/Mean Node bajo los orbes declarados, conserva ausencias relevantes como contraevidencia y deduplica True/Mean a nivel de topología del eje.

Ejemplo mínimo:

```json
{
  "schema_version": "1.0.0",
  "subject": {"id": "SYNTHETIC", "birth_date": "2000-01-01", "birth_time": "12:00", "timezone": "Etc/UTC", "latitude": 0, "longitude": 0, "time_reliability": "A"},
  "report_profile": "FULL_CRITICAL_REPORT",
  "chiron_process": {
    "aspect_policy": {"CONJUNCTION": {"angle": 0, "orb": 1}},
    "aspect_policy_ref": "ASPECT_POLICY_V1"
  }
}
```

La solicitud personal es optativa. Si se activa, el canonical emite `personal_temporal_complexes[]` y el modelo documental incorpora **Complejos de vulnerabilidad, recapitulación e integración**. `P12_CHIRON_PROCESS` aparece solo cuando hay una evaluación presente, para preservar los perfiles y canonical legacy.

## Solver temporal y dependencia

`solve_aspect_perfections()` busca raíces con bisección, descarta el corte de rama angular como falso positivo y localiza mínimos estacionarios para no perder contactos tangenciales en la ventana. Devuelve todas las perfecciones detectables, número de pasada, fecha exacta, error residual, técnica, variante, grupo, paso de muestreo y tolerancias. El llamante proporciona un evaluador por técnica: progresiones directas/conversas, terciarias, arco solar y atacires no comparten una transformación temporal implícita.

Una ventana de búsqueda con paso demasiado grueso puede perder una raíz; paso y tolerancias forman parte del resultado auditable. Estaciones y estados de movimiento se completan solo cuando un `context_evaluator` los entrega. El solver no predice hechos externos.

`temporal_dependency.py` conserva el contrato V1 para señales legacy y emite V2 cuando hay variante/grupo/eje nodal explícitos. V2 agrupa por raíz, `dependency_group` y `nodal_axis_id`. Norte/Sur y True/Mean nunca constituyen por sí solos raíces adicionales. El resumen no crea scores ni altera IAT.

## Estados e integración

`assess_chiron_process()` emite complejos natales, señales, grupos, cronología, contraevidencia y `temporal_convergence`. La convergencia es un cuadro de conteos y trazabilidad, nunca puntuación ni probabilidad metafísica. La búsqueda de técnicas conserva probadas, coincidencias, preregistradas, exploratorias, el contexto de multiplicidad y si hubo selección posterior.

`INTEGRATION_WINDOW` exige arquitectura natal, una secuencia con referencias de evidencia y al menos dos grupos de dependencia. `INTEGRATION_DOCUMENTED` exige además evento M27 con fuente, rol explícito `INTEGRATION_OUTCOME`, calidad documental primaria o autorreporte directo, contrato de calidad/precisión satisfecho y separación entre hecho e interpretación. Los demás estados reservados no se infieren si no existe una regla ejecutable.

## Fuentes y clasificación epistemológica

La fórmula Mean Node está registrada bajo Jean Meeus como referencia técnica P3. Las descripciones astrológicas contemporáneas de Quirón siguen vinculadas a las fuentes ya registradas para `WOUND_REPAIR`; esta capa personal no las amplía ni las presenta como doctrina universal. Los datos y geometrías son A, los procedimientos B, las doctrinas explícitas C, usos contemporáneos D y reglas de proceso ALMAS E.

## Verificación

Los casos sintéticos están en `examples/chiron-process.synthetic.json`; pruebas dedicadas cubren True/Mean, contactos por pares y triada, triada únicamente temporal, búsqueda exploratoria, dependencia, retornos múltiples, corte de rama, estacionariedad, M27 y esquemas públicos. Las mediciones de la suite y del contrato público se registran en `docs/RELEASE_AUDIT_1.23.0.md`.
