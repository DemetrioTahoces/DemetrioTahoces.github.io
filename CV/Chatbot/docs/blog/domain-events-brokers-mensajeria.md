# Domain events y brokers de mensajería

**Descripción:** Ficha resumida para responder sobre el artículo del blog acerca de domain events, exchanges, routing keys, colas y consumidores en brokers de mensajería.

**Fecha:** 2026-07-06

**URL:** https://demetriotahoces.github.io/blog/posts/domain-events-brokers-mensajeria.html

**Etiquetas:** DDD, Domain Events, Event-driven Architecture, RabbitMQ, Kafka, Backend, Mensajería

## Idea central

Los domain events deben modelarse como hechos de negocio ocurridos en el pasado, no como comandos para otros servicios. Cuando esos eventos atraviesan infraestructura de mensajería, los nombres de topics, exchanges y colas deberían sugerir al menos tres cosas: qué entidad de dominio ha disparado el evento, qué ocurrió y qué reacción ejecuta cada consumidor.

## Convención de nombrado

- **Domain event:** hecho en pasado, con lenguaje de dominio. Ejemplos: `UserCreated`, `OrderPaid`, `InvoiceIssued`, `SubscriptionCancelled`.
- **Exchange o topic:** entidad del evento en kebab-case. Ejemplo: `user`.
- **Routing key:** acción técnica que se ha hecho sobre la entidad del exchange, en pasado y separada por puntos si hay más segmentos. Ejemplo: `created`, `password.reset.requested`, `email.verified`.
- **Cola:** acción que se ejecuta "on" evento, separada por guiones. Ejemplo: `send-email-on-user-created`.
- **Consumidor lógico:** cada cola debe tener un único consumidor lógico, aunque pueda haber varias instancias idénticas para escalar o tolerar fallos.

## Matiz técnico importante

El ejemplo principal está planteado con RabbitMQ: exchange `user`, routing key `created` y cola `send-email-on-user-created`. La idea es extrapolable a otros brokers de mensajería, aunque el mapeo exacto cambie. En Kafka, por ejemplo, `user` puede ser el topic, `created` puede ir como `eventType`, header o campo de payload, y `send-email-on-user-created` puede ser el consumer group.

## RabbitMQ y Kafka

- RabbitMQ encaja bien con exchanges, routing keys y colas. Un exchange `user`, routing key `created` y colas como `send-email-on-user-created` hacen la topología legible.
- Kafka no tiene exchanges ni colas AMQP. La traducción habitual sería topic `user`, `eventType` `created` o `UserCreated`, y consumer group `send-email-on-user-created`.
- En Kafka no siempre conviene un topic por cada evento. Si hay muchos eventos de bajo volumen o necesidades de orden por agregado, puede usarse un topic por entidad, agregado o bounded context con `eventType` en payload o headers.

## Buenas prácticas

- Emitir eventos en pasado y con nomenclatura clara.
- No emitir comandos disfrazados de eventos.
- Separar domain event de integration event: el dominio registra el hecho; infraestructura decide si sale al broker.
- Usar metadatos como `eventId`, `eventType`, `occurredOn`, `aggregateId`, `schemaVersion`, `correlationId` y `causationId`.
- Mantener retries, DLQ, métricas y ownership separados por reacción.
- Considerar outbox si el evento sale del proceso después de una transacción de negocio.

## Errores habituales

- Nombrar eventos como comandos: `SendPasswordResetEmail` en lugar de `PasswordResetRequested`.
- Crear colas genéricas como `users`, `notifications` o `events`.
- Mezclar consumidores lógicos distintos en una misma cola.
- Publicar al broker antes de confirmar la transacción.
- Meter payloads enormes o sin versionado.

## Fuentes

- Martin Fowler: Domain Event.
- Microsoft Learn: Domain events, domain events versus integration events y eventos en pasado.
- Enterprise Integration Patterns: Event Message, Command Message y Competing Consumers.
- RabbitMQ: topic exchanges y routing keys separadas por puntos.
- Confluent Kafka docs: topics, producers, consumers, partitions y consumer groups.
- CodelyTV TypeScript DDD example: separación entre `DomainEvent`, `DomainEventSubscriber` e infraestructura RabbitMQ.
