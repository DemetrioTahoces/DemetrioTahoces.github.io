# Backend Engineer — Opendit

## 09/2022 — 12/2024 | [Opendit](https://www.linkedin.com/company/opendit/) | Madrid (Híbrido)

---

## Contexto

Opendit fue una startup dedicada al desarrollo de soluciones IoT para el sector de telefonillos y videoporteros. El producto gestionaba funcionalidades críticas: apertura de puertas, desvío de llamadas, registro de actividad y permisos a terceros. Como Backend Engineer en un equipo multidisciplinar, participé en todas las fases del ciclo de vida del producto, desde la definición de funcionalidades y requisitos (apoyado por análisis de métricas y KPIs de producto) hasta la implementación técnica y el despliegue en producción.

---

## Contribuciones Clave

### ⚙️ Arquitectura DAPR

- DAPR como capa de abstracción de infraestructura (mensajería, secrets, service discovery).
- Sistema completamente agnóstico al cloud provider, facilitando portabilidad Azure/on-premise.
- Sidecars por microservicio, eliminando dependencia con SDKs específicos.
- Reducción de vendor lock-in y facilitación de tests de integración locales.

### 🔀 Optimización con Backend for Frontend (BFF)

- Consolidación de múltiples llamadas API en una sola request, reduciendo latencia.
- Respuestas adaptadas por cliente (iOS, Android, Web), evitando over/under-fetching.
- Evolución independiente de la API de cada cliente.

### 📊 Sistema de Telemetría con CQRS

- Separación Commands (escrituras masivas IoT) vs Queries (consultas optimizadas).
- Procesamiento de altos volúmenes sin comprometer rendimiento de lectura.
- Proyecciones optimizadas para dashboards, históricos y alertas.

### ☁️ Ecosistema Cloud Azure

- AKS para orquestación de contenedores en producción.
- Azure Service Bus como mensajería enterprise-grade.
- CI/CD en Azure DevOps con stages de testing, staging y producción.
- Metodología de trabajo híbrida Scrum/Kanban con Notion, ClickUp y Miro.

### 🎓 Mentoría Técnica

- Formación en patrones (Hexagonal, CQRS, Event-Driven) y Clean Code.
- Code reviews enfocadas en calidad arquitectónica y mantenibilidad.

---

## Stack Técnico

| Categoría | Tecnologías |
|-----------|-------------|
| **Backend** | Spring Boot (Groovy, Java 17), NestJS (TypeScript/Node.js), Programación Reactiva, SOLID |
| **Arquitectura** | Event-Driven, Clean/Hexagonal, CQRS, DDD, BFF |
| **APIs** | GraphQL, OpenAPI/REST, OAuth2 (Keycloak + OpenID Connect) |
| **Infraestructura** | AKS, DAPR, Docker, Azure DevOps (CI/CD) |
| **Mensajería** | Azure Service Bus, RabbitMQ |
| **Bases de Datos** | PostgreSQL, MongoDB, Redis, H2DB |
| **Testing & Tooling** | Spock (BDD), MapStruct, Postman, DBeaver, IntelliJ IDEA |
