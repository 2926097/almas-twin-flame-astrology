# Autoría de informes personales · ALMAS 1.21

## Contrato

La autoría personal comienza sólo después de cerrar:

`personal_canonical_analysis → personal_report_document_model`.

El resultado es `ALMAS_PERSONAL_AUTHORED_REPORT`. La prosa no recalcula posiciones, casas, aspectos, temporalidad ni ninguna otra geometría.

## Autoridad del modelo documental

Los perfiles personales no contienen siempre once secciones. Por ello, la autoría no usa un orden global fijo: debe conservar exactamente los `section_id` y el orden emitidos por `personal_report_document_model`.

Una sección `NOT_AVAILABLE` se representa como `OMITTED_NOT_AVAILABLE`; no se rellena por inferencia editorial.

## Trazabilidad

Cada sección `AUTHORED` declara:

- `canonical_paths_used`, subconjunto de `available_paths`;
- `epistemic_classes_used`, subconjunto de las clases autorizadas;
- `doctrinal_claim_refs`, sólo si el claim existe en el canonical;
- `source_refs`, sólo si la fuente está en la bibliografía del informe;
- limitaciones relevantes.

La bibliografía es más estricta que en la capa relacional inicial: toda `source_id` debe estar trazada previamente en `personal_canonical_analysis.source_trace` o en referencias de la doctrina canónica. La fase de autoría no puede introducir una fuente nueva silenciosamente.

## Minimización de datos

`personal_data_minimized=true` es obligatorio. La autoría consume el canonical minimizado y no reincorpora fecha, hora, lugar o coordenadas brutas por defecto.

## Invariantes

- mismo fingerprint canónico;
- mismo perfil y estado del modelo documental;
- `metaphysical_scientific_validation_claimed=false`;
- `canonical_values_mutated=false`;
- `new_calculations_performed=false`;
- `new_scores_created=false`.

Este bloque termina en autoría estructurada. La adaptación a DOCX/PDF B5 pertenece al bloque siguiente.
