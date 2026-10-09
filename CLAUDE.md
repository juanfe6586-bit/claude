# Boleto del Día — manual de operación

App personal de combinadas de fútbol del usuario (Colombia, hora America/Bogota, apuesta en Stake). Todo en español.

- App: https://claude.ai/artifact/2iPVqbgmH6pZ4zzteViswa (código en `app/index.html`; no republicar salvo cambios de diseño pedidos).
- **La base de la app es la fuente de verdad** (herramienta ArtifactData; cargarla con ToolSearch `select:ArtifactData`):
  - `dias/<AAAA-MM-DD>`: las tres combinadas del día + análisis de partidos.
  - `semanas/<lunes AAAA-MM-DD>`: apuesta semanal.
  - `meta/aprendizaje`: `reglas` activas (texto + origen), `vigilar`, `historial`, `mercados` y `actualizado`. La app muestra reglas y mercados.
- `data/` en el repo replica la base (`data/dias/`, `data/semanas/`, `data/meta/`) y es solo copia de respaldo.

## Rutina diaria — siempre todos los pasos

0. **Sincronizar.** Desde la raíz del repo: `ArtifactData list` de `dias`, `semanas` y `meta` con `out_dir: "data"` y `query.limit: 1000`. Anota la `version` de cada documento que vayas a cambiar (sale en el resultado).
1. **Verificar.** `python3 tools/pendientes.py` lista solo los partidos pendientes que ya se jugaron. Busca cada marcador final (solo cuentan los 90 minutos; los penales no). Si no aparece, busca otra vez en inglés o en FotMob/Sofascore antes de concluir nada; nunca des un partido por aplazado ni le cambies la fecha sin una fuente de resultados que lo confirme. Marca con `python3 tools/marcar.py '<json>'` (ver uso en el script): actualiza todas las combinadas y la semanal donde aparezca y las cierra (perdida si falla una; ganada si todas ganan).
2. **Aprender.** `python3 tools/estadisticas.py` actualiza `mercados` en `data/meta/aprendizaje.json`. Si un fallo enseña algo, edita en ese archivo `reglas` (con su origen), `vigilar` (pocos datos) e `historial`.
3. **Hoy.** Si `dias/<hoy>` ya existe, no lo reemplaces: revisa bajas de última hora y avisa en el resumen.
4. **Mañana (obligatorio).** Arma `data/dias/<mañana>.json`. Confirma la fecha de cada partido en dos fuentes, una de su propia liga (regla 10); si no coinciden, no lo uses. Si mañana es lunes, arma también `data/semanas/<mañana>.json`.
5. **Guardar.** Un solo `ArtifactData batch` con todos los documentos cambiados (`file_path` + `if_version`; sin `if_version` solo los nuevos). Después `git add -A && git commit && git push` a `claude/cool-davinci-21v2qd`; si el push falla, sigue (la base ya quedó guardada) y dilo.
6. **Resumen** de 10 líneas como máximo: resultados verificados, qué se aprendió, novedades de hoy y combinadas de mañana con cuotas.

## Cómo armar las combinadas

- Ligas: Europa top (Champions, Europa/Conference, Premier, LaLiga, Serie A, Bundesliga, Ligue 1) y Latinoamérica (BetPlay, Liga MX, Argentina, Brasil, Libertadores, Sudamericana). En días flojos: Portugal, Holanda, Turquía, MLS, Ecuador, Chile, Perú. **En fecha FIFA**: revisa también Nations League y eliminatorias de ese día y úsalos; evita los amistosos (la fecha FIFA dura varios días; confirma el calendario, no supongas que ya terminó).
- Nunca segunda división o inferiores. Siempre las tres combinadas: si no todo cumple las reglas, usa lo que más reglas cumpla y dilo en la nota.
- Solo combinadas. Segura ~2 (3-5 selecciones), media ~4 (4-5), arriesgada ~10 (5-9). Muchas selecciones de cuota baja: gana el favorito, doble oportunidad, más de 1.5 goles. Nada de goleadas exactas ni "crear apuesta" dentro de un mismo partido.
- **Aplica siempre las `reglas` de `data/meta/aprendizaje.json`. Antes de guardar, repasa cada selección contra cada regla.**
- En cada selección pon `"reglas_rotas"`: lista con los números de las reglas que rompe (`[]` si las cumple todas). La app marca con un sello las combinadas que cumplen todas; prioriza armarlas así y dilo en el resumen.
- Cuotas: intenta Stake; stake.com está bloqueado en este entorno, así que usa la cuota pública, pon `"estimada": true` cuando no la viste en una fuente y avisa en la nota. Cuota total = producto, 2 decimales. `prob` = probabilidad honesta (0-1).
- Semanal: 8-12 selecciones de 1.10-1.35, cuota total 8-20, de lunes a domingo, un partido por selección; `dia` como "sáb 10 oct".
- Formato: copia la estructura de `data/dias/2026-10-02.json` y `data/semanas/2026-09-28.json`. Por partido: 2-4 claves y 1-2 fuentes. Horas en hora de Colombia ("7:00 p. m.").

## Ahorro de tokens (obligatorio)

- No leas los JSON completos: usa `tools/` o `python3 -c` para ver solo lo necesario.
- Usa WebSearch (WebFetch está bloqueado). Una búsqueda por marcador ("Local Visitante resultado <fecha>"). Para armar: 1-3 búsquedas de agenda y 1 de cuotas/previa por partido candidato. Tope: 25 búsquedas por corrida.
- Escribe los JSON con un script de Python y súbelos con `file_path`; nunca pegues el JSON en la llamada.
- No releas archivos recién escritos.
