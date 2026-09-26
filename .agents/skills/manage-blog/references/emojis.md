# Emojis en el blog

Repartidos por el artículo y distintos en cada texto. Dan un tono más personal y funcionan como hitos: quien hace scroll encuentra uno en cada sección importante. Con 1-3 por artículo pasaban desapercibidos, así que el objetivo es más o menos uno por sección principal. El límite sigue ahí: el sitio es un CV técnico con tema oscuro y sobrio, un racimo de emojis basta para que un artículo suene a post de marketing, y los mismos en todos los posts acaban pareciendo una plantilla. Si un emoji solo decora, se quita.

## Reglas comunes

- El texto se entiende igual sin el emoji: nunca sustituye una palabra ni aporta información que no esté ya en la frase.
- Como mucho uno por sección (`<section>` con `id`) y nunca en dos párrafos seguidos.
- Se elige por lo que dice el texto, no de una lista fija: un objeto o una idea de la propia frase. Ejemplos de los posts publicados: 🌙 "cuando algo falla a las tres de la mañana", 📬 "merece su propia cola", 🐇 el aviso de que el ejemplo usa RabbitMQ, 💧 "como una gotera", 🐧 el pingüino que no vuela, ☕ "si solo quieres un café", 🔌 "los adaptadores se enchufan fuera", 🔑 dónde decide el humano (permisos y despliegues), 👀 "ya no queda nadie mirando el conjunto", ⏳ "cada vuelta cuesta tiempo y tokens".
- Variedad: antes de elegir, mirar los que ya llevan los posts publicados (`grep -oh 'class="emoji"[^<]*' blog/posts/*.html`) y no repetirlos salvo que el contenido lo pida. Los genéricos (💡 ⚠️ ✅ 📌 🤔) son el último recurso, no la opción por defecto.
- Evitar 🚀🔥💯🙌🎉✨💪, caras exageradas y cualquier emoji que funcione como eslogan: suenan a marketing.

## Artículo (`blog/posts/<slug>.html`)

- Entre 4 y 7 por artículo: lo normal son 5-6, más o menos uno por sección principal; 7 solo en artículos largos (7-8 min) con muchas secciones. No hace falta cubrir todas: las de fuentes, las muy cortas o las que son sobre todo código o tablas se quedan sin él. `check_post.py` avisa por debajo de 4 y por encima de 7.
- Solo dentro de `.article-prose`, en dos sitios:
  - Al final de un párrafo clave, tras el punto: el que cierra la escena inicial, el que concentra la regla de cada sección, la parte práctica o el cierre de la conclusión. Nunca tras un párrafo que termina en dos puntos para abrir una lista o un bloque de código.
  - Al principio del `h2` de un callout o warning, anticipando su contenido. Como mucho uno por artículo: en un título pesa más que en un párrafo.
- En el resto de la prosa, ninguno: ni en los `h2`/`h3` de secciones normales (el esqueleto del artículo queda limpio), ni como viñetas (la lista HTML ya las tiene), ni en código, tablas, enlaces o fuentes.
- Fuera de la prosa, tampoco: `<title>`, metadatos, JSON-LD, hero, grids de resumen, `alt` y diagrama (SVG/PNG) y tarjeta de `blog/index.html`. Los metadatos salen en buscadores y previsualizaciones, y la tarjeta repite el título del post.
- Nunca en los Markdown del chatbot (`CV/Chatbot/docs/`, incluida la ficha del post) ni en `llms.txt`: son contexto del modelo y ahí solo meten ruido. `check_post.py` y `uv run pytest` fallan si aparece alguno.
- Marcado: `<span class="emoji" aria-hidden="true">`. La clase los reduce y les baja la saturación (`assets/blog.css`) para que se lean como un acento y no como un icono. `aria-hidden` los oculta a lectores de pantalla, así que el texto debe bastar sin ellos. En un `h2` va seguido de un espacio; al final de un párrafo, unido a la última palabra con `&nbsp;` para que nunca quede solo en una línea.

  ```html
  <h2 class="mt-0"><span class="emoji" aria-hidden="true">🧭</span> Regla pragmática</h2>
  <p>... y no atraviese todo el sistema como una gotera.&nbsp;<span class="emoji" aria-hidden="true">💧</span></p>
  ```

### Cómo colocarlos

Al montar el artículo, los emojis van al final, con el texto ya cerrado: su sitio depende de la estructura definitiva y no deben condicionar la redacción.

1. Marcar los candidatos: los párrafos clave y los `h2` de callouts y warnings.
2. Quedarse con 4-7 (lo normal, 5-6), uno por sección como mucho, en el párrafo que el lector no debería saltarse de cada una, repartidos a lo largo del artículo y nunca en bloques contiguos: quien hace scroll debe encontrarlos como hitos, no en racimo.
3. Elegir cada emoji por lo que dice su frase, distinto de los de los posts publicados y sin repetir dentro del artículo.
4. Releer cada frase con su emoji: si choca con lo que dice (un ✅ detrás de "se salta la revisión"), no orienta o no añade cercanía, se quita.

## Draft de LinkedIn (`blog/linkedin-drafts/<slug>.txt`)

- Entre 3 y 5 en todo el post (lo normal, 4), sin dos en líneas seguidas. `check_post.py` avisa por debajo de 3 y por encima de 5.
- Dónde encajan: al final del gancho o de una frase con carga personal, como marcador de los puntos breves (en lugar de guiones; cuentan todos para el total) o junto a la URL del artículo (👇).
- Texto plano, sin marcado, y nunca en los hashtags.
