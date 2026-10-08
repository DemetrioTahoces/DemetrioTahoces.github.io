# Contexto de sesiones

Traspaso entre sesiones de agentes. Cada cambio o PR actualiza su entrada (regla en `AGENTS.md`, sección "Contexto entre sesiones"). Entradas de la más reciente a la más antigua. Cuando una PR se mergea o se cierra, su entrada se reduce a un resumen de dos o tres líneas.

---

## Timeouts de 300 s en `/api/mcp`: sin `subscriptions/listen` (push directo a `main`, 2026-10-08)

- Síntoma: Vercel registraba "Task timed out after 300 seconds" en `POST /api/mcp`, encadenados cada 5 minutos (en los logs de la última hora: 21:05, 21:10, 21:15). El chat no estaba afectado.
- Causa: `mcp` 2.2.0 (`MCPServer`) sirve siempre `subscriptions/listen` (spec 2026-07-28, SEP-2575) y por eso anuncia `listChanged`/`subscribe`. Un cliente moderno abre ese POST cuya respuesta es un stream de eventos; aquí nunca llega ninguno (herramientas estáticas, bus en memoria por instancia), así que Vercel lo corta a los 300 s y el cliente vuelve a escuchar. Reproducido en local: ack y stream abierto indefinidamente.
- Arreglo en `core/mcp_server.py`: se quita el handler (`_lowlevel_server._request_handlers`, no hay API pública). El servidor deja de anunciar `listChanged` y `subscriptions/listen` responde `-32601` al momento. Test `test_mcp_server_does_not_offer_listen_streams` (falla sin el arreglo); 79 tests en verde. Riesgo: usa un atributo privado del SDK; si un upgrade lo cambia, el import o el test fallan de forma visible.
- Sin cambios de prompt, modelo ni docs: no hacen falta evals. Verificación en producción: que no aparezcan timeouts nuevos en `/api/mcp` tras el despliegue.

## PR #20 (mergeada): post de normas para desarrollar con IA (2026-10-08)

Post `normas-desarrollo-ia-equipo` (6 min): el agente resuelve el ahora; el equipo pone el antes (normas escritas en AGENTS.md/skills y comprobadas en CI) y el después (visión de futuro, sobre todo en datos), con el ejemplo propio de NIF/VAT (formato común VIES verificado en backend, normalización por país en frontend). Incluye diagrama, tarjeta, ficha del chatbot, `llms.txt` y draft de LinkedIn. Emojis del post: 🪟 📐 🔭 🧾 ✍️ 🗺️; del draft: 🪟 🧾 ✍️ 👇.
Pendiente del autor: ejecutar las evals (ficha nueva) y revisar en Pages (móvil). Follow-up a petición del autor: fuente oficial de VIES (`https://ec.europa.eu/taxation_customs/vies/`) añadida al post y a la ficha; la URL se confirmó por buscador porque las webs de la UE dan 403 desde el proxy.

## Feedback del chatbot persistido en Redis (push directo a `main`, 2026-09-26)

- Antes el 👍/👎 solo iba a logs de Vercel (efímeros, sin el comentario) y a LangSmith si el tracing estaba activo (por defecto no). Ahora se guarda en el Upstash Redis que ya usa `abuse_guard`.
- `core/feedback_store.py`: cada respuesta (pregunta, respuesta, ruta, modelo; sin IP ni `session_id`) se guarda `FEEDBACK_TURN_TTL_HOURS` (24) en `cvbot:feedback:turn:<request_id>`; `POST /api/feedback` la copia con `rating`/`comment` en `cvbot:feedback:item:<request_id>` (TTL `FEEDBACK_RETENTION_DAYS`, 180) e indexa en `cvbot:feedback:index`. Fail-open. Lectura: `uv run python -m core.feedback_store --limit 20` o la consola de Upstash. Decisión del agente (el autor no la fijó): guardar la pregunta y la respuesta, porque sin ellas un 👎 no sirve; `FEEDBACK_TURN_TTL_HOURS=0` lo desactiva.
- `core/redis_rest.py`: cliente REST de Upstash extraído de `abuse_guard` (ahora `UpstashRedisStore(redis)`). Frontend sin cambios. Tests offline: 78 en verde (`test_feedback_store.py`, `FakeRedis` en `conftest.py`). Sin cambios de prompt, modelo ni docs: no hacen falta evals.
- Verificación en producción: desde el entorno cloud `*.vercel.app` está bloqueado (403 del proxy), así que el agente no pudo hacer el POST real. Pendiente del autor: una pregunta + 👍 en la web y comprobar con el CLI o en Upstash que aparece `cvbot:feedback:item:*` (si no, revisar que las `KV_REST_API_*` estén en el entorno Production de Vercel y el log `Feedback received` con `stored`).

## Más emojis en el blog: uno por sección (push directo a `main`, 2026-09-26)

