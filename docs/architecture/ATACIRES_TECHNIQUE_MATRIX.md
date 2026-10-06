# ALMAS · Autoridad por técnica Atacires

El inventario se refiere a las revisiones congeladas del plan R1. Un nombre igual no demuestra equivalencia matemática.

| Capacidad | ALMAS vigente | Atacires fuente | Decisión |
|---|---|---|---|
| Ciclo uniforme C-N y todas sus vueltas | M26 consume señales declaradas; solver genérico sin mapa C-N propio | `engine.py`, solución analítica con año convencional y sentido explícitos | NEW_CAPABILITY: núcleo uniforme interno en SHADOW |
| Búsqueda de perfecciones | `temporal_perfection_solver.py`, evaluador inyectado, límites y tolerancias declarados | `contacts.py`, secundaria/arco con Swiss, muestreo de estaciones no exhaustivo | AUTHORITATIVE: conservar solver ALMAS; migración del evaluador DEFERRED |
| Progresiones secundarias | Vocabulario TPROG y variantes; no confundir señales suministradas con generación astronómica | `techniques.py`: un día de efemérides por año convencional, directo/converso | DEFERRED: cerrar evaluador Moira/JPL y diferencial antes de habilitar |
| Arco solar | Vocabulario TDIR y solver genérico | `techniques.py`: diferencia solar firmada, posiciones natales rotadas | DEFERRED: convenciones y casos límite no reconciliados |
| Retornos | `return_activation.py`, backend y CLI RRA | `SOLAR_RETURN_CYCLE` con retorno ordinal y ubicación | AUTHORITATIVE: RRA; no migrar ni declarar equivalencia |
| Direcciones primarias | No asignar soporte por vocabulario genérico de direcciones | `PRIMARY_MERIDIAN` restringida, claves y rango propios | DEFERRED: no equivale a direcciones primarias generales |
| MCP | Sin necesidad de transporte para cálculo interno | FastMCP SDK 1.18.0 y servicio HTTP | DEFERRED: fachada externa independiente |
| Swiss | Extras previos de validación y VED | Dependencia obligatoria del servicio fuente | No nuevo provider ni extra Atacires; el núcleo uniforme no lo importa |

Los enlaces del ciclo uniforme a raíces relacionales son activaciones de extremo de un sujeto. No se calculan contactos entre posiciones dirigidas de A y posiciones de B en esta revisión. Las ventanas por orbe son convencionales y no anuncian sucesos.
