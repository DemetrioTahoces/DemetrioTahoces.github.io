# Diagrama del artículo

- `viewBox="0 0 1200 630"` con `width`/`height` iguales, `role="img"` y `<title>`/`<desc>` en castellano.
- Colores equivalentes a los tokens de `assets/tokens.css` (fondo oscuro, acentos azul/verde); el SVG es autocontenido, así que los valores van en hex copiados de los tokens, sin inventar paleta.
- Tipografía Inter (y JetBrains Mono para código), textos cortos y legibles a 600px de ancho: el diagrama se ve en móvil y en el feed de LinkedIn.
- Debe explicar el mecanismo central del artículo, no decorar.
- Conversión: `npm ci --prefix .agents/skills/manage-blog/scripts` (una vez) y `node .agents/skills/manage-blog/scripts/svg-to-png.mjs blog/assets/<slug>.svg blog/assets/<slug>.png`. Si no encuentra Chrome/Chromium, definir `CHROME_PATH`.
- Revisar siempre el PNG generado (abrirlo como imagen). `svg-to-png.mjs` carga Inter y JetBrains Mono desde Google Fonts; si la red las bloquea, usa fuentes de sistema más anchas y el texto puede solaparse. En ese caso, dar más margen a los textos o generar el PNG en un entorno con acceso a Google Fonts.
