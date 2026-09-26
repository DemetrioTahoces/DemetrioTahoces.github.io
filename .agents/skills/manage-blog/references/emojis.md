# Emojis en el blog

Pocos, discretos y distintos en cada texto. Dan un tono más personal y ayudan a orientarse en la lectura; si un emoji solo decora, se quita. El sitio es un CV técnico con tema oscuro y sobrio: un emoji de más basta para que un artículo suene a post de marketing, y los mismos en todos los posts acaban pareciendo una plantilla.

## Reglas comunes

- El texto se entiende igual sin el emoji: nunca sustituye una palabra ni aporta información que no esté ya en la frase.
- Como mucho uno por bloque (sección, párrafo o punto) y nunca varios seguidos.
- Se elige por lo que dice el texto, no de una lista fija: un objeto o una idea de la propia frase. Ejemplos de los posts publicados: 🌙 "cuando algo falla a las tres de la mañana", 📬 "merece su propia cola", 💧 "como una gotera", 🔑 dónde decide el humano (permisos y despliegues), 🧰 las herramientas de cada agente, 🧭 preguntas para orientarse antes de aplicar un principio.
- Variedad: antes de elegir, mirar los que ya llevan los posts publicados (`grep -oh 'class="emoji"[^<]*' blog/posts/*.html`) y no repetirlos salvo que el contenido lo pida. Los genéricos (💡 ⚠️ ✅ 📌 🤔) son el último recurso, no la opción por defecto.
- Evitar 🚀🔥💯🙌🎉✨💪, caras exageradas y cualquier emoji que funcione como eslogan: suenan a marketing.

## Artículo (`blog/posts/<slug>.html`)

- Entre 1 y 3 por artículo: lo normal son 2, y 3 solo en artículos largos (7-8 min) cuando el tercero marca algo que el lector no debería saltarse. `check_post.py` avisa por encima de 3.
- Solo dentro de `.article-prose`, en dos sitios:
  - Al final de un párrafo clave, tras el punto: el que cierra la escena inicial, el que concentra la regla de una sección, la parte práctica o el cierre de la conclusión.
  - Al principio del `h2` de un callout o warning, anticipando su contenido. Como mucho uno por artículo: en un título pesa más que en un párrafo.
- En el resto de la prosa, ninguno: ni en los `h2`/`h3` de secciones normales (el esqueleto del artículo queda limpio), ni como viñetas (la lista HTML ya las tiene), ni en código, tablas, enlaces o fuentes.
- Fuera de la prosa, tampoco: `<title>`, metadatos, JSON-LD, hero, grids de resumen, `alt` y diagrama (SVG/PNG), tarjeta de `blog/index.html` y ficha del chatbot. Los metadatos salen en buscadores y previsualizaciones, la tarjeta repite el título del post y en la ficha solo meten ruido en el contexto del chatbot.
- Marcado: `<span class="emoji" aria-hidden="true">`. La clase los reduce y les baja la saturación (`assets/blog.css`) para que se lean como un acento y no como un icono. `aria-hidden` los oculta a lectores de pantalla, así que el texto debe bastar sin ellos. En un `h2` va seguido de un espacio; al final de un párrafo, unido a la última palabra con `&nbsp;` para que nunca quede solo en una línea.

  ```html
  <h2 class="mt-0"><span class="emoji" aria-hidden="true">🧭</span> Regla pragmática</h2>
  <p>... y no atraviese todo el sistema como una gotera.&nbsp;<span class="emoji" aria-hidden="true">💧</span></p>
  ```

### Cómo colocarlos

Al montar el artículo, los emojis van al final, con el texto ya cerrado: su sitio depende de la estructura definitiva y no deben condicionar la redacción.

1. Marcar los candidatos: los párrafos clave y los `h2` de callouts y warnings.
2. Quedarse con 1-3 (lo normal, 2) que señalen lo que el lector no debería saltarse, repartidos a lo largo del artículo y nunca en bloques contiguos: quien hace scroll debe encontrarlos como hitos, no en racimo.
3. Elegir cada emoji por lo que dice su frase, distinto de los de los posts publicados y sin repetir dentro del artículo.
4. Releer cada frase con su emoji: si choca con lo que dice (un ✅ detrás de "se salta la revisión"), no orienta o no añade cercanía, se quita.

## Draft de LinkedIn (`blog/linkedin-drafts/<slug>.txt`)

- Entre 2 y 4 en todo el post (`check_post.py` avisa por encima de 4).
- Dónde encajan: al final del gancho o de una frase con carga personal, como marcador de los 2-4 puntos breves (en lugar de guiones) o junto a la URL del artículo (👇).
- Texto plano, sin marcado, y nunca en los hashtags.
