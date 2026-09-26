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

- Entre 2 y 4 por artículo (`check_post.py` avisa por encima de 4). Si no hay dos sitios donde encajen de verdad, basta con uno.
- Solo dentro de `.article-prose`, en dos sitios:
  - Al principio del `h2` de un callout o warning, anticipando su función: 💡 Regla pragmática, ⚠️ El ejemplo usa RabbitMQ, ✅ Checklist pragmático.
  - Al final de un párrafo cuya última frase tenga carga personal o sea lo que conviene recordar: la escena inicial, una lección aprendida, el cierre de la conclusión. Uno o dos en toda la prosa.
- En el resto de la prosa, ninguno: ni en los `h2`/`h3` de secciones normales (el esqueleto del artículo queda limpio), ni como viñetas (la lista HTML ya las tiene), ni en código, tablas, enlaces o fuentes.
- Fuera de la prosa, tampoco: `<title>`, metadatos, JSON-LD, hero, grids de resumen, `alt` y diagrama (SVG/PNG), tarjeta de `blog/index.html` y ficha del chatbot. Los metadatos salen en buscadores y previsualizaciones, la tarjeta repite el título del post y en la ficha solo meten ruido en el contexto del chatbot.
- Marcado: decorativo, oculto a lectores de pantalla y separado del texto por un espacio. Por eso el texto debe bastar sin el emoji: lo que solo dijera el emoji, un lector de pantalla no lo leería.

  ```html
  <h2 class="mt-0"><span aria-hidden="true">💡</span> Regla pragmática</h2>
  <p>... Una suposición que se cuela en la primera vuelta se paga en todas las siguientes. <span aria-hidden="true">📌</span></p>
  ```

## Draft de LinkedIn (`blog/linkedin-drafts/<slug>.txt`)

- Entre 2 y 4 en todo el post (`check_post.py` avisa por encima de 4).
- Dónde encajan: al final del gancho o de una frase con carga personal, como marcador de los 2-4 puntos breves (en lugar de guiones) o junto a la URL del artículo.
- Texto plano, sin marcado, y nunca en los hashtags.
