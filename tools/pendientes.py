"""Lista, sin repetir, las selecciones pendientes de partidos que ya debieron jugarse,
y avisa si faltan las combinadas de hoy o de mañana o la semanal de esta semana.

Uso: python3 tools/pendientes.py   (salida compacta: fecha | partido | mercado)
"""
import datetime as dt
import os

from comun import DATA, documentos, fecha_seleccion, grupos, hoy

vistos = {}
for _, _, doc in documentos():
    for c in grupos(doc):
        for s in c["selecciones"]:
            if s.get("estado", "pendiente") != "pendiente":
                continue
            f = fecha_seleccion(doc, s)
            if f > hoy():
                continue
            vistos.setdefault((f.isoformat(), s["partido"]), set()).add(s["mercado"])

for (f, partido), mercados in sorted(vistos.items()):
    print(f"{f} | {partido} | {' / '.join(sorted(mercados))}")
print(f"-- {len(vistos)} partidos por verificar")

lunes = hoy() - dt.timedelta(days=hoy().weekday())
for nombre, ruta in (("hoy", f"dias/{hoy()}"), ("mañana", f"dias/{hoy() + dt.timedelta(days=1)}"), ("semanal", f"semanas/{lunes}")):
    if not os.path.exists(os.path.join(DATA, ruta + ".json")):
        print(f"FALTA {nombre}: {ruta} (ármalo en esta corrida)")
