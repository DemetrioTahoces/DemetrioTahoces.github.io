# Contexto de sesiones

Traspaso entre sesiones de agentes. Cada cambio o PR actualiza su entrada (regla en `AGENTS.md`, sección "Contexto entre sesiones"). Entradas de la más reciente a la más antigua. Cuando una PR se mergea o se cierra, su entrada se reduce a un resumen de dos o tres líneas.

---

## Umbrales de tamaño en la skill edit-cv (push directo a `main`, 2026-09-25)

- Push directo a `main` por petición explícita del autor, verificado en producción.
- `references/umbrales.md` + `scripts/check_cv.py` (stdlib): límites por componente. Tarjeta normal: subtítulo ≤100, 2–4 bullets, ≤200 por bullet, ≤550 en total. Destacada (`data-featured`, máx. 1 por página): ≤130 / ≤5 / ≤220 / ≤900. Job-card en la home ≤170 (actual ≤250). Contexto 250–450 (aviso). Decisiones del autor: dos niveles, script sin CI, el doc RAG no tiene umbrales y conserva el detalle.
- `CV/fermax.html#desarrollo-agentico` resumida de 1704 a ~900 caracteres y marcada como destacada; `#domain-events` condensada (598→541); descripción de Fermax en la home de 397 a 235. `FERMAX.md` sin cambios.
- Avisos pendientes (no bloquean): tarjetas de un solo bullet en `imagine800.html` y `opendit.html#telemetria-cqrs`, y bullets cortos en inditex/opendit.
- Pendiente del autor: regenerar el PDF (`assets/CV-Demetrio-Tahoces.pdf`, comando en `README.md`) si quiere reflejar la nueva descripción de Fermax.

## Mejoras de la skill manage-blog y OG en PNG (push directo a `main`, 2026-09-24)

- Push directo a `main` por petición explícita del autor, sin PR.
- `SKILL.md` más corto: detalle movido a `references/{diagrama,fuentes,linkedin,ficha-chatbot,edicion}.md`. Nuevo flujo para editar posts publicados (`references/edicion.md`).
- `scripts/check_post.py`: errores nuevos para anclas `{#id}` de la ficha inexistentes, minutos distintos entre post y tarjeta, y OG/Twitter que no sean PNG. Avisos nuevos: etiquetas distintas entre post y tarjeta, estilo del humanizer (vocabulario y fórmulas vetadas, más de 3 negritas, headings en title case). Los posts antiguos dan avisos esperados: etiquetas cortas en la tarjeta y los nombres de los principios SOLID en inglés.
- `scripts/screenshot.mjs <slug>`: capturas de escritorio y móvil del post y del índice, con aviso de desbordamiento y de recursos que no cargan.
- Posts antiguos con OG/Twitter/JSON-LD en PNG: `blog/assets/solid-principios-diseno.png` (generado) y `blog/assets/domain-events-brokers-mensajeria.png` (el PNG original de `linkedin-drafts/`, movido; regenerarlo sin Google Fonts solapa el texto).
- CI nuevo `.github/workflows/blog.yml` (`check_post.py --all`); `AGENTS.md` actualizado.

Pendiente del autor (no bloquea):

- Revisar en Pages los posts, sobre todo en móvil (desde el entorno cloud no cargan Tailwind ni Google Fonts), y las previsualizaciones OG en LinkedIn.
- Ejecutar las evals del chatbot (ficha nueva del blog y cambio en `FERMAX.md`).
- Escena inicial genérica del post `flujos-agenticos-desarrollo-ia` (agente, 600 líneas, 500): sustituir si aporta un ejemplo propio.
- Decidir si la ficha `CV/Chatbot/docs/FERMAX.md` enlaza el post (ahora no, para no asociarlo a la empresa).
- Probar la skill con otros casos (editar un post, solo draft de LinkedIn) y ajustar.

## PR #19 (mergeada): skill manage-blog mejorada y post de flujos agénticos

Skill con briefing, plantilla, `check_post.py` y enlaces en `.claude/skills/`; `context.md` y su norma en `AGENTS.md`. Post `flujos-agenticos-desarrollo-ia` sobre el patrón "fábrica de tareas": solo el patrón, sin internos del equipo ni nombre de la empresa (decisión del autor); el humano decide al arrancar, en las dudas de la spec y al final (acepta, revisa la PR y decide la promoción a pre y pro).

## Notas de entorno (sesiones cloud)

- El proxy bloquea `cdn.tailwindcss.com`, Google Fonts, `metr.org` y `arxiv.org`. Las capturas salen sin Tailwind (la imagen desborda en móvil también en posts antiguos): la revisión visual real se hace en local o en GitHub Pages.
- El `uv` preinstalado (0.8.x) solo conoce Python 3.14.0rc2, incompatible con pydantic. Solución usada: instalar un uv reciente con `pip install --target <scratchpad> uv` y ejecutar con ese binario.
- Chromium está en `/opt/pw-browsers/chromium`; `npm ci --prefix .agents/skills/manage-blog/scripts` instala `puppeteer-core`.
- Evals del chatbot: no ejecutadas. Solo las lanza un humano.
