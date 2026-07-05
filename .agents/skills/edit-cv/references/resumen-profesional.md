# Resumen Profesional

Usar esta referencia cuando el usuario pida modificar, ampliar, matizar o reescribir parcialmente el resumen profesional.

## Archivos a revisar

- `index.html`: sección `#resumen`.
- `CV/resumen-profesional.html`: página detallada del resumen profesional.
- `CV/Chatbot/docs/RESUMEN_PROFESIONAL.md`: documento RAG específico.
- `CV/Chatbot/docs/CV.md`: resumen global usado por el chatbot.

## Regla principal

Preservar todo el contenido existente salvo instrucción explícita de reemplazo. Si el usuario dice "amplía", "añade", "actualiza" o "incluye", tratarlo como cambio aditivo. No eliminar frases sobre trayectoria backend, IoT, sistemas distribuidos, datos en tiempo real, arquitectura o agentes si no se pide de forma inequívoca.

## Criterios de edición

- Mantener la narrativa: Ingeniero de Telecomunicación y Software Engineer con foco backend, IoT, sistemas distribuidos y aplicación práctica de IA/agentes.
- Añadir nueva información donde encaje mejor:
  - `index.html` debe seguir siendo breve y escaneable.
  - `CV/resumen-profesional.html` puede desarrollar contexto, motivación, enfoque técnico y visión profesional.
  - Los `.md` del chatbot deben ser más explícitos y recuperables por preguntas.
- Evitar que el resumen parezca una lista de tecnologías. Las tecnologías concretas deben reforzar una idea profesional.
- Si se incorpora una orientación nueva (por ejemplo RAG, MCP, evaluación de LLMs, Kubernetes, emprendimiento), conectarla con experiencia real o interés declarado sin sobreactuar.

## Competencias y temas relacionados

Después de editar el resumen, revisar si deben actualizarse:

- `index.html#competencias`.
- `CV/Chatbot/docs/CV.md` en `## Competencias Técnicas`.
- Algún documento específico en `CV/Chatbot/docs/` si la nueva idea se apoya en una experiencia concreta.

Actualizar competencias solo si el resumen introduce una capacidad con suficiente peso curricular.
