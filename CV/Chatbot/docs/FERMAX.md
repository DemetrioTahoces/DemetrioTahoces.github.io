# Software Engineer — Fermax

## 01/2025 — Presente | [Fermax](https://www.fermax.com/)

---

## Contexto

Fermax es una compañía líder con más de 75 años de trayectoria en el sector de videoporteros y control de accesos. Tras la subrogación técnica del equipo de Opendit, me incorporé al equipo de desarrollo para continuar la evolución del ecosistema IoT y las aplicaciones móviles de la compañía. El reto principal: integrar el conocimiento técnico adquirido en la etapa startup dentro de una organización de mayor escala, manteniendo la agilidad y la calidad del código.

---

## Contribuciones Clave

### 🏗️ Evolución de Arquitectura con Domain Events

Impulso estratégico del uso de Domain Events dentro de la arquitectura DDD del backend.

- Promoví la adopción de Domain Events como mecanismo de comunicación entre bounded contexts, implicando desacoplamiento entre microservicios y contextos.
- La gestión asíncrona de eventos ha facilitado una escalabilidad horizontal mucho más natural, permitiendo que nuevos servicios se suscriban a eventos existentes sin modificar los productores.
- Los listeners de Domain Events pueden ser transaccionales, garantizando consistencia en las operaciones derivadas.
- Reducción de la complejidad accidental en la comunicación inter-servicio, sustituyendo llamadas síncronas por publicación de eventos de dominio.

### 🔄 Migración Tecnológica desde Opendit

Migración crítica de infraestructura y servicios con zero-downtime.

- Participación clave en el equipo de migración desde Opendit a Fermax, asegurando la disponibilidad del servicio y la integridad de los datos para miles de usuarios activos durante la fase de convergencia.
- Coordinación de la migración de bases de datos (MongoDB y PostgreSQL) y reconfiguración de servicios cloud.
- Adaptación del equipo técnico a los procesos y cultura de una organización de mayor escala, manteniendo las buenas prácticas de ingeniería adquiridas en el entorno startup y proponiendo sugerencias de mejora aplicando lo aprendido en la startup.

### 🤖 Early Adopter en IA (GitHub Copilot)

Integración pionera de herramientas de IA en el flujo de desarrollo del equipo.

- Testeo y adopción pionera del ecosistema de agentes y skills de GitHub Copilot dentro del equipo de desarrollo, siendo referente en su uso avanzado.
- Automatización de tareas repetitivas: generación de boilerplate, tests unitarios, documentación de APIs, refactoring de código legacy e incluso desarrollo de nuevas features.

### ☸️ Infraestructura y Disponibilidad

Despliegue y mantenimiento de microservicios en producción sobre Kubernetes.

- Gestión de ConfigMaps y Secrets en Kubernetes para la configuración segura y dinámica de los microservicios en producción.
- Garantía de comunicaciones fluidas entre servicios mediante RabbitMQ (mensajería asíncrona con colas y exchanges).
- Automatización de despliegues con pipelines de CI/CD que incluyen testing.

---

## Stack Técnico

| Categoría | Tecnologías |
|-----------|-------------|
| **Backend & Arquitectura** | Spring Boot (Java), NestJS (TypeScript/Node.js), Arquitectura Hexagonal, DDD, Domain Events, Unit Testing, Tests de Integración |
| **Bases de Datos** | MongoDB, PostgreSQL |
| **Infraestructura & CI/CD** | Kubernetes (ConfigMaps/Secrets), GitHub, OpenAPI/Swagger |
| **Mensajería** | RabbitMQ |
| **IA** | GitHub Copilot (agentes y skills) |
