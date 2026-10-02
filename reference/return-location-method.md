# Ubicación e incertidumbre · RRA V1

Cada variante declara birth_location, residence_location, actual_return_location, event_location o unknown. Una ubicación conocida exige coordenadas y fuente; unknown bloquea ángulos y casas. Se conservan todas las variantes predeclaradas y se comparan raíces por ubicación. La longitud planetaria geocéntrica y el instante de retorno no cambian por relocalizar. Una hora natal incierta no se repara escogiendo una ubicación favorable.

Contrato, algoritmos, límites e integración: [relational-return-activation.md](relational-return-activation.md). Fuentes: [auditoría de corpus](../docs/RRA_SOURCE_AUDIT.md). Política: `src/almas_tfa/data/return-*-policy.json`. Validación externa: **NOT_PERFORMED**.
