# ALMAS Web 1.3 — inicio del flujo integral (fase 1)

## Implementación real

El panel de dos nacimientos captura fecha, hora local opcional y calidad A/B/C/D. La interfaz pide **ciudad de nacimiento**, muestra coincidencias con provincia/región y país y solo tras una selección explícita obtiene latitud, longitud WGS84 y zona IANA en campos ocultos. El servicio de Open-Meteo se consulta solo al pulsar Buscar ciudad, enviando únicamente la cadena buscada; nunca nombres, fechas, horas o el análisis. La zona civil histórica sigue validándose en el servidor Python local (DST ambiguo/inexistente). No hay geocodificación automática sin consentimiento operativo. Construye un **ALMAS_WORK_REQUEST** con `format=ALMAS_WORK_REQUEST`, `type=RELATIONAL`, `execution_state=REQUEST_ONLY`, `public_version=1.26.0`, dos sujetos A/B, perfil seleccionado y preset explícito `ALMAS_RELATIONAL_STRICT_RESEARCH_V1`. No infiere órbitas, nodos, posiciones ni cartas; no incluye `atacires_requests`.

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

## Incremento integrado — servicio local M00–M31 (fase 2)

Implementado `local_engine_server.py` como **programa independiente** que se ejecuta en el ordenador del usuario y solo escucha en `127.0.0.1`. La aplicación Vercel sigue siendo exclusivamente sintética; el botón de cálculo **solo aparece** si se obtiene una capacidad válida del servicio local desde `http://127.0.0.1`, nunca en HTTPS público. La llamada privada requiere acción humana, `Host` y `Origin` de loopback idénticos, token CSRF efímero por proceso y JSON de menos de 64 KiB. Rechaza duplicados de claves y entradas libres, horarios DST inexistentes o ambiguos, coordenadas no finitas, solicitudes Atacires, eventos no autorizados y overrides del preset.

El servidor invoca el `execute_relational_work_request` **original**, con el manifiesto M00–M31 y `MoiraProductionBackend` configurado por parámetros **locales**: archivo de efemérides, SHA-256 esperado, familia DE430/DE440/DE441 y sistema de casas. No descarga kernels, no ejecuta tareas LLM y no almacena nombres, fechas, coordenadas ni resultados en archivos/logs/analytics. El cálculo completo **requiere** los paquetes `moira-astro==6.8.2`, `jsonschema==4.26.0` y un kernel verificado. Sin estos requisitos no hay fallback aproximado.

Cuando el pipeline entrega canónico oficial, se comprueban los tres esquemas, los SHA-256 de M30 y M31, los estados de reportabilidad y la ausencia de mutación del canónico. El navegador revalida la estructura canónica, presenta las posiciones e índices calculados, verifica de nuevo M30/M31 antes de permitir el HTML declarativo y deja exportar un JSON local de resultados **solo mediante pulsación expresa**. Ningún dato natal se envía al backend sintético remoto. Las opciones de publicación DOCX/PDF y la narrativa de autoría siguen bloqueadas si falta autoría trazable.

### Instalación y ejecución en un equipo privado

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[astronomy-moira,schema-validation]'
cd apps/almas-web-preview
npm install --no-audit --no-fund
npm run build
cd ../..
PYTHONPATH=src .venv/bin/python apps/almas-web-preview/local_engine_server.py \
  --kernel-path /RUTA/LOCAL/DE440.bsp \
  --kernel-sha256 SHA256_HEXADECIMAL_64_CARACTERES \
  --kernel-family DE440 \
  --house-system PLACIDUS \
  --port 8765
```

Abrir `http://127.0.0.1:8765/` **en el mismo equipo**. No abrir una puerta/firewall pública, túnel, reverse proxy o modo host `0.0.0.0`: el servicio lo rechaza por diseño. El proceso local no es un despliegue online para usuarios independientes. La aplicación de Vercel continúa en modo preview sin datos personales.

### Pruebas que bloquean la fusión

