# ALMAS 1.22.0 · evolución cuantitativa

Esta versión separa explícitamente la evolución matemática de la referencia congelada 1.21.0. `core.py` conserva las fórmulas históricas para regresión y comparación.

## Dependencia entre raíces y motivos PX/PS

A) **Dato calculado.** M17 conserva las raíces independientes y M18 deriva PX/PS como motivos semánticos construidos sobre esas raíces.

B) **Técnica.** M18 publica `pillar_source_roots`. ALMAS 1.22 mide el solapamiento entre dos pilares como la fracción de raíces compartidas respecto del conjunto de procedencia menor. En el núcleo de cada modelo, un pilar recibe peso efectivo inverso a la redundancia acumulada con los demás pilares esenciales. El núcleo se agrega mediante media geométrica ponderada.

El apoyo se pondera además por novedad respecto del núcleo. Si un pilar de apoyo reutiliza totalmente las raíces ya presentes en el núcleo, no vuelve a añadir masa al multiplicador de apoyo.

E) **Hipótesis del proyecto.** Esta corrección controla reutilización estadística de evidencia. No afirma que PX o PS sean metafísicamente menos importantes.

## IRC por familias de dependencia

B) **Técnica.** Los componentes de robustez se agrupan antes de calcular IRC. BIRTH_TIME, ABLATION y los discriminadores validados mantienen familias propias. PARAMETER_PERTURBATION e IDD_STABILITY comparten por defecto `PARAMETER_ENSEMBLE`, porque la implementación Q5 deriva ambos del mismo conjunto de perturbaciones.

Primero se obtiene una media geométrica dentro de cada familia y después una media geométrica entre familias. `R_min` sigue siendo el mínimo de los componentes individuales. De este modo, duplicar una medida correlacionada no crea una dimensión de robustez adicional.

## ICE autónomo

B) **Técnica.** M20 puede derivar ICE cuando la evaluación se declara completa con `counterevidence_assessment_complete=true`. Tras la deduplicación exacta, dentro de cada familia de dependencia se conserva la severidad máxima. Las familias independientes se combinan con una función saturante del complemento del producto de sus severidades residuales.

Un conjunto completo y vacío produce ICE=0. Si existe una contradicción retenida sin severidad, el cálculo autónomo falla cerrado. No se permite declarar simultáneamente ICE autónomo e ICE precomputado.

E) **Hipótesis del proyecto.** ICE es un índice de severidad estructural. No es una probabilidad metafísica ni una probabilidad de que un modelo sea verdadero o falso.

## Invariantes

- 1.21.0 queda preservado como baseline histórico.
- Missingness nunca se convierte en cero salvo ausencia estructural evaluada según contrato.
- Una feature derivada no se trata como una raíz independiente adicional.
- Las contradicciones esenciales continúan vetando `SUPPORTED` con independencia del valor numérico de ICE.
- Temporalidad y rareza nula no entran en IEM.
- IEM, IDD, IRC e ICE siguen siendo índices internos de ALMAS, no probabilidades metafísicas.
