# Auditoría SSAR · fase 6 · 2026-10-02

La fase 6 del plan 1.25.0 R2 incorpora una API auxiliar optativa de Vertex/Anti-Vertex y dos variantes de Luna Negra. La versión pública sigue en 1.24.1. El trabajo se mantiene en la [PR #84 en borrador](https://github.com/2926097/almas-twin-flame-astrology/pull/84), sin release ni integración canónica/M27.

## Resultado y convenciones

El cálculo propio de Vertex obtiene la intersección occidental eclíptica/vertical primario con ARMC, latitud y oblicuidad verdadera. Trata explícitamente el ecuador, ambos hemisferios y las singularidades. Vertex y Anti-Vertex comparten un eje y una clase de equivalencia, conservando las longitudes y aspectos dirigidos originales. La continuidad de ese eje durante un cambio de polo se comprueba con perturbaciones horarias.

La media es una variante escalar identificada: argumentos IERS 2003 `F + Ω − l + 180° + Δψ`. No equivale al apogeo de órbita media proyectado Moshier/Swiss. La osculante se calcula con el vector excéntrico del estado simultáneo lunar geocéntrico inercial, GM Tierra+Luna DE440 y rotación posterior a la eclíptica verdadera de fecha. No se usa una velocidad de un marco rotante. La etiqueta «true» no otorga superioridad interpretativa.

El proveedor auxiliar exige Skyfield 1.55, DE440 local y SHA-256 comprobado. Declara TT, GAST/UT1, modelo temporal incluido en Skyfield, ICRF, origen, unidades y matrices de fecha. La conversión de hora civil natal y la construcción de los contextos de carta no se inventan aquí. La ausencia de fuente, precisión, estado lunar, rotación o malla queda bloqueada. El cálculo no sustituye a Lilith 1181.

Cada contacto genera siempre los cuatro puntos. Ambas variantes lunares mantienen calificación, separación y discrepancias visibles; `selected_variant` permanece null. Se agrupan conservadoramente por familia de cálculo incluso entre sujetos o técnicas. No se establece independencia estadística, fuerza numérica, ranking o nuevo complejo. La función de encuentro del eje y la función de sombra/deseo/autonomía/tabú/vacío de Luna Negra siguen siendo E.

## Fuentes y alcance epistémico

La [auditoría de fuentes](../reference/ssar-calculated-points-source-audit.json) registra documentación primaria Swiss Ephemeris, IERS TN32 y NASA/JPL, con localizadores, prioridad, alcance técnico B y límites. Moira 6.8.2 se documenta como antecedente de implementación consultado, sin contarlo como autoridad independiente. Las reglas semánticas y metodológicas propias se mantienen en E; no se atribuyen a las fuentes técnicas. La matemática reproducida es dato calculado A, sin promoción ontológica.

La procedencia suministrada por el llamador es declarativa: los metadatos de una solicitud no autentican una fuente natal o un kernel. El proveedor sí verifica su archivo y el protocolo de precisión fija el hash exacto de DE440s. El ejemplo usa estados analíticos y targets fabricados; su hash nulo se declara sintético. El recibo de precisión usa épocas estándar y estados públicos DE440, sin datos de personas reales ni material privado.

## Verificación ejecutada

En Python 3.12.14, la suite completa pasa **989 pruebas**, incluidas **54 nuevas**: 18 de geometría, 32 de contratos/SSAR y 4 de configuración del proveedor. La [matriz](../reference/ssar-phase6-test-matrix.json) enumera cada prueba y los ejes cubiertos. Se prueban los cuatro puntos con contacto positivo, negativo y bloqueado, anclajes ausentes, robustez insuficiente, entradas incompletas, marcos/unidades inválidos, degeneraciones, fuentes técnicas incompletas, discrepancias entre variantes, referencias rotas y manipulación de la salida. La ruta desactivada funciona sin extras.

Las **67 comparaciones vivas** pasan con tolerancia fija de desarrollo **10⁻⁷ grados**: 35 de Vertex con Swiss Ephemeris 2.10.03 mediante pyswisseph 2.10.3.2; 12 de argumentos medios con ERFA/SOFA mediante pyerfa 2.0.1.5; 20 osculantes con CSPICE N0067 mediante SpiceyPy 8.0.2. Se utilizan entradas idénticas en cada comparación y DE440s con SHA-256 `c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2`. La tolerancia no se ha relajado para obtener PASS. El [recibo completo](../validation/ssar/calculated-points-precision.receipt.json) conserva versiones, entradas y diferencias.

| Algoritmo | Comparaciones | Diferencia máxima, grados |
| --- | ---: | ---: |
| Vertex | 35 | 1,000444171950221 × 10⁻¹⁰ |
| Media escalar | 12 | 2,3845814212108962 × 10⁻¹¹ |
| Osculante inercial | 20 | 7,673861546209082 × 10⁻¹³ |

El acuerdo de algoritmos sobre entradas idénticas no constituye validación independiente de la efeméride, conversión temporal o interpretación. Las singularidades y casos adversos están en las pruebas de geometría; no se eliminan para redefinir la tolerancia. La política es de desarrollo y no reemplaza la congelación confirmatoria pendiente de fase 9.

El fixture se reproduce con `scripts/validate_ssar_calculated_points.py`; el contrato público pasa con y sin extras mediante `python -S`. `scripts/validate_ssar_baseline.py` confirma salidas deterministas y archivos protegidos idénticos. Se han comparado también todas las definiciones previas de contrato: sólo se añaden ocho definiciones F6, sin modificar las anteriores. Pasan la revisión de formato y la auditoría pública de los 30 ejemplos sintéticos registrados.

CI conserva los tres workflows existentes, con Python 3.10/3.12 donde corresponde. El workflow del núcleo reproduce también el nuevo fixture y el astronómico añade la comparación viva de puntos calculados en ambas versiones, con hash fijado y recibos adjuntos. Las referencias de validación son extras opcionales, separados de la matemática ejecutable.

## Trabajo pendiente

El resultado sigue siendo auxiliar post-core, parcial y no canónico. No altera adaptador core, scoring, índices, ontología, discriminadores, políticas anteriores o versión. Los alcances temporal/documental permanecen sin evaluación de esta capa. Fases 7–10: lotes, M27/integración, controles/congelación y ensamblaje canónico. La validación externa permanece `NOT_PERFORMED`.
