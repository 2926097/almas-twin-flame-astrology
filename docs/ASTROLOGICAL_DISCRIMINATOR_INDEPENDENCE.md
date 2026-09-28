# Independencia astrológica del discriminador ontológico · Paso 13

## Finalidad

ALMAS utiliza astrología como una metodología de análisis, no como verdad de referencia ontológica.

Por tanto, ninguna configuración astrológica puede decidir por sí misma entre soulmate, origen monádico, split-soul o twin-flame.

La regla ejecutable es:

`uses_astrology=true -> requisitos L3 generales + astrology_validation completa`.

## Qué cuenta como dependencia astrológica

Un discriminador se marca `uses_astrology=true` cuando su observable, proxy, selección de casos o regla decisoria depende materialmente de datos o técnicas astrológicas.

Esto incluye, entre otras capas:

- sinastría tropical;
- declinaciones;
- antiscios;
- carta compuesta;
- Davison;
- dracónica y cruces natal-dracónica;
- asteroides;
- progresiones;
- arco solar;
- atacires;
- técnicas temporales;
- recurrencia entre familias técnicas;
- rareza bajo modelos nulos.

No importa que la astrología sea sólo una parte de un diseño mixto: si afecta la decisión discriminante, el registro se considera astrológico.

## Requisitos adicionales para L3

Además de preregistro, replicación independiente, holdout externo, controles negativos y auditoría de leakage, un discriminador astrológico necesita:

- `non_astrological_criterion_refs`: criterio externo independiente de la astrología;
- `astrology_ablation_refs`: prueba de qué ocurre al retirar familias o features astrológicas;
- `matched_control_refs`: controles comparables procesados con exactamente el mismo pipeline;
- `dependency_audit_refs`: auditoría de raíces compartidas y pseudo-replicación;
- `out_of_sample_refs`: comportamiento fuera de muestra;
- `astrology_specific_replication_refs`: replicación específica de la regla astrológica.

También debe declarar tres invariantes lógicas:

- `single_feature_prohibition_acknowledged=true`;
- `null_rarity_not_ontological=true`;
- `temporal_activation_not_origin_proof=true`.

## Criterio externo

El criterio externo no astrológico no puede ser:

- autoetiqueta “somos twin flames”;
- opinión de un astrólogo;
- canalización;
- regresión;
- sensación de destino;
- intensidad;
- número de sincronías;
- duración, matrimonio o ruptura tomados como ontología.

Puede ser una variable documental o experimental preregistrada, siempre que mida la predicción operacional concreta y no presuponga la categoría metafísica.

## Firewall de feature única

Un aspecto aislado, un asteroide, un atacir, un eclipse, una conjunción exacta o una sincronía temporal nunca puede crear una categoría ontológica.

Incluso una recurrencia multicapa sólo constituye evidencia del proxy definido. Para actuar como L3, la regla completa debe haber superado validación discriminante independiente.

## Rareza

M24 puede describir rareza estructural bajo un modelo nulo.

La rareza no se transforma en:

- probabilidad de ser twin flame;
- probabilidad de origen monádico;
- prueba de split-soul;
- peso ontológico automático.

Por eso el registro exige `null_rarity_not_ontological=true`.

## Temporalidad

Progresiones, arco solar, atacires, tránsitos u otras técnicas temporales pueden indicar cuándo se activa una arquitectura previamente definida.

No pueden crear retrospectivamente dicha arquitectura ni demostrar su origen. Por eso se exige `temporal_activation_not_origin_proof=true`.

## Estado de los candidatos actuales

En el registro productivo se marcan conservadoramente como dependientes de astrología:

- OD01_PAIR_SPECIFICITY_NETWORK;
- OD02_DYADIC_STRUCTURAL_ISOMORPHISM;
- OD04_PROSPECTIVE_MODEL_PREDICTION.

Los tres permanecen sin promoción L3 y con `astrology_validation=null`.

OD03 es no astrológico. OD05 y OD06 están bloqueados por no observabilidad. OD07 está retirado por no discriminación.

## Límite inferencial

Validar un proxy astrológico fuera de muestra demostraría, como máximo, que la regla discrimina el observable operacional definido dentro de su alcance.

No demostraría directamente la existencia metafísica de twin flames, split souls o una Mónada común.

## Siguiente fase

El Paso 14 ampliará el protocolo de validación externa con validez discriminante explícita, tasa de falsa especificidad y criterios cuantitativos de fallo/promoción.
