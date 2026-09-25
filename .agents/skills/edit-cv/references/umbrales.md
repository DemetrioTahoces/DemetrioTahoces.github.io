# Umbrales de tamaño por componente

Todas las secciones del CV usan los mismos componentes HTML. Estos umbrales mantienen el tamaño parecido entre tarjetas: una puede destacar un poco, pero ninguna debe triplicar a las demás. Se cuentan caracteres de texto visible, espacios incluidos. Los valores salen del CV real de septiembre de 2026: las tarjetas normales iban de 75 a 598 caracteres en total.

Comprobar siempre tras editar (solo stdlib):

```bash
python3 .agents/skills/edit-cv/scripts/check_cv.py
```

Errores = se supera un máximo; no cerrar el cambio así. Avisos = por debajo de un mínimo orientativo; revisar, pero no bloquean.

## Tarjeta de contribución (`CV/*.html`, `.detail-card` con `h3`)

| Medida | Normal | Destacada |
|---|---|---|
| Subtítulo (`p.text-gray-400` bajo el `h3`) | ≤ 100 | ≤ 130 |
| Nº de bullets | 2–4 | 2–5 |
| Cada bullet | 80–170 orientativo, máx. 200 | máx. 220 |
| Total de bullets | ≤ 550 | ≤ 900 |

- **Destacada**: atributo `data-featured` en el `div` de la tarjeta, **como mucho una por página**. Sirve para el logro más diferencial de esa experiencia (hoy, `fermax.html#desarrollo-agentico`). El atributo no cambia el estilo, solo el umbral.
- Todas las páginas de detalle (experiencia y formación, `CV/tfg.html` incluido) usan este componente: sección con `h2` fuera de las tarjetas y dentro `.detail-card` con icono, `h3`, subtítulo y bullets. No crear tarjetas de sección con el `h2` dentro y listas largas; el script no las mide.

## Descripción de job-card (`index.html#experiencia`)

- Normal: ≤ 170 caracteres.
- Experiencia actual (fecha con "Presente"): ≤ 250.
- La home resume en una o dos frases; el detalle va a la página de `CV/`.

## Bloque Contexto (`CV/*.html#contexto`)

- 250–450 caracteres, orientativo (aviso, no error).

## Qué hacer si no cabe

1. Condensar la redacción antes de quitar hechos: fundir bullets del mismo tema, quitar muletillas ("lo que permitió", "cabe destacar"), cambiar enumeraciones largas por paréntesis.
2. Si aún no cabe, el detalle se queda en el documento RAG (`CV/Chatbot/docs/*.md`), que **no tiene umbrales**. El chatbot sigue respondiendo con todo y la web resume.
3. No crear una segunda tarjeta destacada ni subir umbrales para que quepa. Si una experiencia necesita más espacio de forma justificada, preguntar al usuario.

Recortar para cumplir el umbral es la excepción a la regla aditiva del SKILL.md: se puede condensar la web sin petición explícita siempre que ningún hecho desaparezca de todas las superficies (web + RAG).
