"""Revisa un día (y su semanal) antes de guardar: orden de cuotas, conteos y límites de las reglas 2 y 6.

Uso:
  python3 tools/validar.py 2026-10-12
Imprime los problemas encontrados ("OK" si no hay). Corrige cada uno o explícalo en la nota.
"""
import json
import math
import os
import sys
from collections import defaultdict

from comun import DATA

OBJETIVO = {"segura": (3, 5, 2), "media": (4, 5, 4), "arriesgada": (5, 9, 10)}
fecha = sys.argv[1]
problemas = []


def revisar_dia(doc):
    combos = {c.get("nivel"): c for c in doc["combinadas"]}
    if sorted(combos) != sorted(OBJETIVO):
        problemas.append(f"faltan combinadas: hay {sorted(combos)}")
        return
    usos = defaultdict(list)
    for nivel, (minimo, maximo, meta) in OBJETIVO.items():
        c = combos[nivel]
        sel = c["selecciones"]
        total = round(math.prod(s["cuota"] for s in sel), 2)
        if abs(total - c["cuota"]) > 0.01:
            problemas.append(f"{nivel}: cuota {c['cuota']} no es el producto {total}")
        if not minimo <= len(sel) <= maximo:
            problemas.append(f"{nivel}: {len(sel)} selecciones (pide {minimo}-{maximo})")
        if not meta * 0.75 <= total <= meta * 1.5:
            problemas.append(f"{nivel}: cuota {total} lejos de ~{meta}")
        for s in sel:
            usos[s["partido"]].append((nivel, s["mercado"]))
            if "reglas_rotas" not in s:
                problemas.append(f"{nivel}: {s['partido']} sin reglas_rotas")
            q = s["cuota"]
            if nivel == "segura" and q > 1.40 or nivel == "media" and q > 1.35:
                problemas.append(f"{nivel}: {s['partido']} {s['mercado']} {q} pasa el tope de la regla 6")
            if q >= 1.80:
                problemas.append(f"{nivel}: {s['partido']} {s['mercado']} {q} (>= 1.80, regla 5/6)")
    if not combos["segura"]["cuota"] < combos["media"]["cuota"] < combos["arriesgada"]["cuota"]:
        problemas.append("orden de cuotas: debe ser segura < media < arriesgada "
                         f"({combos['segura']['cuota']}, {combos['media']['cuota']}, {combos['arriesgada']['cuota']})")
    for partido, u in usos.items():
        if len(u) > 2:
            problemas.append(f"regla 2: {partido} está en {len(u)} combinadas")
        if len({m for _, m in u}) < len(u):
            problemas.append(f"regla 2: {partido} repite mercado")


def revisar_semana(doc):
    sel = doc["selecciones"]
    total = round(math.prod(s["cuota"] for s in sel), 2)
    if abs(total - doc["cuota"]) > 0.01:
        problemas.append(f"semanal: cuota {doc['cuota']} no es el producto {total}")
    if not 8 <= len(sel) <= 12:
        problemas.append(f"semanal: {len(sel)} selecciones (pide 8-12)")
    if not 8 <= total <= 20:
        problemas.append(f"semanal: cuota {total} fuera de 8-20")
    for s in sel:
        if not 1.10 <= s["cuota"] <= 1.35:
            problemas.append(f"semanal: {s['partido']} {s['cuota']} fuera de 1.10-1.35")
    if len({s["partido"] for s in sel}) < len(sel):
        problemas.append("semanal: un partido repetido")
    if len({s.get("dia") for s in sel}) < 2:
        problemas.append("semanal: todas las selecciones son del mismo día (debe cubrir de lunes a domingo)")


ruta = os.path.join(DATA, "dias", f"{fecha}.json")
revisar_dia(json.load(open(ruta)))
semana = os.path.join(DATA, "semanas", f"{fecha}.json")
if os.path.exists(semana):
    revisar_semana(json.load(open(semana)))
print("\n".join(problemas) or "OK")
