# RRA · Endpoint descriptivo candidato 0.1

El runner operacionaliza la comparación del protocolo candidato; no habilita la evaluación confirmatoria. Su entrada identifica cada vínculo, personas y componente, hash de la ejecución RRA, fechas evento/control, incertidumbre, fuentes, cobertura y estrato de selección. Las ejecuciones deben validar el contrato RRA y compartir política. Las referencias documentales se conservan para auditoría; el programa no autentica originales ni acredita observación negativa.

Cada fecha recibe un indicador binario de existencia de al menos un contacto no tautológico anclado y dentro de la ventana exacta. Se examina el universo declarado completo. El ciclo activo no satisface ese indicador. Cobertura parcial, fechas futuras, incertidumbre que cruza la frontera o procedencia temporal ausente conservan un valor nulo. Una cobertura completa sin retornos puede producir cero. Las cartas EVENT se excluyen de esta comparación porque sus controles requieren recálculo específico.

Dentro de cada vínculo se restan las tasas de eventos y controles evaluables. Se promedian las diferencias de los vínculos evaluables dentro de cada componente y después las diferencias de los componentes con peso igual. La salida conserva totales, evaluables, positivos, pérdidas, componentes excluidos y razones. Esta regla es una propuesta E del proyecto; todavía no está congelada en un preregistro confirmatorio ni acredita independencia estadística. Las pérdidas diferenciales pueden sesgar la comparación y deben examinarse antes de cualquier uso inferencial.

Los controles son consultas técnicas de fechas, no afirmaciones de acontecimientos ocurridos. La igualdad del universo astronómico no justifica por sí sola intercambiabilidad. No se implementan p-valores, intervalos inferenciales, ajuste de multiplicidad ni potencia poblacional mientras no exista un diseño verificable. Sólo se aceptan modos SYNTHETIC_TEST_ONLY y DESCRIPTIVE_ONLY; FROZEN_CONFIRMATORY se rechaza. El estado de validación externa real sigue NOT_PERFORMED.

La demostración reproducible reside en `tests/fixtures/rra_external_descriptive`, sin personas reales. Ejecutar desde la raíz del repositorio:

```bash
python scripts/run_rra_external_descriptive.py \
  --study tests/fixtures/rra_external_descriptive/study.json \
  --output /tmp/rra-descriptive.json
```

El recibo esperado sirve para regresión del endpoint, no para validar astrología. La implementación no elimina los requisitos de cohorte independiente, doble codificación, controles, tamaño muestral, intercambio y preregistro del protocolo.
