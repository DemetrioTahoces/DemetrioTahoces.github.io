# Software Engineer — Fermax
**01/2025 — Presente** | fermax.com

## Contexto
Fermax: compañía líder 75+ años en videoporteros y control de accesos. Incorporación tras subrogación técnica desde Opendit. Reto: integrar conocimiento startup en organización de mayor escala manteniendo agilidad y calidad.

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
- IA: GitHub Copilot (agentes y skills).
