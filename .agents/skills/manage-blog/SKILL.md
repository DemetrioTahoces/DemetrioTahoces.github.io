---
name: manage-blog
description: Crear, editar y mantener el blog técnico estático del CV de Demetrio Tahoces. Usar cuando se pidan nuevos artículos educativos en blog/posts, cambios en blog/index.html, copias Markdown para el chatbot en CV/Chatbot/docs/blog, actualización de tarjetas del blog, imágenes/metadatos de posts, o generación de borradores de LinkedIn listos para copiar y pegar desde contenido del blog.
---

# Manage Blog

Mantener `/blog/` como blog educativo separado del CV pero visualmente coherente con él. Sirve para compartir conocimiento técnico de trabajo o proyectos personales, sin mencionar la fuente de aprendizaje salvo petición explícita.

## Reparto: script o criterio

Todo lo que se pueda expresar como regla va a un script y no se repite aquí como instrucción para recordarla. El modelo se reserva lo que pide juicio.

| Lo hace un script | Lo hace el modelo |
|---|---|
| Esqueleto, tarjeta, contador y `?v=N` (`new_post.py`) | Tesis, esquema y redacción |
| Minutos y etiquetas de la tarjeta (`check_post.py --fix`) | Acordar los minutos con el usuario y ajustar el texto a su presupuesto de palabras |
| Metadatos, JSON-LD, anclas, enlaces, ids, orden del índice, ficha frente al post | Título, descripción SEO, resumen de la ficha |
| Marcadores sin sustituir, términos prohibidos, dashes, paleta del SVG, emojis (cuenta, marcado, repetición) | Qué emoji y dónde, tono, auditoría del humanizer |
| Enlaces de Fuentes vivos (`--check-urls`) | Que cada fuente diga lo que se le atribuye |
| SVG a PNG (`build_png.py`), `llms.txt`, tests, skills sincronizadas (`validate.py`, `sync_skills.py`) | Diseño del diagrama y revisión visual del PNG |

Detalle de cada script, CI y el hook de push: `references/automatizacion.md`.

## Artículo nuevo

0. **Briefing:** `references/briefing.md`. Sin idea definida, brainstorm con propuestas basadas en el CV y los posts, y encuesta para elegir. Siempre se pregunta cuántos minutos de lectura quiere y qué se puede contar públicamente. Todo en encuesta cerrada (máximo 4 preguntas por ronda), nunca listas abiertas por chat. No inventar experiencias, métricas ni anécdotas.
1. Leer `blog/index.html` y, si el tema toca experiencia profesional, la ficha de `CV/Chatbot/docs/` para respetar lo que es público.
2. Proponer título, slug, índice de secciones (con sus `id`), idea del diagrama, minutos objetivo con su presupuesto de palabras y los huecos de ejemplos. Ajustar antes de redactar.
3. Esqueleto: `python3 .agents/skills/manage-blog/scripts/new_post.py <slug> --title ... --tags A,B,C --minutes N`. Slug en minúsculas, ASCII y con guiones. Los `id` de sección son estables.
4. Redactar sustituyendo los marcadores `{{...}}` del post, la tarjeta, la ficha y el draft. Reglas de diseño y contenido: `references/diseno.md`.
5. Diagrama `blog/assets/<slug>.svg`: `references/diagrama.md`. PNG con `scripts/build_png.py <slug>` y revisarlo mirándolo.
6. Ficha del chatbot: `references/ficha-chatbot.md`. Draft de LinkedIn: `references/linkedin.md`.
7. Fuentes verificadas: `references/fuentes.md`.
8. Emojis, con el texto ya cerrado: `references/emojis.md`. Auditoría obligatoria de `references/humanizer.md` sobre el artículo y el draft.
9. Validar: `python3 .agents/skills/manage-blog/scripts/validate.py <slug> --minutes N [--forbid TERM ...] --check-urls --fix`. Sin errores; cada aviso se revisa a mano. Revisión visual opcional con `scripts/screenshot.mjs <slug>`.
10. Publicar: commit `feature(blog): ...` y push directo a `main` (AGENTS.md). Cerrar con el resumen de `references/briefing.md`: enlace, ejemplos hipotéticos, afirmaciones solo del briefing, minutos reales frente a los pedidos y evals pendientes (las ejecuta un humano).

## Editar un post publicado

`references/edicion.md`: ids estables, `dateModified`, qué resincronizar.

## Skills duplicadas

El original está en `.agents/skills/` y `.claude/skills/` es copia. Tras editar el original, `python3 .agents/skills/manage-blog/scripts/sync_skills.py`; CI falla si difieren.
