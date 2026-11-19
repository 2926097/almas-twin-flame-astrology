# Recuperar efemérides sin detener la lectura

## Ruta operativa

Comprobar executor, librerías y archivos reales; consultar catálogo ALMAS y datos natales autorizados. Buscar el producto diario como optimización, nunca como dependencia necesaria. Si falta, calcular con efemérides válidas o consultar Horizons. No confundir una efeméride orbital que cubre años con un JSON diario inexistente.

Intentar primero los archivos locales validados; después una distribución Swiss accesible, después otro dominio y finalmente Horizons directo. Si no hay `swisseph`, usar el script de biblioteca estándar directamente; no bloquearse instalando paquetes. Si Horizons falla, intentar las rutas Swiss que no se hayan probado y una consulta web o conector permitido. La web debe proporcionar respuesta numérica y metadatos del instante, no solo enlaces a la API. El script implementa la ruta Horizons, no todas las rutas de este documento: el agente debe completar las restantes disponibles.

Por endpoint usar timeout 15 segundos y como máximo dos intentos únicamente para timeout/429/5xx transitorios; ante DNS, HTML, 404, identidad incorrecta o formato inválido, cambiar de ruta. Mantener consultas JPL secuenciales. No cambiar DNS del sistema ni eludir controles de red. No atribuir a DNS un bloqueo HTTP. Registrar tipo de fallo por proveedor, sin generalizarlo a todos los accesos.

## Swiss Ephemeris

Distribuciones documentadas: https://github.com/aloistr/swisseph y https://www.astro.com/swisseph-download/ ; alternativa https://ephe.scryr.io/ephe/ (verificar disponibilidad, no asumirla).

Consultar listado real antes de inventar una URL de archivo. Los archivos individuales no están necesariamente en el árbol GitHub estándar. Para número n, usar `ast{n//1000}/se{n:05d}s.se1` o la variante larga `se{n:05d}.se1`. Descargar a temporal, rechazar HTML/JSON/página de error aunque devuelva HTTP 200, y mover al destino solo tras validación de lectura y cobertura con Swiss. Una huella identifica el contenido, no demuestra corrección orbital. No guardar respuestas inválidas como efemérides en caché. Para Quirón usar `swe.CHIRON` con `seas_18.se1` para fechas 1800–2399; para Juno `swe.JUNO` puede usar el archivo principal de asteroides.

```python
import swisseph as swe
swe.set_ephe_path('/ruta/ephe')
flags = swe.FLG_SWIEPH | swe.FLG_SPEED
# jd corresponde al instante UTC convertido según el tratamiento temporal de Swiss.
xx, returned = swe.calc_ut(jd, swe.AST_OFFSET + 2847, flags)
if (returned & swe.FLG_EPHMASK) != swe.FLG_SWIEPH:
    raise ValueError('Motor distinto del solicitado: comprobar fallback')
longitude, latitude, distance, speed = xx[:4]
```

Verificar flags, excepciones, identidad, valores finitos y cobertura calculando todos los instantes pedidos. No fabricar un fallback Moshier para cuerpos que lo requieren. Calcular hoy y ayer con el mismo método; para comparación de proveedores registrar versión y diferencias angulares. No clonar un repositorio enorme ni descargar todo el catálogo para resolver ocho objetos.

## Horizons exacto, sin conversión improvisada

Documentación primaria: https://ssd-api.jpl.nasa.gov/doc/horizons.html y https://ssd.jpl.nasa.gov/horizons/manual.html (cantidad 31). El script usa número con punto y coma para seleccionar cuerpo menor, `CENTER='500@399'`, `EPHEM_TYPE='OBSERVER'`, `QUANTITIES='31'`, `TIME_TYPE='UT'`, salida CSV y segundos. Verificar en respuesta nombre/número, Earth (399), GEOCENTRIC (o BODY CENTER según interfaz), fechas solicitadas y columnas ObsEcLon/ObsEcLat. Una ambigüedad de identidad exige resolver en SBDB https://ssd-api.jpl.nasa.gov/doc/sbdb.html ; no escoger la primera coincidencia.

La cantidad 31 desde el geocentro entrega eclíptica aparente de fecha IAU76/80; no necesita convertir RA/Dec ni usar vectores geométricos J2000 como sustituto. Swiss y Horizons pueden diferir por sus convenciones: contrastar discrepancias antes de afirmar segundos de arco, exactitudes o contactos fronterizos. La velocidad del script es una aproximación central a ±1 h, no una certificación de estación o perfeccionamiento. Cerca de velocidad cero, reducir paso y comprobar estabilidad; si falta velocidad fiable, indicar movimiento no resuelto. Una raíz de aspecto requiere cálculos adicionales que la encierren y búsqueda numérica verificable.

Ejecutar desde la carpeta de habilidad:

```bash
python3 scripts/horizons_positions.py --at 2026-10-31T09:00:00Z --cache /ruta/temporal/almas-ephe
```

La caché conserva respuesta y consulta exactas; su existencia no garantiza persistencia entre sesiones. No reutilizar el archivo de ayer como si fuera de hoy. Si el entorno ofrece almacenamiento duradero permitido, conservar allí efemérides reutilizables y manifiesto, sin adjuntar datos privados a repositorios públicos.

## Contactos y cobertura

Computar distancias circulares y verificar la zona histórica antes de convertir la hora natal. Para compuesta y Davison exigir cálculo documentado.

Entregar cobertura y razones concretas de faltantes. Si todos los datos fallan, declarar que no fue posible el cálculo tras enumerar brevemente las vías realmente intentadas. No prometer que mañana se resolverá ni reemplazar la lectura por explicaciones genéricas de asteroides. Si queda información válida suficiente, completar la lectura parcial con conclusión proporcionada y límites visibles. No promover NO-GO/NOT_EVALUABLE ni modificar pesos o estados metodológicos.
