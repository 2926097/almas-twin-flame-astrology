# Decisión técnica sobre backend astronómico

**Estado:** decisión de implementación aplazada; interfaz aprobada.  
**Fecha:** 25 de septiembre de 2026.

## Contexto

M02 necesita un backend capaz de producir posiciones astronómicas reproducibles y, en el despliegue completo de ALMAS, soportar o permitir construir casas, ángulos, nodos, declinaciones, asteroides y cálculos derivados.

El núcleo no debe acoplarse a una biblioteca externa antes de resolver cobertura, mantenimiento y licencia. Por ello se ha introducido primero el protocolo `AstrologyBackend`.

## Candidatos revisados

### Swiss Ephemeris / pyswisseph

Ventajas:

- cobertura muy orientada a astrología;
- efemérides de alta precisión;
- soporte directo de casas y asteroides;
- amplia implantación en software astrológico.

Riesgo principal:

- `pyswisseph` se publica bajo AGPL-3.0;
- la integración debe evaluarse conjuntamente con la licencia futura del repositorio y, cuando proceda, con la licencia profesional de Swiss Ephemeris.

### pysweph

Es una continuación reciente compatible con el nombre de importación `swisseph`.

A septiembre de 2026 presenta interés por mantenimiento reciente, pero su propia información de publicación ha indicado cambios en funciones de `calc`/`houses`, deprecación temporal de la suite de tests en una revisión de 2026 y una refactorización CFFI en curso. Mantiene las condiciones de licencia derivadas de Swiss Ephemeris.

No se adopta todavía como dependencia base.

### Flatlib

Proporciona abstracciones astrológicas convenientes, pero depende de Swiss Ephemeris. Su propia documentación advierte de las consecuencias de licencia del motor subyacente.

No aporta una separación suficiente respecto del problema de licencia y control del cálculo.

### Skyfield

Ventajas:

- proyecto astronómico activo;
- licencia MIT;
- orientación a posiciones astronómicas de precisión;
- adecuado para verificación independiente de posiciones planetarias.

Limitación:

- no es un motor astrológico integral; casas, sistemas de domificación y otras capas específicas tendrían que implementarse o integrarse por separado.

## Decisión

No añadir todavía ninguna dependencia astronómica obligatoria a `pyproject.toml`.

Se conserva:

`ALMAS → AstrologyBackend → backend concreto`

La arquitectura deberá permitir al menos:

1. un backend de producción capaz de cubrir la geometría astrológica requerida;
2. un backend o método independiente de verificación para posiciones fundamentales cuando resulte viable;
3. fixtures dorados de regresión con resultados conocidos;
4. tolerancias numéricas explícitas;
5. registro del backend y versión utilizados en toda salida canónica.

La eventual adopción de Swiss Ephemeris deberá resolverse junto con la política de licencia del repositorio. Skyfield es un candidato especialmente útil para verificación astronómica independiente, pero no sustituye por sí solo toda la capa astrológica.

## Fuentes consultadas

- PyPI · pyswisseph: https://pypi.org/project/pyswisseph/
- PyPI · pysweph: https://pypi.org/project/pysweph/
- PyPI · Skyfield: https://pypi.org/project/skyfield/
- Flatlib · FAQ/licensing: https://github.com/flatangle/flatlib/blob/master/docs/source/faq.rst
