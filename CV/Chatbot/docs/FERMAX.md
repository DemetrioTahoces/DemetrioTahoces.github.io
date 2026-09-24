---
type: cv
title: "Software Engineer en Fermax"
route: "/CV/fermax.html"
tags: ["cv", "fermax", "backend", "iot", "ia", "agentes", "claude code", "desarrollo agentico"]
summary: "Experiencia actual (01/2025–presente): Software Engineer; backend IoT, DDD, Kubernetes y liderazgo del desarrollo agéntico con Claude Code"
order: 10
---

# Software Engineer — Fermax
**01/2025 — Presente** | fermax.com

## Contexto {#contexto}
Fermax: fabricante de videoporteros y sistemas de control de accesos. Me incorporé tras la subrogación del equipo de Opendit para seguir desarrollando el ecosistema IoT y sus aplicaciones móviles. El objetivo principal era trasladar el diseño y la agilidad de la startup a una empresa más grande, cuidando la calidad del código y la estructura de los sistemas.

## Contribuciones {#contribuciones-clave}

### Evolución Arquitectura (Domain Events) {#domain-events}
- Adopción de Domain Events entre bounded contexts → desacoplamiento microservicios.
- Escalabilidad horizontal: nuevos servicios se suscriben sin modificar productores.
- Listeners transaccionales garantizan consistencia en operaciones derivadas.
- Sustitución de llamadas síncronas por publicación de eventos de dominio.

### Migración Opendit → Fermax {#migracion-opendit}
- Zero-downtime en migración infraestructura y servicios.
- Migración bases de datos (MongoDB, PostgreSQL), reconfiguración cloud.
- Adaptación equipo a procesos organización mayor escala, proponiendo mejoras desde experiencia startup.

### Liderazgo en Desarrollo Agéntico (Claude Code) {#desarrollo-agentico}
- Lidera la integración de Claude Code en el desarrollo de un equipo de 10 personas: workflows con 6–7 agentes especializados que cubren el ciclo completo (diseño y definición de tareas → implementación → verificación → documentación).
- Implementación repartida entre varios agentes.
- Fase de verificación con revisiones independientes: funcionalidad, seguridad y mantenibilidad del código, ejecución de pruebas en el entorno de desarrollo y documentación.
- Bucle agéntico implementación ↔ verificación: los hallazgos de las revisiones vuelven a implementación y el ciclo itera hasta que el cambio supera todos los filtros.
- Entre 10 y 15 skills propias que codifican el know-how del equipo. Temas documentados de las skills (lista cerrada; al enumerarlas cita solo estos, sin añadir otros conceptos del stack como DDD o Domain Events): arquitectura de código y arquitectura hexagonal, listeners y publishers de brokers de mensajería, endpoints REST, normas de logging, estrategia de testing y documentación. Hay alguna skill más que no se detalla públicamente. Resultado: código coherente con las convenciones del equipo en lugar de soluciones genéricas.
- Agentes, workflows y skills se comparten en el equipo mediante plugins privados de Fermax para Claude Code.
- Modelo cercano al concepto de software factory, ejecutado íntegramente con agentes locales de Claude Code.
- Resultados:
  - Más del 80% de las PRs son exitosas a la primera.
  - Estimación del equipo (no medición exacta), frente al desarrollo previo ya asistido por IA pero sin estos flujos: el esfuerzo de verificación (revisión + tests) y el de correcciones posteriores se ha reducido a menos de la mitad; la fase de definición y análisis también requiere algo menos de esfuerzo.
- El patrón general (orquestador que no programa, spec en disco como contrato, implementación por capas, puertas deterministas, verificación en paralelo y triage) es conocimiento que Demetrio comparte en su blog técnico. Los detalles de implementación del equipo (agentes concretos, prompts, herramientas internas, reglas exactas) son know-how propio no publicado; Demetrio los explica encantado en una conversación.

### Early Adopter IA (GitHub Copilot) {#github-copilot}
- Referente en uso avanzado de agentes y skills de Copilot.
- Automatización: tests unitarios, documentación APIs, refactoring, code review, nuevas features.

### Infraestructura y Disponibilidad {#infraestructura}
- ConfigMaps/Secrets en Kubernetes para configuración segura y dinámica.
- RabbitMQ para mensajería asíncrona (colas y exchanges).
- CI/CD con pipelines que incluyen testing.
- Despliegues blue green y problemas asociados (retrocompatibilidad BBDD, colas de mensajeria, etc.)

## Stack {#stack-tecnico}
- Backend: Spring Boot (Java), NestJS (TypeScript), Hexagonal, DDD, Domain Events, Unit/Integration Testing.
- BBDD: MongoDB, PostgreSQL.
- Infra: Kubernetes (ConfigMaps/Secrets), GitHub, OpenAPI/Swagger.
- Mensajería: RabbitMQ.
- IA: Claude Code (workflows multiagente, bucle implementación–verificación, skills propias), GitHub Copilot (agentes y skills).
