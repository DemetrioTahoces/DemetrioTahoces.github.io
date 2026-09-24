---
name: manage-blog
description: Crear, editar y mantener el blog técnico estático del CV de Demetrio Tahoces. Usar cuando se pidan nuevos artículos educativos en blog/posts, cambios en blog/index.html, copias Markdown para el chatbot en CV/Chatbot/docs/blog, actualización de tarjetas del blog, imágenes/metadatos de posts, o generación de borradores de LinkedIn listos para copiar y pegar desde contenido del blog.
---

# Manage Blog

## Overview

Mantener la sección `/blog/` como blog educativo separado del CV pero visualmente coherente con él. El blog sirve para almacenar y compartir conocimiento técnico adquirido en trabajo o proyectos personales, sin mencionar la fuente de aprendizaje salvo petición explícita.

## Workflow

0. **Briefing antes de escribir.** Si el usuario no lo ha dado ya, preguntar (una sola ronda, preguntas cerradas con opciones cuando se pueda): enfoque y tesis que defiende el artículo, público objetivo, ejemplos o experiencias propias que quiere incluir, qué se puede contar públicamente y qué no (empresa, métricas, diseño interno) y fuentes que quiera citar. Si el usuario dice que aportará ejemplos más tarde, proponer un índice con huecos marcados y pedirlos antes de redactar la prosa final. No inventar experiencias, métricas ni anécdotas.
1. Leer `blog/index.html`, el artículo relacionado si existe y `index.html` solo si la navegación principal puede verse afectada. Si el tema toca experiencia profesional, leer la ficha en `CV/Chatbot/docs/` y respetar lo que dice sobre qué es público.
2. Proponer al usuario título, slug, índice de secciones (con sus `id`) y la idea del diagrama. Ajustar antes de redactar.
3. Crear `blog/posts/<slug>.html` a partir de `references/post-template.html`. Slug en minúsculas, ASCII y palabras separadas por guiones. Los `id` de sección son estables: no se cambian aunque cambie el título.
4. Actualizar manualmente `blog/index.html`: tarjeta nueva en primera posición (orden de más reciente a más antiguo) y contador "N publicados". No introducir manifest JSON, bundler ni renderizado obligatorio por JavaScript.
5. Crear el diagrama `blog/assets/<slug>.svg` (ver "Diagrama") y convertirlo a `blog/assets/<slug>.png` 1200x630 con `scripts/svg-to-png.mjs`. El SVG se usa en el artículo y la tarjeta; el PNG en `og:image`, `twitter:image`, JSON-LD y como imagen sugerida para LinkedIn.
6. Crear o actualizar `CV/Chatbot/docs/blog/<slug>.md` (ficha resumida para el chatbot, ver abajo).
7. Crear o actualizar `blog/linkedin-drafts/<slug>.txt` con el texto final para LinkedIn, listo para copiar y pegar.
8. Leer `references/humanizer.md` y pasar obligatoriamente el artículo HTML y el draft de LinkedIn por esa auditoría.
9. Validar (ver "Validación"): `python3 .agents/skills/manage-blog/scripts/check_post.py <slug>` sin errores, y desde `CV/Chatbot` `uv run python -m core.llms_txt` + `uv run pytest`.

## Diseño y Contenido

- Mantener el patrón del CV: tema oscuro sobrio, fondo con grid sutil, cards translúcidas, acentos azul/verde y navegación accesible. Tipografía Space Grotesk (display) + Inter 300–800 (cuerpo).
- El blog consume los assets compartidos: `tokens.css` + `cv.css` + `blog.css` + `cv.js` con `?v=N` (rutas `../assets/` desde `blog/`, `../../assets/` desde `blog/posts/`). Inline solo quedan el gate `motion-ready`, favicon y metadatos. Los estilos de prosa, callout/warning, tablas y post-cards viven en `assets/blog.css`; no redefinirlos inline en los posts. La plantilla completa está en `references/post-template.html`.
- Animaciones: hero del post con capas `hero-stage` (`--stage-delay` 0.05/0.13/0.21/0.29/0.37s), `data-reveal` en el `<article>`, el `<figure>` del diagrama y los grids de badges. La prosa NO se trocea en reveals. En el índice, las post-cards van en un `data-reveal-group`.
- No añadir dependencias front-end, build step ni frameworks salvo instrucción explícita. Si cambias `assets/*.css|js` de forma incompatible, incrementa el `?v=N` de los HTML afectados en el mismo commit.
- Escribir en castellano profesional, educativo, directo y sobrio. Evitar marketing vacío, exageraciones y claims no defendibles.
- No mencionar empresa, cliente, compañero, curso, fuente concreta o contexto laboral sensible salvo que el usuario lo pida expresamente.
- Mantener artículos orientados a aprendizaje: problema, contexto técnico, explicación, tradeoffs, ejemplo práctico y conclusiones accionables.
- Mantener cada artículo en 3-8 minutos de lectura: cerca de 3 si el tema es sencillo, cerca de 8 si es complejo. Calcular el tiempo como palabras de `.article-prose` / 220, redondeado (`check_post.py` lo estima y avisa si lo declarado se desvía más de 1 minuto). Priorizar claridad y utilidad sobre exhaustividad; no abrumar al lector con ejemplos largos, listas excesivas o desarrollo enciclopédico.
- Hacer que cada artículo sea ameno y humano: abrir con una situación reconocible, pero con contexto técnico inmediato y sin ambigüedades de lectura. Usar ejemplos de desarrollo cotidiano o vida real, variar el ritmo y sostener una opinión técnica clara.
- Cada post debe incluir título, descripción, fecha, etiquetas, tiempo estimado de lectura si aplica, enlaces de vuelta al blog/CV y metadatos SEO/OG.
- Cada tarjeta del listado debe incluir título, descripción breve, fecha, etiquetas, enlace al artículo e imagen si aplica. Si no hay imagen, usar una composición visual CSS coherente o una card textual sobria.
- El Markdown para el chatbot debe ser una ficha muy resumida, no una copia del artículo: el chatbot la carga entera con la tool `read_blog_article` cuando le preguntan por el artículo. Empieza con frontmatter YAML obligatorio:

  ```markdown
  ---
  type: blog_post
  title: "<título del artículo>"
  route: "/blog/posts/<slug>.html"
  date: "AAAA-MM-DD"
  tags: ["Etiqueta 1", "Etiqueta 2"]
  summary: "<una frase: de qué trata; aparece en el índice del chatbot, el MCP y llms.txt>"
  ---
  ```

  Después: título H1, idea central, puntos clave, errores habituales y fuentes principales (sección final de "Fuentes"). Evitar ejemplos largos, bloques de código extensos, texto narrativo y secciones completas del HTML.
