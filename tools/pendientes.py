"""Lista, sin repetir, las selecciones pendientes de partidos que ya debieron jugarse.

Uso: python3 tools/pendientes.py   (salida compacta: fecha | partido | mercado)
"""
from comun import documentos, fecha_seleccion, grupos, hoy

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
