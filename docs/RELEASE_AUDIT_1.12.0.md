# Auditoría final de release · ALMAS 1.12.0

**Fecha:** 26 de septiembre de 2026  
**Rama auditada:** `feature/discriminador-ontologico-v1`  
**Base congelada:** `1.11.0` · commit `3fd60b834e83ebf5fa984f81d377fb61fb95170b`  
**Tipo de release:** MINOR compatible hacia atrás  
**Estado:** candidato técnico de release; fusión a `main` fuera de esta auditoría.

## 1. Objeto

ALMAS 1.12.0 incorpora una arquitectura formal para investigar si modelos ontológicos competidores pueden distinguirse sin convertir puntuaciones, intensidad, narrativa o rareza en prueba metafísica.

La release cierra los Pasos 1–20 del proyecto de discriminación ontológica iniciado sobre 1.11.0.

No introduce M32. La discriminación ontológica se integra como subcapa de M21 y utiliza M25 únicamente cuando existe un discriminador L3 previamente autorizado.

## 2. Baseline preservado

Se conserva el baseline 1.11.0 como referencia histórica en `docs/DISCRIMINATOR_BASELINE_1.11.0.md`.

No se modifican silenciosamente:

- fórmulas IEM, IDD, IRC, IAT, ICC o ICE;
- pesos estructurales;
- thresholds del gate `SUPPORTED`;
- pilares AF/KA/AG/LG;
- reglas de dependencia y deduplicación;
- principio de activación temporal;
- política de rareza bajo modelos nulos;
- separación A/B/C/D/E;
- ontología multiaxial general.

## 3. Problema de identificación

1.12.0 formaliza:

- hipótesis operativas `SOULMATE_MODEL`, `MONADIC_ORIGIN`, `SPLIT_SOUL` y `TWIN_FLAME_MODEL`;
- equivalencia observacional;
- estados de identificabilidad;
- separabilidad por pares;
- condiciones necesarias, operacionales suficientes, exclusorias y no discriminantes;
- error `FALSE_SPECIFICITY`;
- fallback obligatorio `SHARED_ORIGIN_UNDIFFERENTIATED / INSUFFICIENT`.

Un score no rompe equivalencia observacional salvo validación independiente previa como discriminador.

## 4. Cadena L1 → L3

La release incorpora:

- registro doctrinal L1;
- candidatos operacionales L2;
- motor lógico autónomo;
- registro canónico de promoción;
- máquina de estados;
- validez discriminante cuantitativa;
- cegamiento/leakage;
- independencia astrológica;
- genealogía documental;
- reporting metodológico.

Cadena de promoción:

`EXPLORATORY → REPRODUCIBLE → REPLICATION_READY → CONFIRMATORY_ELIGIBLE → VALIDATED_DISCRIMINATOR`.

No se permiten saltos ascendentes ni autopromoción durante una ejecución.

## 5. Estado real de los discriminadores

En el cierre de 1.12.0:

- OD01 `EXPLORATORY`;
- OD02 `EXPLORATORY`;
- OD03 `EXPLORATORY`;
- OD04 `EXPLORATORY`;
- OD05 `BLOCKED`;
- OD06 `BLOCKED`;
- OD07 `RETIRED`;
- `validated_discriminator_ids=[]`;
- ningún registro tiene `l3_authorized=true`.

Por tanto, la release contiene infraestructura L3, pero ningún discriminador ontológico real L3 utilizable.

## 6. M21, M25 y canonical

M21 conserva IDD AF/KA/AG/LG y añade una subcapa ontológica independiente.

La entrada exploratoria no puede modificar la decisión confirmatoria.

M25 sólo acepta `VALIDATED_DISCRIMINATOR` cuando la raíz procede de una separación M21 `SEPARABLE_VALIDATED` y cumple los gates de promoción aplicables.

`ontological_discrimination` forma parte del contrato canónico y `promotion_trace` se conserva hasta reporting.

## 7. Controles adversariales y metamórficos

La release comprueba, entre otros:

- flooding L1/L2;
- duplicación de una misma raíz;
- conflictos L3;
- ciclos globales de exclusión;
- invariancia frente a reordenamiento;
- inversión de orientación de pares;
- idempotencia;
- equivalencias L3 completas;
- intentos de reutilización de `promotion_ref`;
- autoetiquetas y narrativa;
- rareza astrológica;
- activación temporal;
- eliminación exploratoria de todos los modelos.

Estas pruebas evalúan resistencia operacional del software, no verdad ontológica.

## 8. Astrología como discriminador

Si `uses_astrology=true`, L3 exige además:

