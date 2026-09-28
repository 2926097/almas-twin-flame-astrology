#!/usr/bin/env python3
from importlib import metadata
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

    if not isinstance(PARAN_POLICY_PRESETS, dict):
        raise AssertionError("PARAN_POLICY_PRESETS debe ser un mapping")
    normalized_preset_keys = {
        str(getattr(key, "value", key)).lower()
        for key in PARAN_POLICY_PRESETS
    }
    if "star_planet_only" not in normalized_preset_keys:
        raise AssertionError(
            "Moira 6.8.2 no expone el preset star_planet_only"
        )

    print("ALMAS astronomy backend runtime contract: PASS")
    print(f"moira-astro: {installed}")
    print("Kernel binding: explicit Moira(kernel_path=...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
