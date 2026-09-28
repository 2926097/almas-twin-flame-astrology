# Auditoría final de release · ALMAS 1.20.0

**Fecha:** 28 de septiembre de 2026  
**Rama auditada:** `release/1.20.0`  
**Base funcional:** cierre ALMAS 1.19.0 + desarrollo 1.20 integrado en `main`  
**Tipo de release:** MINOR compatible hacia atrás  
**Objeto:** síntesis interpretativa root-first, ampliación hermenéutica y temporalidad TTRANSIT trazable.

## Alcance

1.20 no sustituye el canonical ni reabre los scores de producción. Amplía la capacidad de convertir la arquitectura ya calculada en una lectura desarrollada, especialmente cuando varias técnicas convergen sobre un mismo motivo.

La cadena sustantiva queda:

`canonical_analysis → raíces/motivos → M30/M31 → authored_report root-first → DOCX/PDF`.

La cadena temporal queda:

`raíz existente → endpoint natal → TTRANSIT → M26 trigger_context → interpretación temporal → límite factual`.

## Cambios auditados

La release incorpora:

- protocolo de síntesis interpretativa root-first;
- hermenéutica de motivos semánticos;
- fuentes técnicas para compuesta/Davison, declinaciones, antiscios, sinastría y casas;
- interpretación de superposición de casas con procedencia;
- recuperación de contactos concretos de raíces normalizadas;
- funciones planetarias, geometría de aspectos y extremos angulares/nodales;
- sustrato natal y campo relacional disponibles para autoría;
- contexto dracónico y contactos planeta–ángulo;
- Fortuna/Espíritu y Juno/Eros como contexto cuando son evaluables;
- hermenéutica temporal M26–M27;
- `trigger_context` preservado para autoría;
- fuentes y contrato de método TTRANSIT;
- generador autónomo TTRANSIT contra endpoints de raíces existentes;
- fixture sintético de lectura temporal root-first enlazado al resultado M26.

## Separación de capas

El release conserva la separación:

- **A · calculado:** geometría, señales, raíces y valores derivados por el motor;
- **B · técnica:** reglas astrológicas y método;
- **C · doctrina:** afirmaciones documentadas en tradiciones concretas;
- **D · uso contemporáneo:** cuando proceda;
- **E · hipótesis ALMAS:** síntesis y función evolutiva.

Una fuente doctrinal o técnica documenta significado; no incrementa por sí sola un índice.

## Temporalidad

El generador TTRANSIT no realiza predicción factual. Calcula contactos entre posiciones transitantes y endpoints natales ya contenidos en raíces M17, aplicando `aspect_policy` explícita.

M26 conserva el contexto concreto del disparador para que S07 pueda expresar:

`quién/qué transita → qué aspecto forma → qué endpoint activa → en qué raíz se integra`.

La ventana temporal vuelve más saliente una función estructural. No crea la relación, el contrato, la misión ni una decisión de terceros.

## Compatibilidad

1.20 conserva los contratos principales de 1.19:

- mismos modelos AF/KA/AG/LG;
- mismos índices operativos;
- misma arquitectura M00–M31;
- mismo contrato de `authored_report`;
- mismos perfiles `ALMAS_B5_BOOK_V1` y `ALMAS_B5_PDF_V1`;
- mismo `engine_revision=1.9.0` del módulo contractual;
- ningún discriminador L3 real activado.

## CI de la rama de release

La PR de cierre 1.20.0 registró:

- `Núcleo Python` Python 3.10: SUCCESS, 537 tests, 7 skipped;
- `Núcleo Python` Python 3.12: SUCCESS, 537 tests, 7 skipped;
- `Contrato público`: SUCCESS;
- `Backend astronómico`: SUCCESS;
- `Publicación DOCX`: SUCCESS;
- `Publicación PDF`: SUCCESS.

El único defecto detectado en el fixture temporal fue una igualdad exacta de coma flotante (`0.5249999999999999` frente a `0.525`). Se corrigió el test para usar `assertAlmostEqual(..., places=12)`; no se redondeó el motor ni se modificó la señal canónica.

## Estado epistemológico

La release mejora la calidad, profundidad y trazabilidad de la lectura astrológica y metafísica. No demuestra científicamente una ontología relacional ni convierte una señal temporal en probabilidad de un hecho futuro.

Cuando distintas ontologías producen una firma observable equivalente y no existe discriminador validado, el sistema conserva la indeterminación correspondiente.

## Criterio de cierre

La release puede declararse cerrada cuando:

1. todas las superficies públicas de versión coinciden en 1.20.0;
2. los documentos `EVOLUTION_1.20.0.md` y `RELEASE_AUDIT_1.20.0.md` forman parte del contrato público;
3. el núcleo, contrato público y backend astronómico pasan CI en la rama de release;
4. no aparece una regresión en autoría/publicación derivada de los cambios 1.20;
5. no se activa scoring, discriminador o inferencia ontológica fuera de los contratos ya publicados.
