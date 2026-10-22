Reglas de diseño y contenido de los posts. Se leen al redactar; lo comprobable lo valida `scripts/check_post.py`.

# Diseño y contenido del artículo

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
