# Command-line scoring interface

The public v1.0.0 CLI works on **precomputed ALMAS pillar values**. It deliberately does not calculate ephemerides, synastry or evidence roots.

## Install

```bash
python -m pip install -e .
```

## Run

```bash
almas-score examples/precomputed-pillars.json
```

Write the result to a file:

```bash
almas-score examples/precomputed-pillars.json -o result.json
```

Equivalent module invocation:

```bash
python -m almas_tfa.cli examples/precomputed-pillars.json
```

## Input

The input contract is defined by `schemas/precomputed-pillars.schema.json`.

The principal object is `pillars`, using percentages from 0 to 100:

- `PA`: afinidad estructural;
- `PK`: continuidad kármica;
- `PE`: espejo/complementariedad;
- `PR`: coherencia relacional;
- `PX`: recurrencia independiente;
- `PT`: transformación/integración;
- `PS`: misión/servicio;
- `PU`: singularidad diádica experimental.

Optional fields include per-model ICE, ICC, IRC, R_min, essential-contradiction flags and root-attribution maps for IDD.

## Output

The output contract is defined by `schemas/precomputed-result.schema.json`.

For each of AF, KA, AG and LG the CLI returns:

- normalized CORE;
- SUPPORT;
- IEM before counterevidence;
- ICE;
- final IEM;
- essential evaluability;
- whether the frozen `SUPPORTED` gate is met when ICC/IRC/R_min are supplied.

Pairwise IDD is produced only for model pairs with supplied attribution maps.

## Important scope boundary

The CLI consumes **already calculated** pillars. It does not infer that those pillars are valid. A future verified astronomical/evidence pipeline must supply them under the dependency and provenance rules defined in `SKILL.md`.
