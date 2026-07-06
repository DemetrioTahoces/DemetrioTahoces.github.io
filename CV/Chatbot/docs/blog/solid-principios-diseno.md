# SOLID: principios de diseño para software que cambia

**Descripción:** Ficha resumida para responder sobre el artículo del blog acerca de SOLID.

**Fecha:** 2026-07-05

**URL:** https://demetriotahoces.github.io/blog/posts/solid-principios-diseno.html

**Etiquetas:** Arquitectura, Diseño de software, Backend, OOP, Mantenibilidad

## Idea central

SOLID no es una receta para crear más clases, sino un conjunto de criterios para reducir el coste del cambio: separar responsabilidades, proteger contratos, facilitar extensión controlada y evitar que las reglas importantes dependan de detalles técnicos.

## Principios

- **SRP, Single Responsibility:** un módulo debe cambiar por una sola razón o actor de negocio. Agrupar lo que cambia junto y separar lo que cambia por motivos distintos.
- **OCP, Open/Closed:** el código estable debería poder extenderse con nuevas variantes sin modificarse constantemente. Útil cuando hay variaciones previsibles; peligroso si se abstrae antes de tiempo.
- **LSP, Liskov Substitution:** un subtipo debe respetar el contrato observable del tipo que sustituye. No basta con compilar; no debe romper precondiciones, postcondiciones ni expectativas del cliente.
- **ISP, Interface Segregation:** un consumidor no debería depender de métodos que no usa. Preferir contratos pequeños orientados al cliente/caso de uso frente a interfaces gigantes.
- **DIP, Dependency Inversion:** las políticas de alto nivel no deben depender directamente de infraestructura. El dominio/caso de uso define puertos; adaptadores técnicos implementan detalles.

## Lectura práctica

Los cinco principios se refuerzan: SRP detecta ejes de cambio, OCP crea puntos de extensión, LSP protege sustituciones, ISP reduce acoplamiento en contratos y DIP orienta dependencias hacia abstracciones. En arquitectura hexagonal, DIP aparece como puertos definidos por el núcleo y adaptadores externos para infraestructura.

## Errores habituales

- Confundir SOLID con más capas, más interfaces o más archivos.
- Usar herencia para reutilizar código aunque no exista sustitución real.
- Aplicar OCP a todo sin evidencia de variación.
- Diseñar interfaces copiando implementaciones en vez de partir de las necesidades del consumidor.
- Crear abstracciones que complican tests simples en lugar de simplificarlos.

## Regla de decisión

Antes de aplicar SOLID, preguntar: qué cambio se quiere facilitar, qué parte se quiere proteger, si la abstracción reduce acoplamiento real, si el contrato es estable para el consumidor y si los tests quedan más simples.

## Fuentes

- Robert C. Martin: SRP, OCP y relevancia de SOLID.
- Barbara Liskov y Jeannette Wing: subtipado de comportamiento.
- Cabral et al. 2024: estudio sobre SOLID y comprensión de código en Machine Learning.
