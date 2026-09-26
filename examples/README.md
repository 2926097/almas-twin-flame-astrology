# Ejemplos

Los ejemplos predeterminados de este directorio son **sintéticos**.

Sus valores son fixtures artificiales diseñados para ejercitar las interfaces públicas y las pruebas de regresión. No representan, aproximan ni codifican una relación privada identificable, una carta natal real ni una historia biográfica privada.

Si en el futuro se añade un ejemplo real, debe situarse en un corpus de casos públicos claramente identificado y cumplir `docs/PUBLICATION_POLICY.md`: los datos subyacentes deben ser ya públicos, independientemente verificables y estar citados.

## Reconstrucción preencarnatoria

`preincarnation-reconstruction.synthetic.json` es un fixture completamente sintético de las ocho etapas del Contrato Preencarnatorio. Demuestra origen, motivo del acuerdo, roles, condiciones de encuentro, tareas individuales, tarea común, cláusulas y mecanismos de cumplimiento sin codificar ninguna relación real.

## Diferencial de origen del alma

`origin-differential.synthetic.json` demuestra el motor diferencial de origen con modelos competidores, discriminadores doctrinales, dimensiones astrológicas y el fallback explícito `SHARED_ORIGIN_UNDIFFERENTIATED`. Es completamente sintético.


## Manifiesto obligatorio

Todos los JSON de este directorio, salvo el propio manifiesto, deben aparecer exactamente una vez en `examples/manifest.json`.

Cada entrada debe permanecer clasificada como `SYNTHETIC` y declarar:

- `contains_real_person_data=false`;
- `contains_nonpublic_material=false`;
- `derived_from_private_case=false`;
- `reversible_from_private_case=false`.

Un ejemplo no puede convertirse en “sintético” mediante una perturbación ligera de un caso privado.
