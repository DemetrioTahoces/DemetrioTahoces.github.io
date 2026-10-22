---
name: manage-blog
description: Crear, editar y mantener el blog técnico estático del CV de Demetrio Tahoces. Usar cuando se pidan nuevos artículos educativos en blog/posts, cambios en blog/index.html, copias Markdown para el chatbot en CV/Chatbot/docs/blog, actualización de tarjetas del blog, imágenes/metadatos de posts, o generación de borradores de LinkedIn listos para copiar y pegar desde contenido del blog.
---

# Manage Blog

Mantener `/blog/` como blog educativo separado del CV pero visualmente coherente con él. Sirve para compartir conocimiento técnico de trabajo o proyectos personales, sin mencionar la fuente de aprendizaje salvo petición explícita.

## Artículo nuevo

0. **Briefing antes de escribir:** `references/briefing.md`. Si el usuario no tiene idea definida, brainstorm con propuestas basadas en su CV y en los posts publicados, y encuesta para elegir. Siempre se pregunta cuántos minutos de lectura quiere y qué se puede contar públicamente. Todo en encuesta cerrada (máximo 4 preguntas por ronda), nunca en listas abiertas por chat. No inventar experiencias, métricas ni anécdotas.
1. Leer `blog/index.html` y, si el tema toca experiencia profesional, la ficha de `CV/Chatbot/docs/` para respetar lo que es público.
2. Proponer título, slug, índice de secciones (con sus `id`), idea del diagrama, minutos objetivo con su presupuesto de palabras y los huecos de ejemplos. Ajustar antes de redactar.
3. Crear el esqueleto con `python3 .agents/skills/manage-blog/scripts/new_post.py <slug> --title ... --tags A,B,C --minutes N ...`: copia `references/post-template.html` con las versiones `?v=N` del índice, añade la tarjeta en primera posición, sube el contador "N publicados" y deja la ficha y el draft con frontmatter. Slug en minúsculas, ASCII y con guiones. Los `id` de sección son estables. Quedan marcadores `{{...}}` que hay que sustituir (el validador falla si sobra alguno). Sin manifest JSON, bundler ni renderizado por JavaScript.
4. Rellenar el artículo, la tarjeta (descripción y alt) y los marcadores del esqueleto.
5. Diagrama `blog/assets/<slug>.svg` y su PNG 1200x630 `blog/assets/<slug>.png`: `references/diagrama.md`. El SVG va en el artículo y la tarjeta; el PNG en `og:image`, `twitter:image`, JSON-LD y como imagen de LinkedIn.
6. Ficha del chatbot `CV/Chatbot/docs/blog/<slug>.md`: `references/ficha-chatbot.md`.
7. Draft de LinkedIn `blog/linkedin-drafts/<slug>.txt`: `references/linkedin.md`.
8. Fuentes verificadas: `references/fuentes.md`.
9. Emojis, con el texto ya cerrado: 4-7 en el artículo (lo normal, 5-6: más o menos uno por sección principal) y 3-5 en el draft, elegidos por lo que dice cada frase y distintos de los de otros posts, repartidos como hitos de lectura: `references/emojis.md`.
10. Auditoría obligatoria de `references/humanizer.md` sobre el artículo y el draft.
11. Validar (ver abajo).
12. Publicar: commit `feature(blog): ...` y push directo a `main` (AGENTS.md). Cerrar con el resumen de `references/briefing.md`: enlace, ejemplos hipotéticos, afirmaciones solo del briefing, minutos reales frente a los pedidos y evals pendientes.

## Editar un post publicado

`references/edicion.md`: ids estables, `dateModified`, qué resincronizar.

## Diseño y contenido

