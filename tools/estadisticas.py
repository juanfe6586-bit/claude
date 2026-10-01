"""Acierto por tipo de mercado, competencia y rango de cuota.

Escribe data/estadisticas.json y actualiza "mercados" y "actualizado" en data/meta/aprendizaje.json
(las reglas de ese archivo se editan a mano). Imprime un resumen compacto.
Uso: python3 tools/estadisticas.py
"""
import json
import os
import re

from comun import DATA, documentos, guardar, hoy


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
    for tope, nombre in ((1.20, "1.00-1.19"), (1.35, "1.20-1.34"), (1.60, "1.35-1.59"), (2.00, "1.60-1.99")):
        if c < tope:
            return nombre
    return "2.00+"


def liga(comp):
    return re.split(r" ·| \(", comp)[0].strip()


def selecciones():
    vistos = set()
    for _, _, doc in documentos():
        for s in [s for c in doc.get("combinadas", []) for s in c["selecciones"]] + doc.get("selecciones", []):
            # Una misma selección puede aparecer en varias combinadas: se cuenta una vez.
            clave = (s["partido"], re.sub(r"\s*\(.*\)", "", s["mercado"]).strip().lower())
            if clave in vistos or s.get("estado") not in ("ganada", "perdida"):
                continue
            vistos.add(clave)
            yield s


def resumir(filas, clave):
    out = {}
    for s in filas:
        r = out.setdefault(clave(s), {"ganadas": 0, "perdidas": 0})
        r["ganadas" if s["estado"] == "ganada" else "perdidas"] += 1
    for r in out.values():
        r["acierto"] = round(r["ganadas"] / (r["ganadas"] + r["perdidas"]), 2)
    return dict(sorted(out.items(), key=lambda kv: -(kv[1]["ganadas"] + kv[1]["perdidas"])))


def combinadas():
    out = {}
    for _, col, doc in documentos():
        for c in doc.get("combinadas", []) if col == "dias" else [doc]:
            if c.get("estado") in ("ganada", "perdida"):
                r = out.setdefault(c.get("nivel", "semanal"), {"ganadas": 0, "perdidas": 0})
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
    guardar(os.path.join(DATA, "estadisticas.json"), stats)

    ruta_meta = os.path.join(DATA, "meta", "aprendizaje.json")
    meta = json.load(open(ruta_meta))
    meta["mercados"] = [{"tipo": k, "ganadas": v["ganadas"], "perdidas": v["perdidas"]} for k, v in stats["por_mercado"].items()]
    meta["actualizado"] = hoy().isoformat()
    guardar(ruta_meta, meta)

    print(f"{len(filas)} selecciones cerradas")
    for nombre in ("por_mercado", "por_competencia", "por_cuota", "combinadas"):
        print(nombre + ": " + "; ".join(f"{k} {v['ganadas']}/{v['ganadas'] + v['perdidas']}" for k, v in stats[nombre].items()))
