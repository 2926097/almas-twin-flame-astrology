# ALMAS 1.15.0 · Specificity Calibration

## Objetivo

ALMAS 1.14.0 corrigió la infradetección de recurrencia semántica de 1.13.0.
La siguiente evolución no debe reducir o aumentar PX mirando un caso concreto.
Primero debe medir **qué tipo de recurrencia está produciendo PX** y cuánto
depende de una familia técnica concreta.

La fase S1 introduce una capa diagnóstica que no cambia ningún score.

## S1 · Recurrence Quality Diagnostics

Política: `ALMAS_RECURRENCE_QUALITY_DIAGNOSTICS_V1`.

Se mantienen separadas:

- identidad geométrica: `root_key`;
- identidad semántica: `motif_id`;
- calidad de recurrencia: diagnóstico descriptivo.

Cada motivo recurrente publica:

- número de familias de dependencia;
- clases técnicas distintas;
- entropía normalizada de fuerza entre familias;
- número efectivo de familias;
- participación de la familia dominante;
- recurrencia después de retirar `NATAL_DRACONIC`;
- supervivencia leave-one-family-out;
- supervivencia leave-one-class-out.

Clases técnicas iniciales:

- SYN → TROPICAL_RELATIONAL;
- DECLINATION/ANTISCIA → SYMMETRY;
- RELCHART → RELATIONSHIP_CHART;
- NATAL_DRACONIC → DRACONIC_CROSS;
- DRACONIC_DD/SECONDARY → SUPPORT_ONLY.

Las familias desconocidas core se conservan como clase propia para no ocultar
nuevas técnicas.

## Invariante central

S1 **no modifica** PX, PS, IEM, IDD, IRC ni la clasificación ontológica.

La observación de que un motivo dependa de dracónica o sobreviva a múltiples
ablaciones se registra, pero todavía no se transforma en peso. Hacerlo antes de
calibración externa produciría una nueva forma de case fitting.

## Siguientes fases

S2 construirá una batería de modelos nulos y controles sintéticos que mida la
tasa de saturación de cada motivo y de cada descriptor de calidad.

S3 congelará candidatos de PX v3 únicamente si muestran discriminación fuera
del conjunto de desarrollo.

S4 podrá modificar PX/PS sólo después de preregistro, controles negativos,
ablación por familia y validación fuera de muestra.

Los casos usados para descubrir estos problemas permanecen DEVELOPMENT_ONLY
para cualquier regla derivada de esta línea metodológica.
