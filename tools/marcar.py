"""Marca resultados en todos los documentos donde aparece cada selección y cierra las combinadas.

Uso:
  python3 tools/marcar.py '[{"partido": "Japón vs Ecuador", "resultado": "0-0",
                            "mercados": {"Japón o empate": "ganada", "Gana Japón": "perdida"}}]'
El nombre del partido y del mercado deben coincidir con el texto guardado (sin importar mayúsculas).
Imprime qué documentos cambiaron, para subirlos en un solo ArtifactData batch.
"""
import json
import sys

from comun import cerrar, documentos, grupos, guardar

entradas = json.loads(sys.argv[1])
norm = lambda t: t.strip().lower()
cambiados, sin_usar = [], {(norm(e["partido"]), norm(m)) for e in entradas for m in e["mercados"]}

for ruta, col, doc in documentos():
    toco = False
    for c in grupos(doc):
        for s in c["selecciones"]:
            for e in entradas:
                if norm(s["partido"]) != norm(e["partido"]):
                    continue
                for mercado, estado in e["mercados"].items():
                    if norm(s["mercado"]) == norm(mercado):
                        s["estado"], s["resultado"] = estado, e["resultado"]
                        sin_usar.discard((norm(e["partido"]), norm(mercado)))
                        toco = True
        cerrar(c)
    if toco:
        guardar(ruta, doc)
        cambiados.append(f"{col}/{doc.get('fecha') or doc.get('semana')}")

print("Cambiados:", ", ".join(cambiados) or "ninguno")
if sin_usar:
    print("Sin coincidencia (revisa el texto):", sorted(sin_usar))
