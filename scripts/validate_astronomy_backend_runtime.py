#!/usr/bin/env python3
from importlib import metadata

EXPECTED = "6.8.2"

def main() -> int:
    installed = metadata.version("moira-astro")
    if installed != EXPECTED:
        raise AssertionError(
            f"moira-astro {EXPECTED} requerido; instalado {installed}"
        )

    from moira import HouseSystem, Moira
    from moira.spk_reader import set_kernel_path

    if not callable(Moira):
        raise AssertionError("moira.Moira no es construible")
    if not hasattr(HouseSystem, "PLACIDUS"):
        raise AssertionError("Moira no expone HouseSystem.PLACIDUS")
    if not callable(set_kernel_path):
        raise AssertionError("Moira no expone set_kernel_path")

    required_methods = ("chart", "houses")
    for name in required_methods:
        if not hasattr(Moira, name):
            raise AssertionError(f"Moira no expone {name}()")

    print("ALMAS astronomy backend runtime contract: PASS")
    print(f"moira-astro: {installed}")
    print("Kernel: external/local and fingerprinted; not loaded by this smoke test")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
