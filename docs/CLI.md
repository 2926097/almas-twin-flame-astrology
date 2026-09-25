# Interfaz de puntuación por línea de comandos

La CLI pública trabaja con **valores de pilares ALMAS precomputados**. Deliberadamente no calcula efemérides, sinastría ni raíces de evidencia.

## Instalación

```bash
python -m pip install -e .
```

## Ejecución

```bash
almas-score examples/precomputed-pillars.json
```

Para escribir el resultado en un archivo:

```bash
almas-score examples/precomputed-pillars.json -o result.json
```

Invocación equivalente como módulo:

```bash
python -m almas_tfa.cli examples/precomputed-pillars.json
```

## Entrada

El contrato de entrada está definido por `schemas/precomputed-pillars.schema.json`.

El objeto principal es `pillars`, con porcentajes de 0 a 100:

- `PA`: afinidad estructural;
- `PK`: continuidad kármica;
- `PE`: espejo/complementariedad;
- `PR`: coherencia relacional;
- `PX`: recurrencia independiente;
- `PT`: transformación/integración;
- `PS`: misión/servicio;
- `PU`: singularidad diádica experimental.

Los campos opcionales incluyen ICE por modelo, ICC, IRC, R_min, banderas de contradicción esencial y mapas de atribución de raíces para IDD.

## Salida

El contrato de salida está definido por `schemas/precomputed-result.schema.json`.

Para AF, KA, AG y LG la CLI devuelve:

- CORE normalizado;
- SUPPORT;
- IEM antes de contraevidencia;
- ICE;
- IEM final;
- evaluabilidad esencial;
- si se cumple el gate `SUPPORTED` congelado cuando se suministran ICC/IRC/R_min.

El IDD por pares sólo se produce para pares de modelos con mapas de atribución suministrados.

## Límite de alcance

La CLI consume pilares **ya calculados**. No infiere que esos pilares sean válidos. El pipeline astronómico/de evidencia de ALMAS debe suministrarlos conforme a las reglas de dependencia y procedencia definidas en `SKILL.md`.
