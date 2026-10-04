# Contrato PU-M V1

PU-M evalúa afirmaciones doctrinales y un proxy de especificidad relativa. Su estado es FROZEN_EXPERIMENTAL. PU_O permanece NOT_EVALUABLE y pu_score es null. No modifica PU heredado, IEM, IRC, ORIGIN ni gates M30/M31. La extensión requiere ejecución explícita lateral y no se introduce silenciosamente en canónicos históricos.

PU_D conserva por valor y modelo requisitos de fuentes verificadas y correspondencias declaradas con evidencia referenciada. La API no autentica documentos ni comprueba el contenido de sus referencias: las correspondencias quedan declaradas, no verificadas independientemente. La compatibilidad doctrinal no suma fuerza estructural.

PU_R extrae CORE_PRIMARY_MOTIF_MAX_V1 desde raíces core y asignaciones M18. Los ceros sólo representan ausencia en un inventario completo; datos faltantes bloquean extracción. Los máximos por motivo son un proxy E experimental y pertenecen a un único grupo DERIVED_CORE_GRAPH, sin votos independientes. Una firma explícita y pesos positivos producen distancia absoluta media ponderada. El margen compara cada díada con esa firma. Un margen menor o igual al de equivalencia contradice exclusividad operacional, sin contradecir la ontología. Diferencia favorable sólo permite COMPATIBLE.

El protocolo exige comparadores reales distintos que compartan exactamente uno de los sujetos, ambos sujetos cubiertos, misma configuración declarada, backend e ICC y un mínimo IRC fijado explícitamente. El registro DECLARED_FROZEN se compara por hash, pero no se autentica como preregistro externo. Un protocolo DRAFT conserva INSUFFICIENT. Calidad ausente o insuficiente conserva NOT_EVALUABLE. La población de referencia es la red declarada, nunca todas las personas.

La firma se deriva del canónico, pero la huella sólo verifica integridad del objeto, no autenticidad de las fuentes o de la ejecución. La selección de comparadores y las declaraciones de protocolo requieren auditoría externa. Datos sintéticos validan comportamiento e invariantes; no eficacia empírica.

API: assess_metaphysical_singularity(request), build_singularity_signature(case), render_metaphysical_singularity_summary(result). CLI: python -m almas_tfa.metaphysical_singularity_cli entrada.json -o salida.json. El módulo es importable desde almas_tfa.metaphysical_singularity y no altera los exports legacy.
