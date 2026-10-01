"""Calcula el porcentaje de acierto por tipo de mercado, competencia y rango de cuota.

Lee data/*.json (días) y data/semanas/*.json y escribe data/estadisticas.json.
Uso: python3 tools/estadisticas.py
"""
import glob
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tipo_mercado(m):
    m = m.lower()
    if "o empate" in m or "doble oportunidad" in m:
        return "Doble oportunidad"
    if "hándicap" in m or "por 2 o más" in m or "por 3" in m:
        return "Hándicap / ganar por margen"
    if "sin recibir" in m:
        return "Gana sin recibir gol"
    if m.startswith("gana") and ("goles" in m or "ambos" in m):
        return "Gana + goles"
    if "goles" in m:
        return "Más / menos goles"
    if "ambos marcan" in m:
        return "Ambos marcan"
    if m.startswith("gana"):
        return "Gana el favorito"
    return "Otro"


def rango_cuota(c):
    if c < 1.20:
        return "1.00-1.19"
    if c < 1.35:
        return "1.20-1.34"
    if c < 1.60:
        return "1.35-1.59"
    if c < 2.00:
        return "1.60-1.99"
    return "2.00+"


def liga(comp):
    return re.split(r" ·| \(", comp)[0].strip()


def selecciones():
    vistos = set()
    archivos = sorted(glob.glob(os.path.join(RAIZ, "data", "*.json"))) + sorted(
        glob.glob(os.path.join(RAIZ, "data", "semanas", "*.json"))
    )
    for ruta in archivos:
        if os.path.basename(ruta) == "estadisticas.json":
            continue
        d = json.load(open(ruta))
        grupos = [s for c in d.get("combinadas", []) for s in c["selecciones"]]
        grupos += d.get("selecciones", [])
        for s in grupos:
            # Una misma selección puede aparecer en varias combinadas: se cuenta una vez.
            clave = (s["partido"], re.sub(r"\s*\(.*\)", "", s["mercado"]).strip().lower())
            if clave in vistos or s.get("estado") not in ("ganada", "perdida"):
                continue
            vistos.add(clave)
            yield s


def resumir(filas, clave):
    out = {}
    for s in filas:
        k = clave(s)
        r = out.setdefault(k, {"ganadas": 0, "perdidas": 0})
        r["ganadas" if s["estado"] == "ganada" else "perdidas"] += 1
    for r in out.values():
        r["acierto"] = round(r["ganadas"] / (r["ganadas"] + r["perdidas"]), 2)
    return dict(sorted(out.items(), key=lambda kv: -(kv[1]["ganadas"] + kv[1]["perdidas"])))


def combinadas():
    out = {}
    for ruta in sorted(glob.glob(os.path.join(RAIZ, "data", "*.json"))):
        if os.path.basename(ruta) == "estadisticas.json":
            continue
        for c in json.load(open(ruta)).get("combinadas", []):
            if c.get("estado") in ("ganada", "perdida"):
                r = out.setdefault(c["nivel"], {"ganadas": 0, "perdidas": 0})
                r["ganadas" if c["estado"] == "ganada" else "perdidas"] += 1
    return out


if __name__ == "__main__":
    filas = list(selecciones())
    stats = {
        "selecciones_cerradas": len(filas),
        "por_mercado": resumir(filas, lambda s: tipo_mercado(s["mercado"])),
        "por_competencia": resumir(filas, lambda s: liga(s["competencia"])),
        "por_cuota": resumir(filas, lambda s: rango_cuota(s["cuota"])),
        "combinadas": combinadas(),
    }
    json.dump(stats, open(os.path.join(RAIZ, "data", "estadisticas.json"), "w"), ensure_ascii=False, indent=2)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
