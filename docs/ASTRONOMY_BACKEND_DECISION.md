# Decisión técnica sobre backend astronómico

**Estado:** backend de producción seleccionado e implementado mediante adaptador opcional.  
**Fecha de revisión:** 27 de septiembre de 2026.  
**Release:** ALMAS 1.18.0.

## Contexto

M02 y M08 necesitan un backend capaz de producir posiciones, nodos, declinaciones, casas, ángulos y carta Davison de forma reproducible sin ocultar efemérides, geocodificación, timezone, sistema de casas o fallback.

ALMAS mantiene el desacoplamiento:

`ALMAS → AstrologyBackend/DavisonBackend → adaptador concreto`.

La dependencia astronómica no forma parte del núcleo obligatorio.

## Decisión de producción

ALMAS 1.18 adopta `moira-astro==6.8.2` mediante
`ALMAS_MOIRA_JPL_SPK_V1` como adaptador de producción opcional.

Motivos de selección:

- licencia MIT declarada por el paquete;
- compatibilidad Python >=3.10;
- wheels publicados para Python 3.10 y 3.12;
- soporte de kernels JPL DE-series locales;
- posiciones tropicales, nodos, casas y ángulos;
- API pública para chart/houses;
- cálculo Davison disponible en el proveedor, aunque ALMAS conserva su propia convención explícita de midpoint antes de volver a ejecutar el mismo pipeline natal;
- ausencia de necesidad de Swiss Ephemeris como dependencia transitiva del adaptador ALMAS.

La dependencia se expone únicamente como extra:

`pip install -e ".[astronomy-moira]"`.

## Política de kernel

El paquete no aporta por sí solo la identidad astronómica completa. Todo cálculo de producción ALMAS exige:

1. archivo JPL BSP local;
2. familia declarada `DE430`, `DE440` o `DE441`;
3. SHA-256 esperado;
4. coincidencia exacta del SHA-256 antes de instanciar el motor;
5. nombre del kernel y fingerprint incorporados a la procedencia de salida.

ALMAS no descarga kernels durante el cálculo.

La recomendación operativa inicial es DE440 para el rango moderno, sin hacer del nombre de archivo una fuente de verdad: la identidad normativa es el fingerprint del archivo efectivamente utilizado.

## Política temporal y geográfica

- timezone: IANA explícita;
- hora local ambigua por DST: fail-closed;
- hora local inexistente por DST: fail-closed;
- carta natal sin hora: `NOT_EVALUABLE` en el backend de producción;
- coordenadas numéricas: obligatorias para cartas horarias;
- geocodificación implícita: prohibida.

## Casas y nodos

El sistema de casas se configura explícitamente al construir el backend.

Cualquier fallback polar informado por el proveedor invalida esa ejecución para ALMAS. Si el sistema efectivo difiere del solicitado, el cálculo queda `NOT_EVALUABLE`.

La capa dracónica canónica utiliza `NORTH_NODE`. El adaptador 1.18 fija `TRUE_NODE` como fuente y deriva `SOUTH_NODE` por oposición exacta.

## Declinar posiciones

El adaptador conserva longitud y latitud eclípticas del proveedor y deriva declinación con la oblicuidad verdadera devuelta para la carta:

`sin δ = sin β cos ε + cos β sin ε sin λ`.

Esta operación está aislada y sometida a tests unitarios.

## Davison

ALMAS no delega al proveedor una convención Davison implícita.

La versión 1.18 fija:

- midpoint temporal: `UTC_INSTANT`;
- midpoint geográfico: `SPHERICAL_GREAT_CIRCLE`;
- cálculo final: mismo pipeline natal del backend en el instante/lugar midpoint.

Si la política de entrada no admite esta convención, M08 queda `NOT_EVALUABLE`.

## Swiss Ephemeris

Swiss Ephemeris y sus bindings continúan excluidos como dependencia obligatoria de esta release.

La distribución de software basado en Swiss exige resolver explícitamente la vía AGPL o la licencia profesional. ALMAS no modifica su régimen jurídico de forma implícita para incorporar un backend.

## Verificación independiente

Skyfield permanece como candidato preferente para una segunda vía de verificación de posiciones fundamentales por su licencia MIT y orientación astronómica.

La adopción de Moira como backend de producción no autoriza a usar sus propios resultados como única prueba de exactitud.

Antes de declarar completamente validado el frente astronómico debe existir una batería dorada con kernel real y comparación independiente dentro de tolerancias preregistradas.

## Estado 1.18

La release 1.18 cierra la selección e implementación del adaptador de producción y cambia M02/M08 a `EXECUTABLE_HANDLER`.

Permanece abierto un gate específico de **validación astronómica dorada**:

- kernel JPL real fingerprintado;
- fixtures con fechas/lugares conocidos;
- tolerancias explícitas por magnitud;
- comparación independiente de longitudes planetarias y nodos;
- validación separada de casas/ángulos;
- evidencia de reproducibilidad en Python 3.10/3.12.

Este gate no añade técnicas astrológicas ni altera el scoring.
