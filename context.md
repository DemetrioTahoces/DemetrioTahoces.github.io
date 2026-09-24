# Contexto de sesiones

Traspaso entre sesiones de agentes. Cada cambio o PR actualiza su entrada (regla en `AGENTS.md`, sección "Contexto entre sesiones"). Entradas de la más reciente a la más antigua. Cuando una PR se mergea o se cierra, su entrada se reduce a un resumen de dos o tres líneas.

---

## PR #19: mejora de la skill manage-blog y post de flujos agénticos

- Rama: `claude/blog-post-generation-skill-x19nsv`. Issue: #17. Estado: abierta, CI verde, esperando revisión del autor.
- Última actualización: 2026-09-24 (post reescrito con el patrón fábrica de tareas).

### Qué se ha hecho

- Skill `.agents/skills/manage-blog` mejorada: paso 0 de briefing y paso 2 de propuesta de índice, `references/post-template.html`, `scripts/check_post.py` (validador sin dependencias), OG/Twitter en PNG, `svg-to-png.mjs` encuentra Chromium en Linux/Playwright, reglas de fuentes verificadas y pautas de diagrama.
- `.claude/skills/{manage-blog,edit-cv}`: enlaces simbólicos a `.agents/skills/` para que Claude Code descubra las skills. Se edita siempre el original.
- Post `flujos-agenticos-desarrollo-ia` con todas sus superficies: `blog/posts/…html`, `blog/assets/…{svg,png}`, tarjeta en `blog/index.html`, `CV/Chatbot/docs/blog/…md`, `blog/linkedin-drafts/…txt` y `llms.txt` regenerado.

### Post reescrito sobre el patrón "fábrica de tareas" (2026-09-24)

El autor compartió en la sesión el plugin privado de su equipo (skill `task-factory`) como referencia. El material **no está en el repo** ni debe entrar. Decisiones del autor, no volver a preguntarlas:

- Publicar el **patrón, sin internos**: nada de nombres de agentes, herramientas, repos, gestores de tareas, credenciales, modelos concretos ni empresa. Lectura ~5 min.
- Ideas del patrón que recoge el post (ids estables): escena inicial (`la-escena-tipica`), orquestador que no programa y subagentes nuevos por fase (`un-orquestador-que-no-programa`), spec en disco como contrato leída por ruta y fuera del repo (`la-spec-como-contrato`), un implementador por capa hexagonal sin investigar y verificado por script (`implementar-por-capas`), puerta determinista y verificación en paralelo (`puertas-y-verificacion`), triage con tres destinos, definición de "terminado" y máximo de cinco vueltas (`el-triage`), puntos de decisión humana (`donde-decide-el-humano`), límites (`limites`).
- `CV/Chatbot/docs/FERMAX.md`: la frase de "no documentado públicamente" se cambió por "el patrón general está en el blog; los detalles del equipo no se publican". El post no nombra la empresa ni la ficha enlaza el post (decisión conservadora; el autor puede pedir enlazarlos).

- Paso final humano (indicado por el autor): verificar y aceptar el desarrollo, revisar la PR y decidir la promoción a preproducción y producción. El bucle solo despliega en desarrollo. Reflejado en el callout `donde-decide-el-humano`, el diagrama, la ficha y el draft.

Pendiente del autor: revisar el post en local o en Pages (sobre todo en móvil) y, si quiere, cambiar la escena inicial genérica (agente, 600 líneas, 500 en un caso de error) por un ejemplo propio. Si se toca la prosa: auditoría del humanizer, `check_post.py`, `llms.txt` + `pytest`, y actualizar el draft de LinkedIn y esta entrada.

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
