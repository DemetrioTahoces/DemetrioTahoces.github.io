---
type: cv
title: "Backend Engineer en Opendit"
route: "/CV/opendit.html"
tags: ["cv", "opendit", "backend", "iot"]
---

# Backend Engineer — Opendit
**09/2022 — 12/2024** | Madrid (Híbrido)

## Contexto
Startup IoT: telefonillos y videoporteros (apertura puertas, desvío llamadas, registro actividad, permisos terceros). Backend Engineer en equipo multidisciplinar, presente en todas las fases del producto (definición→implementación→despliegue).

## Contribuciones

### Arquitectura DAPR
- Capa abstracción infra (mensajería, secrets, service discovery) con sidecars por microservicio.
- Eliminación dependencia SDKs específicos, reducción vendor lock-in.
- Facilitación tests integración locales.

### Backend for Frontend (BFF)
- Consolidación múltiples llamadas API en una request → menor latencia.
- Respuestas adaptadas por cliente (iOS, Android, Web), sin over/under-fetching.
- Seguridad centralizada en BFF, backend oculto a red externa.
- Evolución independiente de API por cliente.

### Telemetría CQRS
- Separación Commands (escrituras masivas IoT) vs Queries (consultas optimizadas).
- Alto volumen sin comprometer rendimiento lectura.

### Cloud Azure
- AKS orquestación contenedores producción.
- Azure Service Bus mensajería enterprise-grade.
- CI/CD Azure DevOps (testing, staging, producción).
- Scrum/Kanban con Notion, ClickUp, Miro.

### Mentoría Técnica
- Formación en Hexagonal, CQRS, Event-Driven, Clean Code.
- Code reviews enfocadas en calidad arquitectónica.

## Stack
- Backend: Spring Boot (Groovy, Java 17), NestJS (TypeScript), Programación Reactiva, SOLID.
- Arquitectura: Event-Driven, Clean/Hexagonal, CQRS, DDD, BFF.
- APIs: GraphQL, OpenAPI/REST, OAuth2 (Keycloak + OpenID Connect).
- Infra: AKS, DAPR, Docker, Azure DevOps (CI/CD).
- Mensajería: Azure Service Bus, RabbitMQ.
- BBDD: PostgreSQL, MongoDB, Redis, H2DB.
- Testing: Spock (BDD), MapStruct, Postman, DBeaver, IntelliJ IDEA.
