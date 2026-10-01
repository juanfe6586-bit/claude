# Boleto del Día

App web con tres combinadas de fútbol cada día (cuota ~2, ~5 y ~10), el análisis de cada partido y un historial de aciertos.

- `app/index.html`: la página publicada como Artifact de claude.ai. Lee las combinadas de su base de datos (colección `dias`, un documento por fecha).
- `data/`: copia de la base de la app (`dias/`, `semanas/`, `meta/`).

Las cuotas marcadas como `estimada` son aproximadas y hay que confirmarlas en la casa de apuestas. Ninguna combinada es segura.

## Operación

`CLAUDE.md` es el manual de operación: la rutina diaria, cómo armar las combinadas y las reglas para ahorrar tokens. Los scripts de `tools/` verifican resultados (`pendientes.py`, `marcar.py`) y miden el acierto (`estadisticas.py`).
