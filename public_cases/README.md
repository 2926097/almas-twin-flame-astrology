# Casos públicos

Este directorio queda reservado para estudios de casos reales cuyos datos subyacentes sean **ya públicos e independientemente verificables**.

Cada caso público debe incluir:

- identificador del caso y título descriptivo;
- fuente pública exacta de cada dato biográfico o evento;
- fecha de recuperación o localizador bibliográfico;
- separación entre hechos de fuente, datos calculados, técnica e interpretación;
- declaración de que el caso no se utilizó para ajustar umbrales, pesos, gates u ontología.

El material obtenido de conversaciones privadas, archivos privados, correspondencia no publicada, registros natales no públicos o historia relacional no pública no es admisible aquí simplemente porque un colaborador tenga acceso a él.

Los fixtures sintéticos pertenecen en `examples/`, no en este directorio.


## Manifiesto obligatorio

Todo JSON añadido a este directorio debe registrarse en `public_cases/manifest.json` como `PUBLIC_VERIFIABLE`.

La entrada requiere `independently_verifiable=true` y `public_source_refs` no vacío.

Un caso pseudonimizado pero basado en datos no públicos continúa siendo privado y no puede registrarse aquí.
