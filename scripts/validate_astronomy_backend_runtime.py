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

    if not callable(Moira):
        raise AssertionError("moira.Moira no es construible")
    if "kernel_path" not in inspect.signature(Moira).parameters:
        raise AssertionError(
            "Moira debe aceptar kernel_path explícito en el constructor"
        )
    if not hasattr(HouseSystem, "PLACIDUS"):
        raise AssertionError("Moira no expone HouseSystem.PLACIDUS")

    required_methods = ("chart", "houses")
    for name in required_methods:
        if not hasattr(Moira, name):
            raise AssertionError(f"Moira no expone {name}()")

    print("ALMAS astronomy backend runtime contract: PASS")
    print(f"moira-astro: {installed}")
    print("Kernel binding: explicit Moira(kernel_path=...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
