"""Adquirir la ventana pública con validación previa y escritura atómica."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlopen
from observatorio import validate

BASE = "https://raw.githubusercontent.com/2926097/almas-twin-flame-astrology/main/data/public-asteroid-ephemerides"


def acquire(folder, day, cache=None):
    dest = folder / f"{day}.json"
    try:
        validate(json.loads(dest.read_bytes()), day)
        return "local"
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        pass
    with tempfile.TemporaryDirectory(dir=folder) as tmp:
        candidate = Path(tmp) / "dia.json"
        try:
            with urlopen(f"{BASE}/{day}.json", timeout=15) as response:
                candidate.write_bytes(response.read())
            validate(json.loads(candidate.read_bytes()), day)
            source = "repositorio"
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            if cache is None:
                raise
            subprocess.run([sys.executable, str(Path(__file__).with_name("daily_asteroid_ephemeris.py")),
                            "--date",str(day),"--cache",str(cache),"--output",str(candidate)],check=True)
            validate(json.loads(candidate.read_bytes()),day)
            source = "cálculo Swiss"
        os.replace(candidate,dest)
        return source


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("carpeta",type=Path)
    p.add_argument("fecha",type=date.fromisoformat)
    p.add_argument("--cache-swiss",type=Path)
    args = p.parse_args()
    args.carpeta.mkdir(parents=True,exist_ok=True)
    failed = False
    for delta in [0,-1,1,-2,2,-3,3,-4,4,-5,5]:
        day = args.fecha+timedelta(days=delta)
        try:
            print(day,acquire(args.carpeta,day,args.cache_swiss))
        except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.CalledProcessError) as exc:
            print(day,str(exc),file=sys.stderr)
            failed = True
    raise SystemExit(2 if failed else 0)
