# ALMAS · Paso 4: hecho observado y mapeo doctrinal

`dynamic-phase-observation.schema.json` define un registro que separa el hecho fuente (`observed_facts`), el estado descriptivo propuesto (`observed_state`) y la interpretación doctrinal (`doctrinal_mapping`, `doctrinal_status`). La fase descriptiva debe referenciar hechos identificados; el mapeo doctrinal requiere identificador, interpretación, clase de procedencia C/D/E y referencias de fuente. Si no hay mapeo, el estado doctrinal es `NOT_EVALUABLE`.

El ejemplo sintético representa un mensaje que fija un límite. El hecho documental permanece igual aunque se añada una lectura contemporánea como “DF surrender”; la lectura se identifica como D, cita su fuente y no puede sustituir el estado descriptivo `boundary_assertion`. El ejemplo no clasifica un caso personal ni constituye regla de asignación.

La separación aplica el firewall epistemológico ALMAS: C (doctrina explícita), D (uso contemporáneo) y E (hipótesis del proyecto) son procedencias distintas. Una asociación de doctrina con un hecho puede quedar `COMPATIBLE` sin hacer que la doctrina pruebe la fase. Tampoco permite inferir sentimientos, causas, reciprocidad o decisiones futuras. El registro aún no se inserta automáticamente en el canonical; eso queda sujeto a la definición del motor documental/conductual del Paso 5.