- `node --test apps/almas-web-preview/test/birth-request.test.mjs`
- `PYTHONPATH=src:tests python -m unittest discover -s apps/almas-web-preview -p 'test_local_engine_server.py' -v`
- `npm run build`, suite completa aislada, seis workflows remotos en PASS en **el mismo SHA**
- Contraste con `run_relational_work_request.py` y manifest de producción sin modificar scoring ni ontología
- Integración sintética con kernel real verificada en `1294cf8b5f6a47b06e3e578f8ba7fdace4b4fe0e`, run [38560213185](https://github.com/2926097/almas-twin-flame-astrology/actions/runs/38560213185): DE440s con checksum preregistrado, 32 módulos, canonical y fingerprint válidos. Es una prueba técnica sintética de ese SHA; para otro HEAD se exige una ejecución aplicable, no se hereda el PASS. No sustituye COMPLETE_GATE, validación empírica externa ni certificación de un equipo privado.

### Gates que permanecen

**NO-GO producción privada**, no autenticación multiusuario ni nube personal; no publicación automática ni DOCX/PDF narrativo; Atacires permanece SHADOW/NO-GO; todos los índices continúan calculados únicamente por el núcleo. El modelo M31 es declarativo y no constituye interpretación autoral exhaustiva ni identificación ontológica de almas.


## Incremento de interfaz — ciudad de nacimiento (búsqueda explícita)

- `birth-geocoding.mjs`: consulta de nombres globales a Open-Meteo/GeoNames (GET `name`, `count`, `language`, `format`); los resultados de usuario requieren ID único, latitud y longitud finitas, zona horaria IANA no vacía y localidad/país. No se selecciona un resultado por defecto.
- `birth-ui.mjs`: campos visibles de ciudad A/B y búsqueda con botón, selección confirmada, eliminación de coordenadas visibles. Cambios de texto o búsqueda distinta invalidan una selección anterior y sus resultados/exportaciones; se ignoran respuestas antiguas.
- La zona IANA y las coordenadas siguen consumiéndose por el adaptador relacional Python original, sin alterar el contrato, índices o motor. Solo el nombre de ciudad buscado abandona el navegador cuando el usuario busca; el catálogo de Open-Meteo tiene límites de cobertura/precisión y la API gratuita está restringida a uso no comercial. Atribución CC BY 4.0 visible.
- En el servidor privado loopback, la CSP permite exclusivamente `connect-src 'self' https://geocoding-api.open-meteo.com`. Vercel no publica análisis natales ni endpoints personales. Si falta localidad, región, país o zona válida, la interfaz bloquea el análisis en lugar de inventar coordenadas.

Pruebas: `node --test apps/almas-web-preview/test/birth-geocoding.test.mjs apps/almas-web-preview/test/birth-city-ui.test.mjs`. Integradas a la suite web en GitHub Actions.

## Corte de reconciliación · 24 octubre 2026

La PR #110 se integró en `0451685910c1e432650ee145a718ccccbf24e4c1`. Conserva el formulario único por ciudad y recupera validaciones estrictas IANA/coordenadas, preset elegido expresamente y regresión JS → adaptador Python. La exportación sigue en `REQUEST_ONLY`; el cálculo se realiza únicamente mediante el servicio local ya descrito. Seis workflows y 27 jobs del HEAD de la PR, y seis workflows principales más tres runs Release SSAR del merge, finalizaron en success. El corte detallado y sus límites constan en `VALIDATION_STATUS.md`.

La edición humana local y la CLI experimental de doce secciones, integradas mediante PR #114/#116/#117, permiten producir DOCX/PDF B5 solo tras autoría trazable, schemas, M30/M31, fingerprint y preflight. No son publicación automática ni sustituyen el authored-report oficial de once secciones. Las prohibiciones de publicación sin autoría anteriores se refieren a ese supuesto, no a esta vía local experimental. Véase `README.md` de esta aplicación para los comandos vigentes.

La reconciliación de #110 no desplegó ni recertificó Vercel. Un nuevo despliegue requiere verificar por separado commit, target Preview, estado READY, SSO para todos los deployments y rutas privadas inaccesibles. Ningún resultado de CI autoriza por sí solo producción ni tratamiento personal remoto. Atacires permanece SHADOW/NO-GO.
