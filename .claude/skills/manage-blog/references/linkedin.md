# Borradores de LinkedIn

- Crear siempre borradores en `blog/linkedin-drafts/<slug>.txt`, no `.md`, para cada artículo publicado.
- El archivo debe contener el texto final del post de LinkedIn, en texto plano y listo para copiar y pegar sin edición manual.
- No usar Markdown: evitar `[texto](url)`, `**negrita**`, encabezados Markdown, tablas, listas Markdown o `![imagen](url)`.
- Usar URL visible del artículo cuando exista publicación pública, por ejemplo `https://demetriotahoces.github.io/blog/posts/<slug>.html`.
- Estructura recomendada del borrador: gancho inicial, idea aprendida, 2-4 puntos breves en texto plano, cierre con pregunta o reflexión y hashtags moderados.
- Emojis: entre 3 y 5 (lo normal, 4), repartidos, para dar un tono más personal y cercano. Dónde encajan y cuáles usar: `references/emojis.md`.
- Si hay imagen sugerida para LinkedIn, no mezclar notas editoriales dentro del `.txt`; el archivo debe seguir siendo copiable completo.
- La imagen sugerida para LinkedIn es `blog/assets/<slug>.png` (la misma que `og:image`); no duplicarla en `blog/linkedin-drafts/`.
- No generar automatizaciones ni publicar en LinkedIn.

## Envío por Gmail

Cada artículo nuevo termina enviando su draft a Gmail. Es parte del flujo, no hay que pedirlo.

- Cuándo: tras el push a `main`, para que el enlace público de la imagen ya resuelva (GitHub Pages tarda ~10 minutos; si aún no responde, el adjunto es la vía principal).
- Destinatario: `tonitahoces@gmail.com`. Herramienta: `mcp__Gmail__send_message` (cargarla con ToolSearch si está diferida).
- Asunto: `Draft LinkedIn: <título del post>`.
- Cuerpo (`body`, texto plano, sin Markdown): el contenido íntegro de `blog/linkedin-drafts/<slug>.txt`, tal cual, listo para copiar. Al final, tras una línea en blanco, `Imagen: https://demetriotahoces.github.io/blog/assets/<slug>.png`.
- Imagen: adjuntar `blog/assets/<slug>.png` en `attachments` (base64, `mimeType: image/png`, `filename: <slug>.png`, no inline). Si no se puede adjuntar (herramienta sin adjuntos, error o más de 25 MB), enviar solo con el enlace público de arriba e indicarlo en el informe final.
- Si Gmail no está disponible, no bloquear la publicación: dejarlo dicho en el resumen final para que el usuario lo reenvíe.
- Solo para artículos nuevos; las ediciones de posts publicados no reenvían el draft salvo petición.
- No se publica nada en LinkedIn (regla anterior).
