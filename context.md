# Contexto de sesiones

Traspaso entre sesiones de agentes. Cada cambio o PR actualiza su entrada (regla en `AGENTS.md`, sección "Contexto entre sesiones"). Entradas de la más reciente a la más antigua. Cuando una PR se mergea o se cierra, su entrada se reduce a un resumen de dos o tres líneas.

---

## Post de flujos agénticos: qué necesita cada agente, 7 min (push directo a `main`, 2026-09-26)

- `blog/posts/flujos-agenticos-desarrollo-ia.html`: sección nueva `#que-necesita-cada-agente` tras `#implementar-por-capas` (contexto, conocimiento, guías/buenas prácticas y herramientas por agente; en Claude Code: `CLAUDE.md`, skills y subagentes con herramientas, modelo y skills acotados por papel, MCP como ejemplo). El párrafo de skills de `#implementar-por-capas` se movió ahí. ~1600 palabras, 7 min en post y tarjeta, `dateModified` 2026-09-26.
- Ficha del chatbot (nueva ancla, tag `Skills`), `llms.txt` y draft de LinkedIn (un párrafo breve con el detalle) resincronizados. Evals ejecutadas por el autor: en verde.

## Emojis en los drafts de LinkedIn y push directo a `main` como norma (push directo a `main`, 2026-09-26)

- Skill `manage-blog`: los drafts de LinkedIn llevan 2-4 emojis discretos para un tono más personal (`references/linkedin.md`, con lista de emojis sobrios y los que evitar); `humanizer.md` deja de vetarlos en LinkedIn (siguen fuera de los artículos). `check_post.py` avisa si un draft pasa de 4 emojis. Drafts existentes sin tocar.
- `AGENTS.md`: cada tarea terminada se commitea y pushea directamente a `main` y se prueba en producción; PR solo si el autor la pide. El flujo del chatbot en Vercel se alinea con esa norma.

## AGENTS.md como guía única (push directo a `main`, 2026-09-26)

- `CLAUDE.md` queda como redirección a `AGENTS.md` (enlace + `@AGENTS.md`). Toda instrucción nueva va en `AGENTS.md`.
- El flujo de despliegue del chatbot en Vercel, que solo estaba en `CLAUDE.md`, pasa a `AGENTS.md` ("Despliegue" > "Flujo de cambios del chatbot en Vercel").
- "Instrucciones adicionales (solo Cowork)" pasa a "Reglas operativas para agentes", que aplican a cualquier agente: git solo con petición explícita, `.env` intocable, skills locales, exclusiones de exploración.
- Push directo a `main` por petición explícita del autor.

## Post de flujos agénticos ampliado a 6 min (push directo a `main`, 2026-09-25)

- Push directo a `main` por petición explícita del autor, verificado en producción.
- `blog/posts/flujos-agenticos-desarrollo-ia.html`: 987 → ~1390 palabras (6 min en post y tarjeta), `dateModified` 2026-09-25. Basado en el boceto "Software factory" del autor: humano define (análisis inicial de requisitos opcional) y valida/decide despliegue al final con un informe; analista con el modelo más capaz (diseño, análisis, planificación, estructura tipo OpenSpec); implementadores por capa con modelo barato; tester con modelo algo más capaz; seguridad, mantenibilidad/escalabilidad y documentación; skills como conocimiento transversal; bucle con máximo de vueltas.
- El callout "Dónde decide el humano" (`#donde-decide-el-humano`) se movió justo tras la escena inicial y es el único sitio con la lista de decisiones humanas. La conclusión (`#conclusion`) pasa a "un equipo de software hecho de agentes". Ids sin cambios; fuente nueva: OpenSpec (verificada).
- Matiz del autor en `#la-spec-como-contrato`: la spec no entra en el repo del código pero queda registrada para revisar las decisiones de diseño de la IA en cualquier momento (también en la ficha).
- Ficha del chatbot y draft de LinkedIn resincronizados. Diagrama sin cambios. Evals ejecutadas por el autor: en verde.

## Umbrales de tamaño en la skill edit-cv (push directo a `main`, 2026-09-25)

- Push directo a `main` por petición explícita del autor, verificado en producción.
- `references/umbrales.md` + `scripts/check_cv.py` (stdlib): límites por componente. Tarjeta normal: subtítulo ≤100, 2–4 bullets, ≤200 por bullet, ≤550 en total. Destacada (`data-featured`, máx. 1 por página): ≤130 / ≤5 / ≤220 / ≤900. Job-card en la home ≤170 (actual ≤250). Contexto 250–450 (aviso). Decisiones del autor: dos niveles, script sin CI, el doc RAG no tiene umbrales y conserva el detalle.
- `CV/fermax.html#desarrollo-agentico` resumida de 1704 a ~900 caracteres y marcada como destacada; `#domain-events` condensada (598→541); descripción de Fermax en la home de 397 a 235. `FERMAX.md` sin cambios.
- Segunda pasada (2026-09-25): `CV/tfg.html` pasa al componente estándar (sección `#desarrollo-del-trabajo` con tres `.detail-card`; los `id` de siempre siguen en las tarjetas y las conclusiones son la destacada). Los 11 avisos, corregidos con datos que ya estaban en los docs RAG. `check_cv.py`: 0 errores, 0 avisos.
- Opendit desplegaba con Azure Container Apps (confirmado por el autor), no con AKS: corregido en `opendit.html`, `OPENDIT.md`, `CV.md` y el criterio de la eval de Kubernetes. Kubernetes sigue respaldado por Fermax y Securitas Direct. Evals pendientes de que las ejecute el autor.
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
