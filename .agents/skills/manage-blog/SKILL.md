---
name: manage-blog
description: Crear, editar y mantener el blog técnico estático del CV de Demetrio Tahoces. Usar cuando se pidan nuevos artículos educativos en blog/posts, cambios en blog/index.html, copias Markdown para el chatbot en CV/Chatbot/docs/blog, actualización de tarjetas del blog, imágenes/metadatos de posts, o generación de borradores de LinkedIn listos para copiar y pegar desde contenido del blog.
---

# Manage Blog

Mantener `/blog/` como blog educativo separado del CV pero visualmente coherente con él. Sirve para compartir conocimiento técnico de trabajo o proyectos personales, sin mencionar la fuente de aprendizaje salvo petición explícita.

## Artículo nuevo

0. **Briefing antes de escribir.** Si el usuario no lo ha dado ya, preguntar en una sola ronda (preguntas cerradas con opciones cuando se pueda): enfoque y tesis, público, ejemplos o experiencias propias, qué se puede contar públicamente (empresa, métricas, diseño interno) y fuentes. Si aportará ejemplos más tarde, proponer un índice con huecos marcados. No inventar experiencias, métricas ni anécdotas.
1. Leer `blog/index.html` y, si el tema toca experiencia profesional, la ficha de `CV/Chatbot/docs/` para respetar lo que es público.
2. Proponer título, slug, índice de secciones (con sus `id`) y la idea del diagrama. Ajustar antes de redactar.
3. Crear `blog/posts/<slug>.html` desde `references/post-template.html`. Slug en minúsculas, ASCII y con guiones. Los `id` de sección son estables.
4. Añadir la tarjeta en `blog/index.html` en primera posición (más reciente primero) y actualizar el contador "N publicados". Sin manifest JSON, bundler ni renderizado por JavaScript.
5. Diagrama `blog/assets/<slug>.svg` y su PNG 1200x630 `blog/assets/<slug>.png`: `references/diagrama.md`. El SVG va en el artículo y la tarjeta; el PNG en `og:image`, `twitter:image`, JSON-LD y como imagen de LinkedIn.
6. Ficha del chatbot `CV/Chatbot/docs/blog/<slug>.md`: `references/ficha-chatbot.md`.
7. Draft de LinkedIn `blog/linkedin-drafts/<slug>.txt`: `references/linkedin.md`.
8. Fuentes verificadas: `references/fuentes.md`.
9. Auditoría obligatoria de `references/humanizer.md` sobre el artículo y el draft.
10. Validar (ver abajo) y actualizar la entrada de `context.md`.

## Editar un post publicado

`references/edicion.md`: ids estables, `dateModified`, qué resincronizar.

## Diseño y contenido

- Patrón del CV: tema oscuro sobrio, grid sutil, cards translúcidas, acentos azul/verde, Space Grotesk (display) + Inter (cuerpo).
- Assets compartidos `tokens.css` + `cv.css` + `blog.css` + `cv.js` con `?v=N` (`../assets/` desde `blog/`, `../../assets/` desde `blog/posts/`). Inline solo el gate `motion-ready`, favicon y metadatos. Prosa, callout/warning, tablas y post-cards viven en `assets/blog.css`; no redefinirlos en los posts.
- Animaciones: hero con capas `hero-stage` (`--stage-delay` 0.05/0.13/0.21/0.29/0.37s), `data-reveal` en el `<article>`, el `<figure>` y los grids de badges. La prosa no se trocea en reveals. En el índice, las post-cards van en un `data-reveal-group`.
- Sin dependencias front-end, build ni frameworks salvo instrucción explícita. Si cambia `assets/*.css|js` de forma incompatible, subir el `?v=N` de los HTML afectados en el mismo commit.
- Castellano profesional, educativo, directo y sobrio. Sin marketing vacío ni claims no defendibles. No mencionar empresa, cliente, compañero, curso o contexto laboral sensible salvo petición expresa.
- Estructura orientada a aprendizaje: problema, contexto técnico, explicación, tradeoffs, ejemplo y conclusiones accionables. Abrir con una situación reconocible y contexto técnico inmediato; sostener una opinión técnica clara.
- Lectura de 3 a 8 minutos (cerca de 3 si el tema es sencillo, cerca de 8 si es complejo), calculada como palabras de `.article-prose` / 220. Priorizar claridad sobre exhaustividad.
- Cada post: título, descripción, fecha, etiquetas, tiempo de lectura, enlaces al blog/CV y metadatos SEO/OG. Cada tarjeta: título, descripción breve, fecha, minutos, etiquetas (las mismas que el hero del post), enlace e imagen.
- Slug sincronizado entre `blog/posts/<slug>.html`, la tarjeta, `CV/Chatbot/docs/blog/<slug>.md`, `blog/linkedin-drafts/<slug>.txt` y `blog/assets/<slug>.{svg,png}`.
- Si el cambio afecta a lo que responde el chatbot, indicarlo en la PR: las evals (`uv run pytest -m evals`) solo las ejecuta un humano.

## Validación

- `python3 .agents/skills/manage-blog/scripts/check_post.py <slug>` (o `--all`) sin errores. También corre en CI (`.github/workflows/blog.yml`). Comprueba: existencia y sincronía de HTML, ficha, draft y tarjeta; canonical, OG/Twitter (PNG) y JSON-LD; frontmatter; anclas `{#id}` de la ficha; enlaces relativos e `id` duplicados; tiempo de lectura; minutos iguales en post y tarjeta (y aviso si difieren las etiquetas); orden y contador del índice; `?v=N`; draft sin Markdown y con URL pública; em/en dash; y avisos de estilo del humanizer (vocabulario inflado, fórmulas, exceso de negritas).
- Desde `CV/Chatbot`: `uv run python -m core.llms_txt` y `uv run pytest`.
- Revisión visual: `node .agents/skills/manage-blog/scripts/screenshot.mjs <slug>` con un servidor estático en marcha (`python -m http.server 8000` desde la raíz). Guarda capturas de escritorio y móvil, e informa de desbordamiento horizontal y de recursos bloqueados (si Tailwind o las fuentes no cargan, la captura no es fiable).
- Los avisos de estilo no bloquean, pero cada uno se revisa a mano con `references/humanizer.md`.
