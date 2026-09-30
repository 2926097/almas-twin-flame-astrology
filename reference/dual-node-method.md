# Contrato metodológico dual-node

## Definiciones de implementación

`TRUE_NODE` representa el nodo lunar ascendente instantáneo según el provider astronómico configurado por ALMAS. El nodo descendente se deriva como antipodal. El método actual de producción conserva el contrato `ALMAS_PRODUCTION_ASTRONOMY_BACKEND_V1` y sus datos de procedencia.

`MEAN_NODE` es una serie media secular independiente de la posición True. La implementación ALMAS declara `MEEUS_MEAN_ASCENDING_NODE_1998_47_7`, el polinomio de longitud media del nodo ascendente lunar indicado por Jean Meeus, *Astronomical Algorithms*, 2.ª ed. (1998), §47, ecuación 47.7, evaluado con JD TT. El nodo descendente medio se deriva añadiendo 180°. La derivada del mismo polinomio aporta velocidad media. La referencia no convierte esta fórmula en consenso único de todas las escuelas astrológicas.

Cada punto conserva `node_variant`, `nodal_axis_id`, `calculation_method` y escala temporal. True y Mean son variantes del mismo eje, no raíces independientes. Norte y Sur son extremos de cada variante, tampoco raíces separadas. Las comparaciones de timing requieren objetivo, aspecto y orbe declarados; sin ellos la concordancia es `NOT_EVALUABLE`.

## Estados de concordancia

`DUAL_CONVERGENCE` indica que ambas variantes caen dentro del orbe declarado del mismo objetivo y aspecto. `TRUE_DOMINANT` o `MEAN_DOMINANT` indica que solo esa variante cumple la regla declarada. `DIVERGENT_TIMING` indica que ninguna la cumple bajo esa regla. `NOT_EVALUABLE` indica que falta alguno de los datos de comparación. Estos estados comparan timing, no ontología ni fuerza espiritual.

## Hipótesis de interpretación

La asociación “Mean Node = vector estructural de fondo” y “True Node = modulación fenoménica/oscilatoria” se registra exclusivamente como `E_PROJECT_HYPOTHESIS`. El cálculo astronómico no valida por sí solo dicha interpretación. Sensibilidad, ablación, preregistro y validación fuera de muestra son requisitos antes de cualquier promoción.