- Criterio del autor: con 1-3 por artículo quedaban demasiado discretos. Skill `manage-blog` (`references/emojis.md`, `SKILL.md`, `humanizer.md`) y `AGENTS.md`: 4-7 por artículo (lo normal, 5-6), más o menos uno por sección principal y nunca dos en la misma ni en párrafos seguidos, ni tras un párrafo que abre una lista con dos puntos. Sigue como mucho uno en el `h2` de un callout/warning; el resto de reglas (marcado, dónde no van, drafts 2-4, fichas sin emojis) sin cambios. CSS sin tocar.
- `check_post.py`: avisa por debajo de 4 (`MIN_POST_EMOJIS`) y por encima de 7; el regex `EMOJI` ahora incluye U+231A-23FF (antes no detectaba ⏳ ni ⌛).
- Posts publicados (solo emojis; sin `dateModified`, fichas, drafts ni ids): domain events 6 (🌙 📣 🐇 en el h2 del warning 📬 📦 🕸️), flujos agénticos 6 (🔑 👀 📜 🧰 🏁 ⏳), SOLID 6 (⛓️ 🐧 ☕ 🔌 💧 🧭). `check_post.py --all` en OK (solo los avisos previos de etiquetas); `uv run pytest`: 71 en verde.
- Drafts de LinkedIn: de 2-4 a 3-5 emojis (lo normal, 4); `check_post.py` avisa por debajo de 3 (`MIN_DRAFT_EMOJIS`) y por encima de 5. Drafts publicados: domain events 🏷️ 🧯 🧩 👇, flujos agénticos 🤝 🛠️ 👥 👇, SOLID 🌱 🧲 🛡️ 👇 (👇 junto a la URL).
- `.claude/skills/` sincronizada con `.agents/skills/` (copia, no symlink).

## Emojis discretos y variados en el blog: skill y posts publicados (push directo a `main`, 2026-09-26)

- Criterio del autor: pocos, discretos y distintos según lo que se escribe, colocados de forma estratégica. Skill `manage-blog` (`references/emojis.md`, paso 9 de "Artículo nuevo"): 1-3 por artículo (lo normal, 2), con el texto ya cerrado, al final de párrafos clave y como mucho uno en el `h2` de un callout o warning; elegidos por lo que dice la frase (no de una lista fija) y sin repetir los de otros posts; los genéricos (💡 ⚠️ ✅ 📌 🤔) solo como último recurso. Nunca en títulos, metadatos, hero, `h2`/`h3` normales, código, tarjeta ni ficha del chatbot. Drafts de LinkedIn: 2-4, sin cambios.
- Marcado `<span class="emoji" aria-hidden="true">` y `&nbsp;` delante de los de final de párrafo. `assets/blog.css` (`?v=3` en el índice y los posts) los reduce (0.85em; 0.7em en `h2`) y les baja la saturación para que sean un acento y no un icono.
- `check_post.py` avisa por más de 3 emojis en la prosa (4 en el draft), fuera de la prosa, en headings que no sean el `h2` de un callout o en más de uno, sin `class="emoji"`/`aria-hidden`, sin `&nbsp;`, en la tarjeta o en la ficha. La plantilla deja el emoji del callout como `{{EMOJI_SEGUN_CONTENIDO}}`. `AGENTS.md` lo resume en una línea.
- Posts publicados, sin tocar texto, ids, `dateModified`, fichas ni drafts: domain events 🌙 escena ("a las tres de la mañana") y 📬 `#una-cola-un-consumidor-logico`; flujos agénticos 🔑 `#donde-decide-el-humano` y 🧰 `#que-necesita-cada-agente`; SOLID 💧 `#como-se-refuerzan-entre-si` ("como una gotera") y 🧭 `#regla-pragmatica`. `check_post.py --all` da los mismos avisos que antes.
- Skills: `.claude/skills/` es una copia de `.agents/skills/` (no enlaces simbólicos) desde `efc75d8`; ambas sincronizadas (`edit-cv` y `manage-blog`). `AGENTS.md`: se edita el original y se replica en la copia en el mismo commit.
- Los Markdown del chatbot (`CV/Chatbot/docs/`, fichas del blog incluidas) y `llms.txt` van sin emojis (criterio del autor): `test_documents_and_llms_txt_have_no_emojis` en `test_knowledge.py`, error en `check_post.py` si la ficha lleva alguno, y la norma en `AGENTS.md`, `CV/Chatbot/README.md`, `edit-cv` y `manage-blog`. Ahora mismo ninguno lleva. Tests offline: 71 en verde (con un uv reciente). `CV/Chatbot/.venv` ya lo ignoraba `CV/Chatbot/.gitignore`; el `.gitignore` raíz ignora ahora también el `.venv/` de la raíz.
- Pendiente del autor: revisar los emojis en GitHub Pages (desde el entorno cloud no cargan Tailwind ni Google Fonts).

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
