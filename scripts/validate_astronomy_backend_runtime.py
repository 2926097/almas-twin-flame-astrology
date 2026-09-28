#!/usr/bin/env python3
from importlib import metadata
from collections.abc import Mapping
import inspect

EXPECTED = "6.8.2"


def main() -> int:
    installed = metadata.version("moira-astro")
    if installed != EXPECTED:
        raise AssertionError(
            f"moira-astro {EXPECTED} requerido; instalado {installed}"
        )

    from moira import HouseSystem, Moira
    from moira.facade import (
        PARAN_POLICY_PRESETS,
        list_paran_stars,
        natal_angular_contacts,
        natal_parans,
    )

    if not callable(Moira):
        raise AssertionError("moira.Moira no es construible")
    if "kernel_path" not in inspect.signature(Moira).parameters:
        raise AssertionError(
            "Moira debe aceptar kernel_path explícito en el constructor"
        )
    if not hasattr(HouseSystem, "PLACIDUS"):
        raise AssertionError("Moira no expone HouseSystem.PLACIDUS")

    required_methods = ("chart", "houses", "fixed_star", "parans")
    for name in required_methods:
        if not hasattr(Moira, name):
            raise AssertionError(f"Moira no expone {name}()")

    fixed_star_params = inspect.signature(Moira.fixed_star).parameters
    if not {"name", "dt"}.issubset(fixed_star_params):
        raise AssertionError(
            "Moira.fixed_star debe aceptar name y dt"
        )

    parans_params = inspect.signature(Moira.parans).parameters
    for name in ("natal_dt", "latitude", "longitude", "orb_minutes"):
        if name not in parans_params:
            raise AssertionError(
                f"Moira.parans no expone parámetro requerido: {name}"
            )

    canon_params = inspect.signature(list_paran_stars).parameters
    if not {"tiers", "available_only"}.issubset(canon_params):
        raise AssertionError(
            "list_paran_stars debe aceptar tiers y available_only"
        )

    natal_paran_params = inspect.signature(natal_parans).parameters
    for name in ("bodies", "natal_jd", "lat", "lon", "orb_minutes", "policy"):
        if name not in natal_paran_params:
            raise AssertionError(
                f"natal_parans no expone parámetro requerido: {name}"
            )

    angular_params = inspect.signature(natal_angular_contacts).parameters
    for name in ("bodies", "natal_jd", "lat", "lon", "orb_minutes"):
        if name not in angular_params:
            raise AssertionError(
                "natal_angular_contacts no expone parámetro requerido: "
                + name
            )

    preset_tokens: set[str] = set()
    if isinstance(PARAN_POLICY_PRESETS, Mapping):
        candidates = list(PARAN_POLICY_PRESETS.keys()) + list(
            PARAN_POLICY_PRESETS.values()
        )
    else:
        try:
            candidates = list(PARAN_POLICY_PRESETS)
        except TypeError as exc:
            raise AssertionError(
                "PARAN_POLICY_PRESETS debe ser iterable"
            ) from exc

    for candidate in candidates:
        preset_tokens.add(str(candidate).lower())
        for attr in ("name", "value", "id", "preset_id"):
            value = getattr(candidate, attr, None)
            if value is not None:
                preset_tokens.add(str(value).lower())

    if not any("star_planet_only" in token for token in preset_tokens):
        raise AssertionError(
            "Moira 6.8.2 no expone el preset star_planet_only"
        )

    print("ALMAS astronomy backend runtime contract: PASS")
    print(f"moira-astro: {installed}")
    print("Kernel binding: explicit Moira(kernel_path=...)")
    print(
        "Paran preset container: "
        + type(PARAN_POLICY_PRESETS).__name__
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
