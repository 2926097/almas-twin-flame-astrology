# Presets explícitos de política relacional

## Problema

ALMAS 1.25.0 exige orbes declarados y prohíbe inferirlos en runtime. Esto es
metodológicamente correcto, pero una interfaz no puede presentar una solicitud
como ejecutable si no conserva también la política analítica utilizada.

El registro `ALMAS_RELATIONAL_POLICY_PRESET_REGISTRY_V1` añade perfiles
seleccionables. No convierte ningún preset en default implícito.

## Primer preset

`ALMAS_RELATIONAL_STRICT_RESEARCH_V1` es una baseline experimental de clase
`E_PROJECT_POLICY`. Su finalidad es investigación estructural reproducible,
no codificar un supuesto estándar universal de astrología.

La sinastría tropical conserva los cinco aspectos mayores con una ventana
uniforme de 3.5°. La decisión es deliberadamente estrecha porque el contrato
actual de M03 expresa el orbe por aspecto, no por clase de punto. Astrodienst
documenta que los orbes varían entre escuelas y que Sol/Luna suelen recibir
más margen que otros factores; por ello la uniformidad de 3.5° no se atribuye a
Astrodienst, sino al proyecto. Una herramienta contemporánea de sinastría
revisada bajo metodología de María Blaquier utiliza 3.5° para listar contactos
cruzados, lo que aporta un antecedente de uso, no una validación.

Declinaciones usan 1° en paralelo y contraparalelo. Astrodienst sitúa el
paralelo alrededor de 1° y una guía específica de sinastría de declinaciones
emplea 1°.

Antiscios usan 1° simétrico. Richard Smoot declara 2° aplicando y 1° separando;
como M06 no modela aplicación/separación, ALMAS adopta el límite menor como
decisión conservadora E.

La consonancia compuesta-Davison usa sólo conjunción homóloga a 1°. Es una
regla propia del proyecto: mide repetición posicional del mismo significador
entre ambas cartas relacionales y no pretende ser una doctrina general de
aspectos.

Los cruces dracónicos utilizan conjunción/oposición con máximo 3°, conforme a
la metodología contemporánea atribuida a María Blaquier. Esta capa permanece
corroborativa y dependiente del radix/nodo.

## Selección

El frontend debe enviar de manera explícita:

```json
{
  "analysis_policy_profile": "ALMAS_RELATIONAL_STRICT_RESEARCH_V1"
}
```

Cada resolución calcula además `policy_fingerprint`, un SHA-256 determinista
del objeto de políticas materializado. El fingerprint viaja en la traza del
request y permite detectar cualquier mutación silenciosa bajo un mismo ID.

La selección materializa las cinco políticas de orbe requeridas antes de entrar
en M00-M31. No se considera `implicit_orbs_used` porque la decisión queda
registrada por ID de política.

No se permite combinar el preset con overrides inline de esas mismas políticas.
Para ejecutar una política personalizada, se omite `analysis_policy_profile`
y se declaran las políticas completas en `analysis_policies`.

## Robustez

Seleccionar el preset no elimina la incertidumbre de orbe. M25 conserva su
perturbación preregistrada 0.90/0.95/1.05/1.10 sobre las familias de orbes.
El resultado debe revelar si la clasificación depende de pequeñas variaciones
de la baseline.

## Fuentes y nivel epistemológico

- Astrodienst, *Orb*: P4, contexto técnico sobre variabilidad de orbes.
- Astrodienst, *Parallel*: P4, intervalo técnico para paralelos.
- Cafe Astrology, *Determining Parallels and Contra-Parallels in Synastry*:
  P4, uso contemporáneo explícito de 1°.
- Richard Smoot, *Working with the Antiscia* (Astro.com, 2020): P4, método
  identificado.
- DraconicChart, artículos revisados por María Blaquier (2026): P4/P5 según
  alcance, método contemporáneo para contactos dracónicos estrictos y evidencia
  emic de uso relacional.

Ninguna de estas fuentes valida IEM, LG, twin-flame, origen compartido o
probabilidad metafísica. Los valores agregados que adopta el preset son política
E del proyecto.
