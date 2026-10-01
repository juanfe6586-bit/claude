"""Utilidades compartidas: carpeta de datos, fechas y cierre de combinadas.

data/ replica la base de la app: data/dias/<fecha>.json, data/semanas/<lunes>.json, data/meta/aprendizaje.json.
Se sincroniza con: ArtifactData list collection=<dias|semanas> out_dir=data
"""
import datetime as dt
import glob
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(RAIZ, "data")
MESES = {m: i + 1 for i, m in enumerate(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"])}


def documentos():
    """(ruta, coleccion, doc) de cada día y semana."""
    for col in ("dias", "semanas"):
        for ruta in sorted(glob.glob(os.path.join(DATA, col, "*.json"))):
            yield ruta, col, json.load(open(ruta))


def guardar(ruta, doc):
    json.dump(doc, open(ruta, "w"), ensure_ascii=False, indent=2)


def grupos(doc):
    """Combinadas de un documento: las tres del día o la semanal como una sola."""
    return doc["combinadas"] if "combinadas" in doc else [doc]


def fecha_seleccion(doc, sel):
    """Fecha del partido: la del día, o la del campo 'dia' en la semanal ("sáb 3 oct")."""
    if "fecha" in doc:
        return dt.date.fromisoformat(doc["fecha"])
    m = re.search(r"(\d+)\s+(\w{3})", sel.get("dia", ""))
    lunes = dt.date.fromisoformat(doc["semana"])
    if not m:
        return lunes
    f = dt.date(lunes.year, MESES[m.group(2).lower()], int(m.group(1)))
    return f if f >= lunes - dt.timedelta(days=7) else f.replace(year=f.year + 1)


def cerrar(combinada):
    estados = [s["estado"] for s in combinada["selecciones"]]
    if "perdida" in estados:
        combinada["estado"] = "perdida"
    elif all(e in ("ganada", "nula") for e in estados):
        combinada["estado"] = "ganada"
    else:
        combinada["estado"] = "pendiente"


def hoy():
    return (dt.datetime.utcnow() - dt.timedelta(hours=5)).date()
