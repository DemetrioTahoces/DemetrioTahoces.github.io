# Contexto de sesiones

Traspaso entre sesiones de agentes. Cada cambio o PR actualiza su entrada (regla en `AGENTS.md`, sección "Contexto entre sesiones"). Entradas de la más reciente a la más antigua. Cuando una PR se mergea o se cierra, su entrada se reduce a un resumen de dos o tres líneas.

---

## PR #19: mejora de la skill manage-blog y post de flujos agénticos

- Rama: `claude/blog-post-generation-skill-x19nsv`. Issue: #17. Estado: abierta, CI verde, esperando revisión del autor.
- Última actualización: 2026-09-24.

### Qué se ha hecho

- Skill `.agents/skills/manage-blog` mejorada: paso 0 de briefing y paso 2 de propuesta de índice, `references/post-template.html`, `scripts/check_post.py` (validador sin dependencias), OG/Twitter en PNG, `svg-to-png.mjs` encuentra Chromium en Linux/Playwright, reglas de fuentes verificadas y pautas de diagrama.
- `.claude/skills/{manage-blog,edit-cv}`: enlaces simbólicos a `.agents/skills/` para que Claude Code descubra las skills. Se edita siempre el original.
- Post de prueba `flujos-agenticos-desarrollo-ia` con todas sus superficies: `blog/posts/…html`, `blog/assets/…{svg,png}`, tarjeta en `blog/index.html`, `CV/Chatbot/docs/blog/…md`, `blog/linkedin-drafts/…txt` y `llms.txt` regenerado.

### Siguiente sesión: sustituir ejemplos genéricos del post

El autor aportará ejemplos reales. Briefing ya cerrado (no volver a preguntarlo):

- Tesis: "el humano decide, el agente ejecuta". Público: devs que ya usan IA. Lectura objetivo: ~5 min (3-8 permitido).
- Inspiración: el flujo de desarrollo agéntico descrito en `CV/Chatbot/docs/FERMAX.md` (sección `desarrollo-agentico`).
- Restricciones: no nombrar la empresa; no incluir cifras ni métricas; no revelar el diseño interno que la ficha marca como no público (reparto concreto de agentes, criterios de salida del bucle, forma de las skills). No inventar experiencias: solo lo que aporte el autor.

Ejemplos genéricos actuales, candidatos a sustituir (ids estables, no cambiarlos):

| Sección (`id`) | Ejemplo genérico actual |
| --- | --- |
| `la-escena-tipica` | Agente añade un endpoint REST: 600 líneas en 3 minutos, log con otro formato, 500 en validación, consulta sin índice. |
| `definir-antes-de-delegar` | Definición del mismo endpoint: códigos HTTP por error, formato de log, tests de caso feliz y validación. |
| `implementacion-repartida` | Reparto dominio / adaptador REST / tests. |
| `el-bucle` | Sin ejemplo; solo reglas (hallazgos solo de corrección, limitar vueltas). |
| `skills-conocimiento-del-equipo` | Enlaza con el log y el 500 de la escena inicial; temas de skills tomados de la ficha pública. |
| `limites` | "Renombrar una variable no necesita cuatro agentes". |

Si cambian los ejemplos, revisar también: el draft de LinkedIn (reutiliza la escena de las 600 líneas), la ficha del chatbot si cambia alguna idea y el tiempo de lectura declarado (post y tarjeta).

Cierre obligatorio tras editar:

1. Auditoría de `.agents/skills/manage-blog/references/humanizer.md` sobre post y draft.
2. `python3 .agents/skills/manage-blog/scripts/check_post.py flujos-agenticos-desarrollo-ia` sin errores.
3. Desde `CV/Chatbot`: `uv run python -m core.llms_txt` y `uv run pytest`.
4. Actualizar esta entrada.

### Decisiones pendientes del autor

Mejoras de la skill propuestas y no hechas todavía:

1. Partir `SKILL.md` y mover LinkedIn, diagrama, fuentes y ficha a `references/` (carga bajo demanda).
2. Revisión léxica del humanizer en `check_post.py` (palabras y fórmulas vetadas, exceso de negritas).
3. `check_post.py`: anclas `{#id}` de la ficha, etiquetas y minutos coherentes entre post, tarjeta y ficha.
4. Script de capturas escritorio/móvil dentro de la skill.
5. Flujo de edición de posts publicados (`dateModified`, ids estables, resincronizar ficha y draft).
6. Migrar a OG PNG los dos posts antiguos. Toca contenido publicado: requiere el visto bueno del autor.
7. Ejecutar `check_post.py --all` en CI. Cambia la política "el frontend no tiene CI": requiere el visto bueno del autor.

Además, evaluar la skill con dos o tres peticiones distintas (post nuevo, edición, solo draft).

### Notas de entorno (sesiones cloud)

- El proxy bloquea `cdn.tailwindcss.com`, Google Fonts, `metr.org` y `arxiv.org`. Las capturas salen sin Tailwind (la imagen desborda en móvil también en posts antiguos): la revisión visual real se hace en local o en GitHub Pages.
- El `uv` preinstalado (0.8.x) solo conoce Python 3.14.0rc2, incompatible con pydantic. Solución usada: instalar un uv reciente con `pip install --target <scratchpad> uv` y ejecutar con ese binario.
- Chromium está en `/opt/pw-browsers/chromium`; `npm ci --prefix .agents/skills/manage-blog/scripts` instala `puppeteer-core`.
- Evals del chatbot: no ejecutadas. Solo las lanza un humano.
