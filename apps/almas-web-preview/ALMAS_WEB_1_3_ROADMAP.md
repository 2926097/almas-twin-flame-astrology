# ALMAS Web 1.3 — aplicación integral: etapa A

Estado: **CAPTURA ESTRUCTURADA IMPLEMENTADA EN RAMA; CÁLCULO AUTOMÁTICO DESDE EL NAVEGADOR PENDIENTE**.

ALMAS ya posee un ejecutor privado M00–M31. Esta entrega añade un formulario de
dos nacimientos y produce una solicitud `ALMAS_WORK_REQUEST` compatible con él.
No añade una ruta POST remota ni modifica índices y ontología.

## Etapas para completar la aplicación

| Etapa | Objetivo | Criterio de aceptación |
|---|---|---|
| A. Entrada natal | Captura local de dos fechas, horas, zonas horarias IANA, coordenadas, fiabilidad y procedencia; preset explícito | JSON `REQUEST_ONLY`, preflight en Python, sin tráfico de datos natales |
| B. Motor en equipo privado | Conectar solicitud al runner privado con kernel Moira JPL y SHA-256 verificado | M00–M31 ejecutados en dispositivo local, receipt y degradación verificables |
| C. Resultados completos | Consumir exclusivamente el canonical generado por M30; cartas natales, sinastría, compuesta, Davison, dracónicas y capas disponibles | Mostrar ausencia como NOT_EVALUABLE, nunca generar posiciones inventadas |
| D. Índices | Presentar IEM por modelo, IDD, IRC, IAT, ICC, ICE del motor canónico | Mantener nulos, no reimplementar scoring en navegador |
| E. Informe interpretativo | Conectar M30/M31 y reporting oficial, evidencia, contraevidencia, referencias y narrativa autorizada | Solo producir informes cuando los gates oficiales lo permitan |
| F. Seguridad y entrega | Privacidad, aislamiento por caso, control de acceso, borrado y auditoría | No abrir API pública personal hasta GO explícito |

Las hipótesis metafísicas son **interpretaciones de una tradición simbólica**,
no hechos comprobados sobre origen del alma, exclusividad ni probabilidades.
Atacires sigue SHADOW/NO-GO.

## Uso de la etapa A

1. En el visor protegido, abre «Nuevo análisis desde dos nacimientos».
2. Introduce el nacimiento de cada persona con **hora civil local**, zona
   horaria IANA, coordenadas geográficas y calidad de los datos. El lugar
   descriptivo no se usa para geocodificar.
3. Selecciona un perfil y **elige expresamente** el preset experimental
   `ALMAS_RELATIONAL_STRICT_RESEARCH_V1`. No es un default implícito.
4. Pulsa «Preparar solicitud local» y descarga
   `almas-relational-request.local.json` fuera del repositorio.

El formulario no descarga efemérides ni calcula índices. El fichero descargado
contiene datos personales y no debe publicarse en GitHub, Vercel o CI.

## Preflight local (sin astronomía)

Desde un checkout privado del proyecto, con dependencias Python instaladas:

```bash
python scripts/run_relational_work_request.py /ruta/privada/almas-relational-request.local.json \
  --output-dir /ruta/privada/preflight --assessment-only
```

Consulta `request_assessment.json`: debe figurar
`ready_for_raw_input=true` y el fingerprint de la política explícita.

## Ejecución privada real (kernel certificado)

```bash
python scripts/run_relational_work_request.py /ruta/privada/almas-relational-request.local.json \
  --output-dir /ruta/privada/salida \
  --manifest manifests/analysis-pipeline-manifest.json \
  --kernel-path /ruta/local/de440.bsp \
  --kernel-sha256 SHA256_VERIFICADO_DEL_KERNEL \
  --kernel-family DE440 --house-system P
```

El kernel y su SHA se configuran explícitamente: no se inventan, ni se
descargan de forma implícita. El backend rechaza fechas y horas locales
inexistentes o ambiguas por DST. El runner solo escribe `canonical_analysis.json`
si lo genera M30, y produce `execution_receipt.json` con el estado real.
El visor puede abrir luego ese canonical y verificar el triplete M30/M31
cuando las salidas oficiales existan.

## Límites y barrera de privacidad

- No precargar fechas o identidades reales en código ni fixtures.
- La página no envía los valores del formulario ni el JSON descargado.
- Los endpoints de Vercel y Render siguen siendo GET exclusivamente sintéticos.
- Para casos reales remotos persiste la condición NO-GO y la evaluación formal
  de base jurídica, identidad, MFA, segregación, retención y seguridad.
- Esta etapa no toca `src/almas_tfa`, `schemas`, indices productivos, pesos,
  scoring, ontología ni la promoción de Atacires.
