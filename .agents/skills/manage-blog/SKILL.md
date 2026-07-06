---
name: manage-blog
description: Crear, editar y mantener el blog técnico estático del CV de Demetrio Tahoces. Usar cuando se pidan nuevos artículos educativos en blog/posts, cambios en blog/index.html, copias Markdown para el chatbot en CV/Chatbot/docs/blog, actualización de tarjetas del blog, imágenes/metadatos de posts, o generación de borradores de LinkedIn listos para copiar y pegar desde contenido del blog.
---

# Manage Blog

## Overview

Mantener la sección `/blog/` como blog educativo separado del CV pero visualmente coherente con él. El blog sirve para almacenar y compartir conocimiento técnico adquirido en trabajo o proyectos personales, sin mencionar la fuente de aprendizaje salvo petición explícita.

## Workflow

1. Leer `blog/index.html`, el artículo relacionado si existe y `index.html` solo si la navegación principal puede verse afectada.
2. Para un artículo nuevo, crear `blog/posts/<slug>.html` con HTML estático. Usar slug en minúsculas, ASCII y palabras separadas por guiones.
3. Actualizar manualmente `blog/index.html` con una tarjeta por artículo publicado. No introducir manifest JSON, bundler ni renderizado obligatorio por JavaScript.
4. Crear o actualizar siempre la versión Markdown del artículo en `CV/Chatbot/docs/blog/<slug>.md` para que el chatbot pueda consultarlo sin cambios de código.
5. Si el artículo usa imagen, guardar el asset en `blog/assets/` y referenciarlo desde la tarjeta, el artículo y los metadatos OG/Twitter.
6. Crear o actualizar siempre `blog/linkedin-drafts/<slug>.txt` con el texto final para LinkedIn, listo para copiar y pegar.
7. Leer `references/humanizer.md` y pasar obligatoriamente el artículo HTML y el draft de LinkedIn por esa auditoría antes de cerrar.
8. Verificar enlaces relativos, metadatos, responsive básico, coherencia visual con el CV, disponibilidad del Markdown para el chatbot y existencia del borrador de LinkedIn.

## Diseño y Contenido

- Mantener el patrón del CV: HTML inline, Tailwind CDN, fuente Inter, tema oscuro, fondo con grid sutil, cards translúcidas, acentos azul/verde y navegación accesible.
- No añadir dependencias front-end, build step, framework ni hojas CSS separadas salvo instrucción explícita.
- Escribir en castellano profesional, educativo, directo y sobrio. Evitar marketing vacío, exageraciones y claims no defendibles.
- No mencionar empresa, cliente, compañero, curso, fuente concreta o contexto laboral sensible salvo que el usuario lo pida expresamente.
- Mantener artículos orientados a aprendizaje: problema, contexto técnico, explicación, tradeoffs, ejemplo práctico y conclusiones accionables.
- Mantener cada artículo en una lectura aproximada de 5-8 minutos. Priorizar claridad y utilidad sobre exhaustividad; no abrumar al lector con ejemplos largos, listas excesivas o desarrollo enciclopédico.
- Hacer que cada artículo sea ameno y humano: abrir con una situación reconocible, pero con contexto técnico inmediato y sin ambigüedades de lectura. Usar ejemplos de desarrollo cotidiano o vida real, variar el ritmo y sostener una opinión técnica clara.
- Cada post debe incluir título, descripción, fecha, etiquetas, tiempo estimado de lectura si aplica, enlaces de vuelta al blog/CV y metadatos SEO/OG.
- Cada tarjeta del listado debe incluir título, descripción breve, fecha, etiquetas, enlace al artículo e imagen si aplica. Si no hay imagen, usar una composición visual CSS coherente o una card textual sobria.
- El Markdown para el chatbot debe ser una ficha RAG muy resumida, no una copia del artículo. Objetivo: bajo consumo de tokens al inyectarse en contexto. Mantener título H1, descripción, fecha, etiquetas, URL pública, idea central, puntos clave, errores habituales y fuentes principales (sección final de "Fuentes"). Evitar ejemplos largos, bloques de código extensos, texto narrativo y secciones completas del HTML.
- Mantener el slug sincronizado entre `blog/posts/<slug>.html`, la tarjeta de `blog/index.html`, `CV/Chatbot/docs/blog/<slug>.md` y `blog/linkedin-drafts/<slug>.txt`.

## Borradores de LinkedIn

- Crear siempre borradores en `blog/linkedin-drafts/<slug>.txt`, no `.md`, para cada artículo publicado.
- El archivo debe contener el texto final del post de LinkedIn, en texto plano y listo para copiar y pegar sin edición manual.
- No usar Markdown: evitar `[texto](url)`, `**negrita**`, encabezados Markdown, tablas, listas Markdown o `![imagen](url)`.
- Usar URL visible del artículo cuando exista publicación pública, por ejemplo `https://demetriotahoces.github.io/blog/posts/<slug>.html`.
- Estructura recomendada del borrador: gancho inicial, idea aprendida, 2-4 puntos breves en texto plano, cierre con pregunta o reflexión y hashtags moderados.
- Si hay imagen sugerida para LinkedIn, no mezclar notas editoriales dentro del `.txt`; el archivo debe seguir siendo copiable completo.
- No generar automatizaciones ni publicar en LinkedIn.

## Validación

- Revisar que las rutas relativas funcionan desde `/blog/` y desde `/blog/posts/`.
- Comprobar que el listado no enlaza a posts inexistentes.
- Comprobar que `CV/Chatbot/docs/blog/<slug>.md` existe para cada artículo publicado, que el chatbot lo descubrirá como documento `blog/<slug>` y que está resumido para RAG, no duplicado del artículo HTML.
- Comprobar que `blog/linkedin-drafts/<slug>.txt` existe, no está vacío y contiene un post final de LinkedIn con la URL pública del artículo.
- Comprobar que el artículo y el draft han pasado la auditoría de `references/humanizer.md`.
- Probar con un servidor estático local cuando se modifique HTML visible.
- Validar que los borradores de LinkedIn son copiables completos sin edición manual.
