"""Revisa un día (y su semanal) antes de guardar: orden de cuotas, conteos y las reglas 2, 5, 6, 7, 12 y 13.

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

OBJETIVO = {"segura": (3, 5, 2), "media": (4, 5, 4), "arriesgada": (7, 9, 10)}
TOPE = {"segura": 1.40, "media": 1.35, "arriesgada": 1.59}
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
            q, m = s["cuota"], s["mercado"].strip()
            local = s["partido"].split(" vs ")[0].strip().lower()
            if q > TOPE[nivel]:
                problemas.append(f"{nivel}: {s['partido']} {m} {q} pasa el tope de {TOPE[nivel]} (reglas 6 y 12)")
            if m.lower().startswith("gana ") and m[5:].strip().lower() != local:
                problemas.append(f"{nivel}: {s['partido']} {m}: victoria del visitante (regla 12)")
            if "o empate" in m.lower() and m.lower().replace(" o empate", "").strip() == local and q >= 1.20:
                problemas.append(f"{nivel}: {s['partido']} {m} {q}: doble oportunidad local a 1.20 o más (regla 13)")
            if "goles" in m.lower() and "más de 1.5" not in m.lower():
                problemas.append(f"{nivel}: {s['partido']} {m}: solo Más de 1.5 (regla 7)")
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
