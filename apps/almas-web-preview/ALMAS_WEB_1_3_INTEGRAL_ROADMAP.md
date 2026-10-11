# ALMAS Web 1.3 — inicio del flujo integral (fase 1)

## Implementación real

El panel de dos nacimientos captura fecha, hora local opcional, calidad A/B/C/D, zona IANA (comprobación de **formato**, no verificación del calendario DST en el navegador), latitud y longitud explícitas. Validación fail-closed de fecha y rangos; no hay geocodificación implícita. Construye un **ALMAS_WORK_REQUEST** con `format=ALMAS_WORK_REQUEST`, `type=RELATIONAL`, `execution_state=REQUEST_ONLY`, `public_version=1.26.0`, dos sujetos A/B, perfil seleccionado y preset explícito `ALMAS_RELATIONAL_STRICT_RESEARCH_V1`. No infiere órbitas, nodos, posiciones ni cartas; no incluye `atacires_requests`.

El JSON puede exportarse localmente. Esta fase **no ejecuta** el backend, ni calcula cartas o índices ni fabrica narrativas. No envía datos al servidor; los endpoints sintéticos existentes permanecen invariables. Integración aislada en `apps/almas-web-preview`, sin modificar `src/`, `schemas/`, índices, scoring u ontología.

## Siguientes hitos, con puertas de aceptación

1. **Normalización geográfica y temporal**: selección explícita de geocodificación verificada, zona IANA y resolución segura de horarios DST ambiguos/inexistentes; consentimiento y mínima retención. Nunca asumir huso por país o ciudad.
2. **Ejecución privada**: invocar el adaptador existente `assess_relational_work_request` y `execute_relational_work_request` solo desde backend autenticado, con autorización, límites, auditoría minimizada y políticas de privacidad aprobadas. Backend Moira/JPL con kernel local y SHA-256 verificado. Mantener NO-GO hasta disponer de esas garantías.
3. **Pipeline completo**: manifest oficial M00–M31, pruebas de regresión, generación de canonical solo desde M30, índices producidos por el motor (no derivados en JavaScript). Faltantes como `NOT_EVALUABLE`.
4. **Interpretación trazable**: posición por signo/casa/decanato/regencia y retrogradación según datos reales; sinastría, compuesta/Davison, dracónica, Jyotiṣa, lotes y puntos compatibles si el motor los provee. Separar cálculo, interpretación simbólica e hipótesis metafísica.
5. **Informes y salida**: M30/M31 con SHA coincidente, estados PARTIAL/BLOCKED respetados, narrativas trazables y exportación DOCX/PDF solo mediante pipelines oficiales. Atacires permanece SHADOW/NO-GO y no modifica los índices productivos.

## Verificación

```bash
cd apps/almas-web-preview
npm ci --no-audit --no-fund  # o npm install cuando no exista lockfile
npm run build
npm test
```

**Contrato:** habilitar cálculo y almacenamiento privado requiere un gate separado y revisión técnica, no basta con completar un formulario. La capacidad actual es creación de solicitudes, no cálculo automático.
