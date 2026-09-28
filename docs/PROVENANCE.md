# Procedencia pública y versionado

La versión `1.0.0` constituye la línea base pública de versionado semántico del repositorio.

El repositorio público prioriza el método y excluye material de casos no públicos. La procedencia registra el origen de reglas publicadas, referencias de fuentes, cambios de código, fixtures sintéticos y cualquier material de casos reales cuyos datos subyacentes ya sean públicos e independientemente verificables.

Los cambios públicos posteriores usan versionado semántico:

- **PATCH** — corrección de implementación o documentación que no modifica la metodología declarada.
- **MINOR** — módulo nuevo compatible hacia atrás, capa de fuentes, técnica opcional o capacidad generalizada.
- **MAJOR** — cambio de ontología, fórmula de puntuación, gates, reglas de independencia o contratos canónicos.

Todo cambio metodológico debe seguir siendo reproducible a partir de entradas generalizadas o fixtures explícitamente sintéticos. Los estudios de casos reales públicos pueden documentarse por separado cuando sus datos de origen ya sean públicos y estén citados; el material de casos privados permanece fuera del alcance de publicación del repositorio.
