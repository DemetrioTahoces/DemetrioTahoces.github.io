# Editar un post publicado

Aplica cuando se cambia contenido de un post que ya está en `main` (no a correcciones dentro de la PR que lo crea).

1. Leer el post, su ficha `CV/Chatbot/docs/blog/<slug>.md`, su draft `blog/linkedin-drafts/<slug>.txt` y la tarjeta en `blog/index.html`.
2. Los `id` de sección son estables: no se renombran aunque cambie el título. Una sección nueva lleva un `id` nuevo; una sección eliminada se quita también de la ficha.
3. Si cambia el contenido, actualizar `dateModified` en el JSON-LD. `datePublished`, la fecha visible, la fecha de la tarjeta y el `date` de la ficha no cambian.
4. Resincronizar lo que dependa del cambio: ficha (ideas y anclas `{#id}`), tiempo de lectura (post y tarjeta), descripción de la tarjeta y metadatos si cambia el enfoque, y draft de LinkedIn solo si aún no se ha publicado.
5. Si cambia el diagrama, regenerar el PNG y revisarlo (ver `diagrama.md`).
6. Pasar el humanizer sobre el texto nuevo, `check_post.py <slug>`, y desde `CV/Chatbot` `uv run python -m core.llms_txt` + `uv run pytest`.
7. Actualizar la entrada de `context.md`.

Metadatos técnicos sin cambio de contenido (una ruta de imagen, una versión `?v=N`) no tocan `dateModified`.
