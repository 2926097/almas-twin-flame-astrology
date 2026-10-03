# Método de estrellas fijas y parans · preregistro ALMAS 1.22

## Estado

F1 registró las fuentes y F2 congeló una capacidad de cálculo opcional sobre `MoiraProductionBackend`. La presencia de fuentes o de resultados calculables no cambia por sí sola `fixed_stars` de `SOURCE_GAP`; la capa de informes y el router siguen pendientes de F3/F4.

## Separación de capas

ALMAS distingue tres niveles:

1. **Astronomía calculada (A_CALCULATED):** identidad de la estrella, posición, magnitud, cruces angulares y tiempos de paran producidos por el backend vigente.
2. **Método astrológico (B_TECHNIQUE):** selección, relación estrella–planeta/ángulo, paran y fases conforme a una política explícita y a fuentes identificadas.
3. **Interpretación (E_PROJECT_HYPOTHESIS cuando exceda la fuente):** síntesis ALMAS dentro del informe personal.

Ningún nivel convierte una estrella o paran en evidencia ontológica por sí solo.

## Fuentes de método

`brady_book_fixed_stars_1998` se preregistra como método moderno identificado. Sustenta el uso natal de estrellas fijas y la consideración diferenciada de planetas/orbes, ángulos y parans. No autoriza a ALMAS a atribuirle los umbrales operativos del adaptador.

`ptolemy_tetrabiblos_1_9_fixed_stars` se registra como antecedente histórico técnico de naturalezas estelares análogas a cualidades planetarias. No es fuente del método moderno de parans.

## Política de ejecución

`ALMAS_FIXED_STAR_PARAN_POLICY_V1` congela las superficies públicas de `moira-astro==6.8.2`, el canon disponible, su fingerprint, los orbes, la delimitación del día y el firewall inferencial. Los parans se buscan en la ventana del día UT según `find_parans`; los contactos angulares se mantienen como eventos separados cercanos al instante natal. Los 4 minutos para parans y 2 minutos para contactos son valores explícitos de la política ALMAS basados en los defaults documentados del proveedor, no reglas atribuidas a Brady o Ptolomeo.

## Backend

La capacidad opcional `FixedStarParanBackend` se implementa en `MoiraProductionBackend`. Usa `Moira.fixed_star`, `moira.facade.list_paran_stars`, `moira.facade.find_parans` y `moira.facade.natal_angular_contacts`. No añade otro backend ni hace llamadas de red o geocodificación.

## Invariantes de F2

- `support_only=true`;
- sin modificación de IEM, IDD, IRC, IAT, raíces o discriminadores;
- canon normalizado y fingerprint obligatorio por ejecución;
- esquema cerrado para política y resultado, con provenance del motor/kernel y de cada estrella;
- ausencia de hora, zona horaria o coordenadas válidas produce un error no evaluable, sin fallback;
- cualquier respuesta parcial o evento fuera de contrato falla cerrada;
- fixtures sintéticos sin datos personales;
- `SUPPORT_ONLY`: sin scoring, raíces, discriminadores ni inferencia ontológica;
- el router personal pasa a `SUPPORTED` para atribución técnica tras integrar F3–F4; este estado no valida eficacia astrológica.

## Capa personal F3–F4

Una solicitud natal puede activar `fixed_stars: {"enabled": true}`. El pipeline reutiliza Moira, exige hora A/B, conserva canon, geometría y procedencia, y elimina metadata natal y relojes julianos absolutos de la salida personal. La capa entra en `secondary_layers.fixed_stars` y en la sección P08 del modelo documental. El renderer técnico conserva resultados negativos y diferencia el método moderno de Brady del antecedente histórico de Ptolomeo; no inventa lecturas individuales de estrellas sin pasajes. La autoría posterior usa esos datos canónicos y fuentes ya registrados, sin mutar el canonical.
