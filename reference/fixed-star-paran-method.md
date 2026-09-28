# Método de estrellas fijas y parans · preregistro ALMAS 1.22

## Estado

Este documento preregistra la capa antes de su implementación ejecutable. La existencia de fuentes no cambia todavía `fixed_stars` de `SOURCE_GAP`.

## Separación de capas

ALMAS distingue tres niveles:

1. **Astronomía calculada (A_CALCULATED):** identidad de la estrella, posición, magnitud, cruces angulares y tiempos de paran producidos por el backend vigente.
2. **Método astrológico (B_TECHNIQUE):** selección, relación estrella–planeta/ángulo, paran y fases conforme a una política explícita y a fuentes identificadas.
3. **Interpretación (E_PROJECT_HYPOTHESIS cuando exceda la fuente):** síntesis ALMAS dentro del informe personal.

Ningún nivel convierte una estrella o paran en evidencia ontológica por sí solo.

## Fuentes de método

`brady_book_fixed_stars_1998` se preregistra como método moderno identificado. Sustenta el uso natal de estrellas fijas y la consideración diferenciada de planetas/orbes, ángulos y parans. No autoriza a ALMAS a inventar un orbe: la política numérica deberá congelarse en F2 antes de ejecutar casos.

`ptolemy_tetrabiblos_1_9_fixed_stars` se registra como antecedente histórico técnico de naturalezas estelares análogas a cualidades planetarias. No es fuente del método moderno de parans.

## Política de ejecución

`ALMAS_FIXED_STAR_PARAN_POLICY_V1` congela antes de implementar el cálculo el canon lógico, las superficies del proveedor, los orbes y el firewall inferencial. El canon operativo es el canon disponible del proveedor 6.8.2, con membresías documentadas Royal, Behenian y Ptolemaic y fingerprint de ejecución obligatorio. Los 4 minutos de paran y 2 minutos de contacto angular se registran como baseline explícita del proveedor, no como una regla atribuida a Brady.

## Backend

La implementación debe reutilizar `moira-astro==6.8.2` a través del backend de producción ya existente. La API del proveedor dispone de superficies de estrellas fijas y parans; ALMAS no añadirá un segundo motor astronómico para esta capa.

## Invariantes previos a F2

- `support_only=true`;
- sin modificación de IEM, IDD, IRC, IAT, raíces o discriminadores;
- canon de estrellas versionado;
- orbes explícitos y versionados;
- procedencia del backend y de los datos estelares conservada;
- parans dependientes de hora/lugar degradan o fallan cerrado cuando faltan datos;
- fixtures exclusivamente sintéticos;
- el router personal permanece `SOURCE_GAP` hasta que cálculo, schema y tests estén completos.