- Patrón del CV: tema oscuro sobrio, grid sutil, cards translúcidas, acentos azul/verde, Space Grotesk (display) + Inter (cuerpo).
- Assets compartidos `tokens.css` + `cv.css` + `blog.css` + `cv.js` con `?v=N` (`../assets/` desde `blog/`, `../../assets/` desde `blog/posts/`). Inline solo el gate `motion-ready`, favicon y metadatos. Prosa, callout/warning, tablas y post-cards viven en `assets/blog.css`; no redefinirlos en los posts.
- Animaciones: hero con capas `hero-stage` (`--stage-delay` 0.05/0.13/0.21/0.29/0.37s), `data-reveal` en el `<article>`, el `<figure>` y los grids de badges. La prosa no se trocea en reveals. En el índice, las post-cards van en un `data-reveal-group`.
- Sin dependencias front-end, build ni frameworks salvo instrucción explícita. Si cambia `assets/*.css|js` de forma incompatible, subir el `?v=N` de los HTML afectados en el mismo commit.
- Castellano profesional, educativo, directo y sobrio. Sin marketing vacío ni claims no defendibles. No mencionar empresa, cliente, compañero, curso o contexto laboral sensible salvo petición expresa; los términos prohibidos que dé el usuario se comprueban con `check_post.py --forbid`.
- Emojis: 4-7 por artículo (lo normal, 5-6), más o menos uno por sección principal y nunca dos en la misma, elegidos por el contenido para que no se repitan entre posts: al final de párrafos clave y, como mucho uno, en el `h2` de un callout. Solo dentro de la prosa y con `<span class="emoji" aria-hidden="true">`; nunca en títulos, metadatos, hero, tarjeta ni en los Markdown del chatbot. Detalle y marcado: `references/emojis.md`.
- Estructura orientada a aprendizaje: problema, contexto técnico, explicación, tradeoffs, ejemplo y conclusiones accionables. Abrir con una situación reconocible y contexto técnico inmediato; sostener una opinión técnica clara.
- Lectura de 3 a 8 minutos: los que pida el usuario en el briefing (si no los fija, cerca de 3 en temas sencillos y de 8 en complejos), calculada como palabras de `.article-prose` / 220. El valor declarado en post y tarjeta es el estimado, y el validador avisa si no coincide con el objetivo (`--minutes N`). Priorizar claridad sobre exhaustividad.
- Cada post: título, descripción, fecha, etiquetas, tiempo de lectura, enlaces al blog/CV y metadatos SEO/OG. Cada tarjeta: título, descripción breve, fecha, minutos, etiquetas (las mismas que el hero del post), enlace e imagen.
- Slug sincronizado entre `blog/posts/<slug>.html`, la tarjeta, `CV/Chatbot/docs/blog/<slug>.md`, `blog/linkedin-drafts/<slug>.txt` y `blog/assets/<slug>.{svg,png}`.
- Si el cambio afecta a lo que responde el chatbot, indicarlo en la PR: las evals (`uv run pytest -m evals`) solo las ejecuta un humano.

## Validación

- `python3 .agents/skills/manage-blog/scripts/check_post.py <slug> [--minutes N] [--forbid TERM ...]` (o `--all`) sin errores. También corre en CI (`.github/workflows/blog.yml`). Comprueba: existencia y sincronía de HTML, ficha, draft y tarjeta; canonical, OG/Twitter (PNG) y JSON-LD; frontmatter; anclas `{#id}` de la ficha y ficha sin emojis; enlaces relativos e `id` duplicados; tiempo de lectura; minutos iguales en post y tarjeta (y aviso si difieren las etiquetas); orden y contador del índice; `?v=N`; draft sin Markdown y con URL pública; em/en dash; marcadores `{{...}}` sin sustituir; términos prohibidos en HTML, ficha, draft y SVG; colores del SVG ajenos a los tokens y al resto de diagramas; y avisos de estilo del humanizer (vocabulario inflado, fórmulas, exceso de negritas) y de emojis (menos de 4 o más de 7 en la prosa, menos de 3 o más de 5 en el draft, fuera de la prosa, en un heading que no sea el `h2` de un callout o en más de uno, sin `class="emoji"`/`aria-hidden`, sin `&nbsp;` al final de párrafo o en la tarjeta).
- Desde `CV/Chatbot`: `uv run python -m core.llms_txt` y `uv run pytest`.
- Revisión visual: `node .agents/skills/manage-blog/scripts/screenshot.mjs <slug>` con un servidor estático en marcha (`python -m http.server 8000` desde la raíz). Guarda capturas de escritorio y móvil, e informa de desbordamiento horizontal y de recursos bloqueados (si Tailwind o las fuentes no cargan, la captura no es fiable).
- Los avisos de estilo no bloquean, pero cada uno se revisa a mano con `references/humanizer.md`.
