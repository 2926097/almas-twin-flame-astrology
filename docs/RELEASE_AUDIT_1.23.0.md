# Auditoría de release ALMAS 1.23.0

**Versión objetivo:** 1.23.0  
**Base:** ALMAS 1.22.0  
**Rama de trabajo:** `codex/almas-1.23-chiron-nodes`  
**Alcance:** Chiron–Nodal Integration Engine personal y temporal  
**Estado:** verificación local completa; sin publicar.

## Invariantes de alcance

La extensión mantiene `personal_temporal_complexes[]` opcional y admite canonical personal legacy. No altera IEM, IDD, IRC, ICC, ICE, PX, PS, IAT, M18 `WOUND_REPAIR`, discriminadores ni ontología relacional. El Mean Node se atribuye al método técnico registrado de Meeus §47.7; la lectura “Mean estructural / True fenoménico” permanece E no validada.

`INTEGRATION_WINDOW` requiere arquitectura, secuencia con evidencia y dos grupos de dependencia. `INTEGRATION_DOCUMENTED` requiere adicionalmente evento M27 con calidad documental y precisión contractual, fuente y separación entre hecho e interpretación. Solver y convergencia temporal no generan predicciones, scores ni probabilidades metafísicas.

## Resultados de pruebas

Suite completa `PYTHONPATH=src:_testdeps python -m unittest discover -s tests`: **728 tests, PASS**, 68.851 s.
Validador `PYTHONPATH=src:_testdeps python scripts/validate_public_contract.py`: **PASS**; paquete y contrato 1.23.0, 32 módulos, 2 discriminadores registrados y 77 fuentes.
La suite incluye schemas y el ejemplo sintético Chiron–Nodal. Se corrigió el inventario esperado de ejemplos públicos de 24 a 25.

## Limitaciones

Verificaciones ejecutadas localmente; no se han lanzado workflows remotos ni matrices Python 3.10/3.12. Gates de publicación: DOCX **6 tests PASS** y fixture generado; PDF **4 tests PASS**, preflight B5 PASS y smoke render de **13 páginas**. La suite interna verifica implementación, contratos e invariantes sintéticos. No constituye validación científica de astrología ni de hipótesis metafísicas. El solver requiere un evaluador apropiado para cada técnica y su capacidad de detectar todas las raíces depende del paso de muestreo declarado.
