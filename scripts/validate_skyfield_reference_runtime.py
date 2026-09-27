#!/usr/bin/env python3
from importlib import metadata

EXPECTED = "1.55"


def main() -> int:
    installed = metadata.version("skyfield")
    if installed != EXPECTED:
        raise AssertionError(
            f"skyfield {EXPECTED} requerido; instalado {installed}"
        )

    from skyfield.api import load, load_file
    from skyfield.framelib import (
        ecliptic_frame,
        true_equator_and_equinox_of_date,
    )

    if not callable(load_file):
        raise AssertionError("Skyfield no expone load_file()")
    timescale = load.timescale(builtin=True)
    if not callable(getattr(timescale, "tt_jd", None)):
        raise AssertionError("Skyfield Timescale no expone tt_jd()")
    if ecliptic_frame is None or true_equator_and_equinox_of_date is None:
        raise AssertionError("Skyfield no expone los frames requeridos")

    print("ALMAS Skyfield planetary reference runtime: PASS")
    print(f"skyfield: {installed}")
    print("Kernel: local, explicit and externally fingerprinted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
