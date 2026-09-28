# Política de publicación

El repositorio público separa tres clases admisibles de material.

## 1. Material generalizado

Las reglas metodológicas, fórmulas, schemas, ontologías, políticas de fuentes, código reutilizable y documentación pueden publicarse cuando están redactados independientemente de cualquier caso privado identificable.

## 2. Material sintético

Los ejemplos, fixtures, tests unitarios y demostraciones pueden utilizar datos artificiales. El material sintético debe identificarse claramente como tal y no puede ser una copia encubierta, una perturbación ligera o una codificación reversible de un caso real privado.

## 3. Material real público

Un caso real sólo puede incluirse cuando los hechos o datos subyacentes ya sean públicos e independientemente verificables mediante una fuente pública citada. Ese material debe:

- identificar la fuente pública y su procedencia bibliográfica o de recuperación;
- distinguir hechos de fuente, cálculos ALMAS e interpretación;
- permanecer separado del corpus sintético de validación;
- no utilizarse nunca para reajustar umbrales, pesos, gates o reglas ontológicas con el fin de obtener una clasificación deseada.

## Material excluido

El repositorio no debe publicar datos personales no públicos, comunicaciones privadas, datos natales privados, eventos relacionales no publicados, cartas privadas, informes privados ni salidas específicas de casos derivadas de información que no sea ya pública.

El acceso a material privado no lo convierte en público. Un hallazgo metodológico generalizado surgido durante investigación privada sólo puede publicarse después de reformular la regla de forma independiente al caso privado y validarla sin incorporar identificadores ni valores privados.


## Firewall ejecutable de publicación

Desde el Paso 19 esta política se ejecuta mediante `ALMAS_PUBLIC_DATA_ISOLATION_V1`.

Los scopes de artefactos de caso son:

- `examples/` → únicamente `SYNTHETIC`;
- `public_cases/` → únicamente `PUBLIC_VERIFIABLE`;
- `validation/holdouts/` → `SYNTHETIC`, `PUBLIC_VERIFIABLE` o `PUBLIC_METADATA_ONLY`.

Cada scope dispone de un manifiesto exhaustivo. Un JSON no registrado hace fallar el contrato público.

Las clases `PRIVATE_CASE`, `PSEUDONYMIZED_PRIVATE`, `PRIVATE_HOLDOUT` y `CONFIDENTIAL` están prohibidas como artefactos del repositorio.

La pseudonimización no convierte material privado en público.

Los holdouts privados deben permanecer fuera del repositorio. Sólo pueden publicarse referencias externas opacas, protocolos preregistrados y métricas agregadas no identificables.

Véase `docs/PRIVATE_CASE_ISOLATION_POLICY.md`.
