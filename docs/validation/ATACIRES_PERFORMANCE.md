# ALMAS · Rendimiento Atacires

Medición local de 6 de octubre de 2026, Python 3.12.14. Recibo reproducible: `atacires-performance.json`, junto a este documento. Es un benchmark sintético del proceso local, no un SLA ni una demostración de rendimiento en Render.

El núcleo con 2 puntos registra p95 de 0.211003 ms. Con 20 puntos, cinco aspectos y 50 años registra p95 de 32.142422 ms y memoria máxima observada de 1625614 bytes. El camino real OFF, incluida la lectura de la variable de entorno, presenta una razón p95 de 1.025832 frente a M26; en esta muestra permanece por debajo del umbral 1,20 del contrato.

Los límites son 100 puntos y 20 aspectos por solicitud, 40.000 combinaciones orientadas en el adaptador, 10.000 eventos por cálculo, 16 solicitudes por lote, 10.000 raíces admitidas y 10.000 vínculos/señales acumulados. Intervalos o ventanas que desborden datetime producen error tipado. El máximo operativo puede ser un rechazo por límite y no garantiza completar el producto cartesiano de todos los límites a la vez. La robustez admite hasta 1.000 muestras ya recalculadas.

El benchmark separa geometría pura de generación natal, transporte y backend; no sustituye una medición de pipeline completo ni avala técnicas astronómicas futuras. Ejecutar `python benchmarks/atacires_benchmark.py` para repetirlo y comparar bajo condiciones equivalentes.
