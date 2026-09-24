# ALMAS · Arquitectura modular única

## Decisión arquitectónica

ALMAS se publica y versiona como **una única skill**.

Los motores especializados —astrología relacional, doctrina, ontología, contrato preencarnatorio, roles, causalidad, temporalidad, validación e informes— son **módulos internos** de la misma metodología.

No existe una segunda skill pública de “Contrato Álmico”.

El archivo `skills/almas-soul-contract/SKILL.md` se conserva como punto de entrada especializado y por compatibilidad histórica, pero su estatus normativo es **módulo**, no skill independiente.

## Flujo canónico

```text
FUENTES + DATOS
      ↓
ASTROLOGÍA METAFÍSICA RELACIONAL
      ↓
canonical_analysis.json
      ↓
ONTOLOGÍA + DIAGNÓSTICO DIFERENCIAL
      ↓
RECONSTRUCCIÓN PREENCARNATORIA
  ├─ origen
  ├─ motivo del acuerdo
  ├─ roles
  ├─ condiciones de encuentro
  ├─ tareas individuales
  ├─ tarea común
  ├─ cláusulas
  └─ mecanismos de cumplimiento
      ↓
VALIDACIÓN
  ├─ dependencia
  ├─ contraevidencia
  ├─ ablación
  ├─ sensibilidad horaria
  └─ robustez
      ↓
canonical_soul_contract.json
      ↓
INFORME HERMENÉUTICO
```

## Regla de versionado

`VERSION` en la raíz es la única versión pública de ALMAS.

Los módulos pueden tener:

- `schema_version`;
- `engine_revision`;
- `manifest_version`.

No pueden declararse como una segunda skill con SemVer público independiente.

## Separación epistemológica

Cada afirmación debe conservar su procedencia:

- A · DATO CALCULADO/documental.
- B · TÉCNICA.
- C · DOCTRINA explícita.
- D · USO CONTEMPORÁNEO.
- E · HIPÓTESIS DEL PROYECTO.

Las fuentes definen qué conceptos existen doctrinalmente y qué significan. La astrología evalúa si una arquitectura operacionalizada aparece. Una fuente nunca añade puntos por existir.

## Regla de desarrollo

Toda nueva función sigue:

`fuente/problema → definición → evidencia necesaria → límites → regla reproducible → test sintético → validación → incorporación`.

Los casos privados pueden descubrir problemas metodológicos, pero no se publican ni se convierten directamente en reglas sin generalización y test.