- criterio externo no astrológico;
- ablación astrológica;
- controles emparejados;
- auditoría de dependencia;
- evaluación fuera de muestra;
- replicación específica.

Un aspecto, asteroide, atacir, sincronía o recurrencia aislada no autoriza L3.

La rareza bajo un modelo nulo no es probabilidad metafísica y la temporalidad no demuestra origen.

## 9. Validez discriminante y cegamiento

`ALMAS_DISCRIMINANT_VALIDATION_V1` exige por par:

- CI95 inferior de sensibilidad ≥ 0.60;
- CI95 inferior de especificidad ≥ 0.90;
- balanced accuracy ≥ 0.75;
- CI95 superior de `FALSE_SPECIFICITY_RATE` ≤ 0.05;
- falsa especificidad sintética/adversarial = 0.

`ALMAS_BLINDING_LEAKAGE_V1` exige:

- `STEP_A_BLINDED`;
- `STEP_B_DOCUMENTARY_REVEAL`;
- fingerprints estructurales pre/post idénticos;
- `LABEL_LEAKAGE=0`;
- `NARRATIVE_LEAKAGE=0`;
- `CASE_FITTING=0`;
- cero cambios post-holdout.

Estos umbrales son `E_PROJECT_POLICY`.

## 10. Genealogía y doctrina

OD01–OD07 disponen de genealogía documental canónica.

La genealogía conserva:

- prioridad P1–P6;
- tradición;
- autor;
- obra;
- fecha;
- ancla;
- `supports[]`;
- `does_not_support[]`;
- relaciones doctrinales requeridas;
- equivalencias prohibidas;
- techo epistemológico.

Cantidad o prioridad de fuentes no añade peso ontológico.

## 11. Privacidad

`ALMAS_PUBLIC_DATA_ISOLATION_V1` separa:

- `SYNTHETIC`;
- `PUBLIC_VERIFIABLE`;
- `PUBLIC_METADATA_ONLY`.

Quedan prohibidos como artefactos públicos:

- `PRIVATE_CASE`;
- `PSEUDONYMIZED_PRIVATE`;
- `PRIVATE_HOLDOUT`;
- `CONFIDENTIAL`.

`examples/manifest.json` registra 18 fixtures sintéticos.

`public_cases/manifest.json` permanece vacío.

`validation/holdouts/manifest.json` permanece vacío.

Los holdouts privados deben residir fuera del repositorio.

## 12. Cobertura automatizada

La suite de cierre contiene **266 tests deterministas** y una ejecución FULL sintética M00–M31.

Se ejecutan en Python 3.10 y 3.12.

El contrato público comprueba, entre otros:

- sincronía SemVer;
- schemas y manifests;
- estados de promoción;
- gates L3;
- validez discriminante;
- blinding/leakage;
- genealogía;
- privacidad;
- pipeline M00–M31;
- fuentes y ontología;
- fixtures sintéticos.

## 13. Limitaciones que permanecen abiertas

### Backend astronómico

M02 natal y M08 Davison mantienen contratos ejecutables con backend inyectable, pero la selección/implantación del backend astronómico de producción sigue pendiente.

### Holdout externo

No se ha ejecutado un holdout externo real preregistrado.

### L3 real

No existe ningún `VALIDATED_DISCRIMINATOR` real.

### Validez metafísica

La validación del clasificador operacional no equivale a validar una ontología metafísica.

### Rendering

M31 produce el modelo documental; DOCX/PDF material pertenece a la capa posterior de authoring/rendering.

## 14. Criterios finales de release

1. `VERSION`, `pyproject.toml`, skills, manifests y fixtures públicos deben coincidir en 1.12.0.
2. `Núcleo Python` debe concluir `SUCCESS` en Python 3.10 y 3.12 sobre el HEAD final.
3. `Contrato público` debe concluir `SUCCESS` sobre el mismo HEAD.
4. La PR debe permanecer fusionable.
5. `validated_discriminator_ids` debe seguir vacío salvo evidencia L3 real incorporada mediante el protocolo completo.
6. No debe existir material privado en el repositorio público.
7. No debe alterarse el baseline 1.11.0 histórico.

## 15. Decisión

La arquitectura implementada es coherente con una release minor 1.12.0: amplía capacidad metodológica y de validación sin cambiar las fórmulas estructurales públicas ni declarar una validación ontológica inexistente.

La rama puede considerarse técnicamente preparada para 1.12.0 cuando los workflows finales del HEAD de release satisfagan los criterios anteriores.

La fusión a `main`, creación del tag `v1.12.0` y publicación de GitHub Release quedan fuera de este Paso 20 y requieren acciones posteriores explícitas.
