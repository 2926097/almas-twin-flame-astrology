# ALMAS 1.25.0 R3 · Auditoría corregida de base

Fecha: 2 de octubre de 2026. Base reproducible: `73caa8c7356139f4da87a97cbf91f4005ce1840c`, ALMAS 1.25.0 SSAR congelado. La copia completa se verificó contra los hashes Git de los blobs y se recuperó su historial.

## Rectificación del primer informe

El informe preliminar examinó una referencia anterior (1.24.1) y afirmó incorrectamente que no existía un solver de exactitud. La inspección completa encontró `temporal_perfection_solver.py`: resuelve cruces y contactos estacionarios, conserva contexto de movimiento y múltiples perfecciones. Esta auditoría sustituye la afirmación anterior. RRA reutiliza el solver y añade definiciones, cartas, anclajes, eventos, controles y contratos específicos.

| Capacidad en la base | Estado y decisión R3 |
|---|---|
| Solver de perfecciones | Existente; reutilizado. Se corrige cancelación del residual próximo a cero para no duplicar una tangencia. |
| Posiciones, velocidades y procedencia | Moira de producción disponible; se conserva versión/kernel y ausencia de fallback. |
| Cartas de retorno | Faltaba API pública; se añade `calculate_return_chart` sobre el cálculo ya existente. |
| Variantes geográficas | Coordenadas y backend existentes; RRA añade bases explícitas, fuentes y análisis separado. |
| Natal, sinastría, compuesta, Davison, dracónica | Arquitectura existente; RRA exige procedencia y referencias a raíces previas. |
| SSAR | Base 1.25.0 congelada. Sus recursos y hashes permanecen intactos; la extensión se valida por un envelope independiente. |
| M26 y M27 | Permanecen como módulos existentes. RRA conserva su registro experimental separado y recibe eventos explícitos; no sustituye el IAT. |
| Dependencia y raíces M17 | Se consumen raíces existentes; no se crean raíces. La dependencia desconocida se agrupa conservadoramente. |
| Canonical/M30/M31 | Extensión optativa antes del ensamblaje y rutas de informe. Un canonical ya importado conserva prioridad. |
| Controles | Nuevos controles condicionales, presupuesto fijo, ablaciones y negativos. No se afirma intercambiabilidad ni validación externa. |

## Cierre técnico y límites

Políticas, contratos, módulos, CLI, documentos de fuente/método y pruebas se incorporan en la misma rama de implementación. La verificación incluye casos sintéticos, invariantes del pipeline y efemérides reales contrastadas con Skyfield. El recibo numérico conserva kernel, versiones, tolerancias y cinco pasadas.

RRA V1 no implementa recurrencias no homólogas angulares, antiscios o declinaciones sin política propia; no sustituye el cálculo canónico de cartas derivadas. Los controles nulos sobre cartas EVENT que exigirían recomputación se bloquean expresamente. La densidad anual es descriptiva. La validación relacional externa permanece `NOT_PERFORMED`: requiere una cohorte preregistrada no empleada en el diseño.
