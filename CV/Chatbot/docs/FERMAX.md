---
type: cv
title: "Software Engineer en Fermax"
route: "/CV/fermax.html"
tags: ["cv", "fermax", "backend", "iot", "ia", "agentes", "claude code", "desarrollo agentico"]
---

# Software Engineer — Fermax
**01/2025 — Presente** | fermax.com

## Contexto
Fermax: fabricante de videoporteros y sistemas de control de accesos. Me incorporé tras la subrogación del equipo de Opendit para seguir desarrollando el ecosistema IoT y sus aplicaciones móviles. El objetivo principal era trasladar el diseño y la agilidad de la startup a una empresa más grande, cuidando la calidad del código y la estructura de los sistemas.

## Contribuciones

### Evolución Arquitectura (Domain Events)
- Adopción de Domain Events entre bounded contexts → desacoplamiento microservicios.
- Escalabilidad horizontal: nuevos servicios se suscriben sin modificar productores.
- Listeners transaccionales garantizan consistencia en operaciones derivadas.
- Sustitución de llamadas síncronas por publicación de eventos de dominio.

### Migración Opendit → Fermax
- Zero-downtime en migración infraestructura y servicios.
- Migración bases de datos (MongoDB, PostgreSQL), reconfiguración cloud.
- Adaptación equipo a procesos organización mayor escala, proponiendo mejoras desde experiencia startup.

### Liderazgo en Desarrollo Agéntico (Claude Code)
- Lidera la integración de Claude Code en el desarrollo de un equipo de 10 personas: workflows con 6–7 agentes especializados que cubren el ciclo completo (diseño y definición de tareas → implementación → verificación → documentación).
- Implementación repartida entre varios agentes.
- Fase de verificación con revisiones independientes: funcionalidad, seguridad y mantenibilidad del código, ejecución de pruebas en el entorno de desarrollo y documentación.
- Bucle agéntico implementación ↔ verificación: los hallazgos de las revisiones vuelven a implementación y el ciclo itera hasta que el cambio supera todos los filtros.
- Entre 10 y 15 skills propias que codifican el know-how del equipo. Temas documentados de las skills (lista cerrada; al enumerarlas cita solo estos, sin añadir otros conceptos del stack como DDD o Domain Events): arquitectura de código y arquitectura hexagonal, listeners y publishers de brokers de mensajería, endpoints REST, normas de logging, estrategia de testing y documentación. Hay alguna skill más que no se detalla públicamente. Resultado: código coherente con las convenciones del equipo en lugar de soluciones genéricas.
- Modelo cercano al concepto de software factory, ejecutado íntegramente con agentes locales de Claude Code.
- Resultados:
  - Más del 80% de las PRs son exitosas a la primera.
  - Estimación del equipo (no medición exacta), frente al desarrollo previo ya asistido por IA pero sin estos flujos: el esfuerzo de verificación (revisión + tests) y el de correcciones posteriores se ha reducido a menos de la mitad; la fase de definición y análisis también requiere algo menos de esfuerzo.
- El diseño concreto (reparto de responsabilidades entre agentes, criterios de salida del bucle, forma de las skills) es know-how propio fruto de iterar sobre el desarrollo real del equipo; no está documentado públicamente en detalle y Demetrio lo explica encantado en una conversación.

### Early Adopter IA (GitHub Copilot)
- Referente en uso avanzado de agentes y skills de Copilot.
- Automatización: tests unitarios, documentación APIs, refactoring, code review, nuevas features.

### Infraestructura y Disponibilidad
- ConfigMaps/Secrets en Kubernetes para configuración segura y dinámica.
- RabbitMQ para mensajería asíncrona (colas y exchanges).
- CI/CD con pipelines que incluyen testing.
- Despliegues blue green y problemas asociados (retrocompatibilidad BBDD, colas de mensajeria, etc.)

## Stack
- Backend: Spring Boot (Java), NestJS (TypeScript), Hexagonal, DDD, Domain Events, Unit/Integration Testing.
- BBDD: MongoDB, PostgreSQL.
- Infra: Kubernetes (ConfigMaps/Secrets), GitHub, OpenAPI/Swagger.
- Mensajería: RabbitMQ.
- IA: Claude Code (workflows multiagente, bucle implementación–verificación, skills propias), GitHub Copilot (agentes y skills).
