"""Refinar las ramas orientadas de aspectos mayores con posiciones Swiss intradiarias."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from functools import lru_cache
from observatorio import separation


def signed(x):
    return (x + 180) % 360 - 180


def roots(fn, stamps, tolerance=1e-7):
    """Localizar cruces y tangencias en extremos de velocidad dentro de cada tramo."""
    def bisect(left, right, component):
        start = fn(left)[component]
        for _ in range(55):
            mid = left+(right-left)/2
            value = fn(mid)[component]
            if mid in (left,right) or abs(value) < 1e-12:
                return mid
            if (start < 0) == (value < 0):
                left,start = mid,value
            else:
                right=mid
        return mid

    knots=set(stamps)
    for left,right in zip(stamps,stamps[1:]):
        if fn(left)[1] * fn(right)[1] < 0:
            knots.add(bisect(left,right,1))
    knots=sorted(knots)
    found=[]
    for t in knots:
        if abs(fn(t)[0]) <= tolerance:
            found.append(t)
    for left,right in zip(knots,knots[1:]):
        a,b=fn(left)[0],fn(right)[0]
        if a*b < 0 and abs(a-b)<180:
            t=bisect(left,right,0)
            if abs(fn(t)[0]) <= tolerance:
                found.append(t)
    return sorted(set(found))


def refine(data, ephe):
    import swisseph as swe
    from daily_asteroid_ephemeris import PLANETS
    from observatorio import LABELS, ASTEROIDS
    ids={LABELS[k]:v for k,v in PLANETS.items()}
    ids.update({name:swe.JUNO if key=="3" else swe.AST_OFFSET+int(key) for key,name in ASTEROIDS.items()})
    ids["Quirón"]=swe.CHIRON
    swe.set_ephe_path(str(ephe))
    @lru_cache(maxsize=100000)
    def position(name,t):
        instant=datetime.fromtimestamp(t,timezone.utc)
        hour=(instant.hour+instant.minute/60+(instant.second+instant.microsecond/1e6)/3600)
        jd=swe.julday(instant.year,instant.month,instant.day,hour)
        xx,flags=swe.calc_ut(jd,ids[name],swe.FLG_SWIEPH|swe.FLG_SPEED)
        if flags!=258:
            raise ValueError(f"{name}: motor/marco inesperado {flags}")
        return xx[0],xx[3]
    center=datetime.fromisoformat(data["fecha"]+"T09:00:00+00:00")
    stamps=[(center+timedelta(hours=i)).timestamp() for i in range(-120,121,3)]
    rows=[]
    for c in data["contactos"]:
        lon,speed=position(c["transito"],center.timestamp())
        if separation(lon,c["longitud"])>1e-5:
            raise ValueError("La fuente intradiaria difiere del producto diario")
        if c["carta"]=="Tránsito" and separation(position(c["receptor"],center.timestamp())[0],c["destino"])>1e-5:
            raise ValueError("El receptor móvil difiere del producto diario")
        for angle in sorted({c["angulo"],(-c["angulo"])%360}):
            def fn(t):
                a,sa=position(c["transito"],t)
                b,sb=position(c["receptor"],t) if c["carta"]=="Tránsito" else (c["destino"],0)
                return signed(a-b-angle),sa-sb
            for t in roots(fn,stamps):
                rows.append(dict(transito=c["transito"],receptor=c["receptor"],carta=c["carta"],
                                 aspecto=c["aspecto"],utc=datetime.fromtimestamp(t,timezone.utc).isoformat(timespec="seconds"),
                                 residuo_deg=abs(fn(t)[0])))
    return sorted(rows,key=lambda row:row["utc"])


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("resultado",type=Path)
    p.add_argument("efemerides",type=Path)
    args=p.parse_args()
    print(json.dumps(refine(json.loads(args.resultado.read_text()),args.efemerides),ensure_ascii=False))
