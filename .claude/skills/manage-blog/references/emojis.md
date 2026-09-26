# Emojis en el blog

Pocos y discretos, en el artículo y en el draft de LinkedIn. Dan un tono más personal y ayudan a orientarse en la lectura; si un emoji solo decora, se quita. El sitio es un CV técnico con tema oscuro y sobrio: dos emojis de más bastan para que un artículo suene a post de marketing.

## Reglas comunes

- El texto se entiende igual sin el emoji: nunca sustituye una palabra ni aporta información que no esté ya en la frase.
- Como mucho uno por bloque (sección, párrafo o punto) y nunca varios seguidos.
- Cada emoji tiene una función y se repite poco. Vocabulario de referencia:
  - 💡 idea o regla práctica
  - ⚠️ advertencia, límite o matiz
  - ✅ checklist o criterio de terminado
  - 📌 lo que conviene recordar
  - 🔍 detalle o ejemplo concreto
  - 🛠️ práctica: cómo aplicarlo
  - 🤔 pregunta o reflexión abierta
  - 👇 enlace al artículo (solo en LinkedIn)
- Evitar 🚀🔥💯🙌🎉✨💪, caras exageradas y cualquier emoji que funcione como eslogan: suenan a marketing.

## Artículo (`blog/posts/<slug>.html`)

- Entre 2 y 4 por artículo: lo normal son 3, y 4 solo en artículos largos (7-8 min) cuando el cuarto marca algo que el lector no debería saltarse. `check_post.py` avisa por encima de 4.
- Solo dentro de `.article-prose`, en dos sitios:
  - Al principio del `h2` de un callout o warning, anticipando su función: 💡 Regla pragmática, ⚠️ El ejemplo usa RabbitMQ, ✅ Checklist pragmático. Son el ancla natural: si el artículo tiene callouts, se empieza por ellos.
  - Al final de un párrafo clave, tras el punto: el que cierra la escena inicial, el que concentra la regla de una sección, la parte práctica o el cierre de la conclusión. Uno o dos en toda la prosa.
- En el resto de la prosa, ninguno: ni en los `h2`/`h3` de secciones normales (el esqueleto del artículo queda limpio), ni como viñetas (la lista HTML ya las tiene), ni en código, tablas, enlaces o fuentes.
- Fuera de la prosa, tampoco: `<title>`, metadatos, JSON-LD, hero, grids de resumen, `alt` y diagrama (SVG/PNG), tarjeta de `blog/index.html` y ficha del chatbot. Los metadatos salen en buscadores y previsualizaciones, la tarjeta repite el título del post y en la ficha solo meten ruido en el contexto del chatbot.
- Marcado: decorativo y oculto a lectores de pantalla, así que el texto debe bastar sin el emoji: lo que solo dijera el emoji, un lector de pantalla no lo leería. En un `h2` va seguido de un espacio; al final de un párrafo, unido a la última palabra con `&nbsp;` para que nunca quede solo en una línea.

  ```html
  <h2 class="mt-0"><span aria-hidden="true">💡</span> Regla pragmática</h2>
  <p>... si mañana cambia esta regla, ¿cuánto código arrastra detrás?&nbsp;<span aria-hidden="true">🤔</span></p>
  ```

### Cómo colocarlos

Al montar el artículo, los emojis van al final, con el texto ya cerrado: su sitio depende de la estructura definitiva y no deben condicionar la redacción.

1. Marcar los candidatos: los `h2` de callouts y warnings y los párrafos clave.
2. Quedarse con los que señalan lo que el lector no debería saltarse, repartidos a lo largo del artículo y nunca en bloques contiguos: quien hace scroll debe encontrarlos como hitos, no en racimo.
3. Elegir cada emoji por su función según el vocabulario, sin repetir dentro del artículo.
4. Releer cada frase con su emoji: si choca con lo que dice (un ✅ detrás de "se salta la revisión"), no orienta o no añade cercanía, se quita.

## Draft de LinkedIn (`blog/linkedin-drafts/<slug>.txt`)

- Entre 2 y 4 en todo el post (`check_post.py` avisa por encima de 4).
- Dónde encajan: al final del gancho o de una frase con carga personal, como marcador de los 2-4 puntos breves (en lugar de guiones) o junto a la URL del artículo.
- Texto plano, sin marcado, y nunca en los hashtags.
