# Ficha del chatbot

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