- Cada `##`/`###` de la ficha declara el `id` de la sección HTML que lo respalda: `## Idea central {#id-de-la-seccion}`. El chatbot cita cada párrafo con esa URL y `uv run pytest` falla si el ancla no existe en el HTML.
- Tras crear o editar la ficha, desde `CV/Chatbot` ejecutar `uv run python -m core.llms_txt` (regenera `/llms.txt`) y `uv run pytest`.
- Si el cambio afecta a lo que el chatbot responde, recordar en la PR que las evals (`uv run pytest -m evals`) solo las ejecuta un humano a mano. Ningún agente las lanza.
- Mantener el slug sincronizado entre `blog/posts/<slug>.html`, la tarjeta de `blog/index.html`, `CV/Chatbot/docs/blog/<slug>.md` y `blog/linkedin-drafts/<slug>.txt`.

## Fuentes

- Cada afirmación no trivial (datos, estudios, definiciones atribuidas, citas) lleva fuente primaria en la sección "Fuentes": documentación oficial, paper, post del autor original.
- Verificar cada URL antes de citarla (abrirla y comprobar que dice lo que se le atribuye). Si no se puede verificar, reformular la afirmación como opinión propia o quitarla. Nunca inventar títulos, autores ni URLs.
- En temas de IA, preferir fuentes con fecha y evitar cifras de benchmarks o productividad sin estudio concreto detrás.
- La experiencia propia no necesita fuente, pero solo se cuenta lo que el usuario ha aportado o ya es público en el CV.

## Diagrama

- `viewBox="0 0 1200 630"` con `width`/`height` iguales, `role="img"` y `<title>`/`<desc>` en castellano.
- Colores equivalentes a los tokens de `assets/tokens.css` (fondo oscuro, acentos azul/verde); el SVG es autocontenido, así que los valores van en hex copiados de los tokens, sin inventar paleta.
- Tipografía Inter (y JetBrains Mono para código), textos cortos y legibles a 600px de ancho: el diagrama se ve en móvil y en el feed de LinkedIn.
- Debe explicar el mecanismo central del artículo, no decorar.
- Conversión: `npm ci --prefix .agents/skills/manage-blog/scripts` (una vez) y `node .agents/skills/manage-blog/scripts/svg-to-png.mjs blog/assets/<slug>.svg blog/assets/<slug>.png`. Si no encuentra Chrome/Chromium, definir `CHROME_PATH`.

## Borradores de LinkedIn

- Crear siempre borradores en `blog/linkedin-drafts/<slug>.txt`, no `.md`, para cada artículo publicado.
- El archivo debe contener el texto final del post de LinkedIn, en texto plano y listo para copiar y pegar sin edición manual.
- No usar Markdown: evitar `[texto](url)`, `**negrita**`, encabezados Markdown, tablas, listas Markdown o `![imagen](url)`.
- Usar URL visible del artículo cuando exista publicación pública, por ejemplo `https://demetriotahoces.github.io/blog/posts/<slug>.html`.
- Estructura recomendada del borrador: gancho inicial, idea aprendida, 2-4 puntos breves en texto plano, cierre con pregunta o reflexión y hashtags moderados.
- Si hay imagen sugerida para LinkedIn, no mezclar notas editoriales dentro del `.txt`; el archivo debe seguir siendo copiable completo.
- La imagen sugerida para LinkedIn es `blog/assets/<slug>.png` (la misma que `og:image`); no duplicarla en `blog/linkedin-drafts/`.
- No generar automatizaciones ni publicar en LinkedIn.

## Validación

`python3 .agents/skills/manage-blog/scripts/check_post.py <slug>` (o `--all`) comprueba automáticamente:

- existen HTML, ficha `.md` y draft `.txt` con el mismo slug;
- canonical, `og:url`, OG/Twitter y JSON-LD `BlogPosting` coherentes, con imágenes existentes (avisa si son SVG);
- frontmatter de la ficha completo y `route` correcta; fecha igual en ficha, JSON-LD y tarjeta;
- enlaces relativos del post no rotos e `id` sin duplicar;
- tiempo de lectura declarado frente al estimado;
- sin em/en dash en el HTML ni en el draft; draft sin Markdown y con la URL pública;
- tarjeta en `blog/index.html`, orden por fecha y contador "N publicados";
- `?v=N` de assets iguales que en el índice.

Además, a mano:

- `uv run pytest` en `CV/Chatbot` (anclas `{#id}` de la ficha, frontmatter y `llms.txt` al día).
- Auditoría de `references/humanizer.md` sobre el artículo y el draft.
- Fuentes verificadas.
- Revisión visual con servidor estático (`python -m http.server 8000`) en escritorio y ancho móvil (~390px) cuando cambie HTML visible.
