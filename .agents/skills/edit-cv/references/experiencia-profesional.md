# Experiencia Profesional

Usar esta referencia cuando el usuario pida modificar, ampliar o añadir experiencia profesional, proyectos laborales, responsabilidades, logros o tecnologías asociadas a empresas.

## Archivos a revisar

- `index.html`: sección `#experiencia`.
- Página detallada correspondiente en `CV/`:
  - `CV/fermax.html`
  - `CV/opendit.html`
  - `CV/inditex.html`
  - `CV/alisys.html`
  - `CV/securitas-direct.html`
  - `CV/imagine800.html`
- Documento RAG correspondiente en `CV/Chatbot/docs/`:
  - `FERMAX.md`, `OPENDIT.md`, `INDITEX.md`, `ALISYS.md`, `SECURITAS_DIRECT.md`, `IMAGINE800.md`.
- `CV/Chatbot/docs/CV.md`: cronología y resumen global.

## Regla principal

Preservar todo lo escrito anteriormente salvo instrucción explícita de reemplazo. Si se amplía una experiencia, añadir responsabilidades, impacto, contexto o tecnologías sin borrar el relato anterior.

## Criterios de edición

- Mantener consistencia cronológica, cargo, empresa, fechas y relación contractual.
- No inventar métricas, seniority, liderazgo, impacto de negocio ni alcance técnico si no están en la petición o en documentos existentes.
- Separar claramente:
  - Responsabilidades.
  - Tecnologías usadas.
  - Arquitectura o prácticas de ingeniería.
  - Impacto o resultado.
- Evitar duplicar literalmente párrafos largos entre `index.html` y páginas detalladas. La home debe resumir; la página de detalle debe explicar.
- Respetar los umbrales de tamaño de `references/umbrales.md` (subtítulo, nº y longitud de bullets, total por tarjeta, descripción de la home). Como mucho una tarjeta destacada (`data-featured`) por página. Lo que no quepa se queda en el documento RAG.
- Si se crea una nueva experiencia, revisar navegación anterior/siguiente (case-nav), enlaces desde `index.html`, metadatos SEO básicos y documento RAG asociado.
- La página nueva sigue el patrón de assets compartidos y animaciones descrito en "Patrón de página y animaciones" del SKILL.md (head con `tokens.css`/`cv.css`, gate `motion-ready`, `cv.js`, kicker + capas `hero-stage`, atributos `data-reveal`).
- Su job-card en `index.html` se añade dentro de `.experience-list.timeline` con `data-reveal`; la línea de trayectoria y el nodo lateral se dibujan solos por CSS.
- Si se modifica una experiencia existente, sincronizar el documento RAG correspondiente para que el chatbot responda con la misma versión.

## Competencias y temas relacionados

Después de editar experiencia profesional, revisar si deben añadirse o ajustar:

- Tecnologías concretas: lenguajes, frameworks, bases de datos, mensajería, cloud, CI/CD, observabilidad, testing.
- Arquitectura y prácticas: DDD, Arquitectura Hexagonal, CQRS, Event-Driven, microservicios, clean code, mentoring, liderazgo técnico.
- Dominios: IoT, videoporteros, robótica, logística, alarmas, VoIP, datos en tiempo real, IA aplicada.

Actualizar `index.html#competencias` y `CV/Chatbot/docs/CV.md` si el cambio introduce o refuerza una competencia relevante. No añadir tecnologías marginales usadas de forma anecdótica.
