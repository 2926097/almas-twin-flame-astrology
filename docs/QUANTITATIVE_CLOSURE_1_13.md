# ALMAS 1.13.0 · Cierre cuantitativo estructural

## Estado

Documento de evolución en la rama `evolution/1.13.0-quantitative-closure`.

La finalidad de 1.13.0 es retirar entradas numéricas manuales del flujo FULL
cuando puedan derivarse de forma determinista a partir de la evidencia
canónica. Ninguna regla se ajusta a un caso real concreto.

## Fase Q1 · Fuerza automática de raíces

La primera fase cierra el hueco M17 señalado en 1.12.0.

Política canónica:

`ALMAS_ROOT_STRENGTH_BASELINE_V1`

Fórmula conservada:

`S = F × technique_reliability × birth_time_factor × aspect_coefficient`.

La baseline utiliza coeficientes 1.0 de forma deliberada. Esto no afirma que
todas las técnicas tengan la misma validez empírica; evita inventar diferencias
de peso antes de disponer de una calibración externa preregistrada.

La incertidumbre horaria no se penaliza en M17. Se mide en M23 y se integra en
M25, evitando doble penalización.

La agregación de raíz es `MAX_CORE_EVIDENCE`: una raíz estructural adopta la
mayor fuerza de sus evidencias core ya deduplicadas. Una evidencia
`support_only` puede conservar fuerza diagnóstica, pero nunca sustituye
evidencia core ni convierte una raíz en core-eligible.

## Próximas fases

Q2: atribución automática raíz → pilar y cierre de M18.

Q3: atribuciones automáticas por modelo para IDD M21.

Q4: generador de perturbación horaria y parametrización preregistrada para M23.

Q5: cuantificación canónica de ablación, perturbación paramétrica e IDD stability
para M25.

Q6: generadores de universos nulos para M24, manteniendo rareza estructural
separada de IRC y de cualquier probabilidad metafísica.

Q7: actualización del gate FULL, fixtures y release pública 1.13.0.
