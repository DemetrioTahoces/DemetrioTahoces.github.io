---
name: edit-cv
description: Editar, ampliar o mantener el CV estático de Demetrio Tahoces en este repositorio, incluyendo resumen profesional, experiencia profesional, formación académica o formación complementaria. Usar cuando se pidan cambios en index.html, páginas de CV, documentación RAG del chatbot, competencias técnicas o cualquier contenido curricular del proyecto, preservando por defecto el texto existente salvo instrucción explícita de reemplazo.
---

# Edit CV

## Overview

Usar esta skill para modificar el CV del proyecto sin perder contenido previo ni desalinear la página principal, las páginas detalladas y la base documental del chatbot. Leer solo la referencia que corresponda al tipo de cambio solicitado.

## Flujo Base

1. Identificar el alcance real del cambio: resumen profesional, experiencia profesional, formación/formación complementaria o una combinación.
2. Leer la referencia aplicable:
   - Resumen profesional: `references/resumen-profesional.md`.
   - Experiencia profesional: `references/experiencia-profesional.md`.
   - Formación o formación complementaria: `references/formacion.md`.
3. Revisar los archivos actuales antes de editar. No asumir que `index.html`, las páginas en `CV/` y los documentos en `CV/Chatbot/docs/` están sincronizados.
4. Aplicar cambios de forma aditiva por defecto:
   - Conservar todo lo escrito anteriormente.
   - Ampliar, matizar o reorganizar solo lo imprescindible.
   - No eliminar, condensar agresivamente ni sustituir frases salvo petición totalmente explícita.
5. Revisar si el cambio exige actualizar competencias técnicas, tecnologías, dominios, metodologías o temas relacionados. Si aplica, sincronizar `index.html#competencias` y `CV/Chatbot/docs/CV.md`.
6. Mantener el estilo del repo: HTML inline, Tailwind CDN, tema oscuro cyber-neon, sin build step ni nuevas dependencias front-end.
7. Verificar enlaces, anclas, navegación y coherencia entre la vista pública y la documentación RAG.

## Criterios Editoriales

- Escribir en castellano profesional, directo y sobrio.
- Evitar marketing vacío, exageraciones y claims difíciles de defender.
- Priorizar hechos, responsabilidades, tecnologías, impacto y contexto de negocio.
- Mantener primera persona cuando el bloque existente la use, y tercera persona solo si el bloque ya está redactado así.
- Si una nueva información contradice el CV existente, parar y resolver la contradicción antes de editar.
- Si el usuario pide "mejorar" o "ampliar" sin pedir eliminación, preservar el contenido actual y añadir precisión.

## Superficies del CV

Cambios curriculares suelen tener más de una superficie:

- `index.html`: resumen visible del CV y secciones principales.
- `CV/*.html`: páginas detalladas de resumen, experiencia o proyectos.
- `CV/Chatbot/docs/*.md`: base RAG usada por el chatbot.

No dejar una afirmación relevante en la web pública sin reflejo razonable en la documentación RAG cuando el chatbot deba poder responder sobre ella.

## Competencias Técnicas

En cada modificación o ampliación, comprobar si aparecen:

- Lenguajes, frameworks, bases de datos, mensajería, cloud, DevOps, IA, agentes, RAG, arquitectura, testing o seguridad.
- Dominios funcionales relevantes: IoT, intercomunicación, datos en tiempo real, logística, robótica, VoIP, alarmas, etc.
- Prácticas profesionales: DDD, Arquitectura Hexagonal, CQRS, Event-Driven, microservicios, Kubernetes, Docker, observabilidad o liderazgo técnico.

Actualizar competencias solo cuando aporte señal real. No convertir la sección en un listado inflado de buzzwords.
