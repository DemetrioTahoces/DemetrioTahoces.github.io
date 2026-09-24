---
type: blog_post
title: "Flujos agénticos de desarrollo: el humano decide, el agente ejecuta"
route: "/blog/posts/flujos-agenticos-desarrollo-ia.html"
date: "2026-09-24"
tags: ["IA", "Agentes", "Desarrollo de software", "Claude Code", "Spec-driven development", "Code review"]
summary: "Fábrica de tareas con agentes: spec en disco como contrato, implementación por capas, puertas deterministas, verificación en paralelo y triage, con decisiones humanas"
---

# Flujos agénticos de desarrollo: el humano decide, el agente ejecuta

## Idea central {#la-escena-tipica}

Si el mismo agente analiza, programa y da su trabajo por bueno, la única verificación independiente es la persona leyendo todo al final. Una fábrica de tareas separa responsabilidades con una regla: el humano decide, el agente ejecuta.

## Piezas del flujo

### Orquestador {#un-orquestador-que-no-programa}
No analiza, no programa ni revisa: reparte fases, juzga resultados y decide si hay otra vuelta. Es el único que habla con la persona. Cada fase usa un subagente nuevo, sin heredar el contexto (ni el sesgo) de la anterior.

### Spec en disco {#la-spec-como-contrato}
Un analista (modelo más capaz, una vez) escribe la spec: cambio y motivo, diseño, escenarios WHEN/THEN con id estable y contexto por capa y servicio. Las fases la reciben por ruta, nunca resumida. No entra en el repositorio. Las dudas abiertas se resuelven con la persona antes de implementar.

### Implementación por capas {#implementar-por-capas}
Un agente por capa hexagonal y servicio (dominio → aplicación → infraestructura), servicios en paralelo. Modelo más barato, sin investigar: si falta contexto, se corrige la spec. Un script verifica que no usan git ni salen de su capa.

### Puertas y verificación {#puertas-y-verificacion}
Puerta determinista (build y tests) antes de revisar; en rojo no se sigue. Después, en paralelo: revisión contra la spec, pruebas en entorno de desarrollo, seguridad si aplica, documentación y mantenimiento (introducido frente a preexistente).

### Triage y "terminado" {#el-triage}
Tres destinos: código → implementador de la capa; spec → el analista la enmienda; expectativa del test → se corrige la prueba. Terminado = puerta verde, sin hallazgos abiertos y cada escenario con prueba que pasa o no probable justificado. Máximo cinco vueltas; si no, vuelve a la persona.

## Dónde decide el humano {#donde-decide-el-humano}

- Al arrancar: si la tarea merece el flujo y un visto bueno único.
- Tras el análisis: dudas abiertas de la spec.
- Durante el bucle: permisos y credenciales, cuando hacen falta.
- Al final: verificar y aceptar el desarrollo, revisar la PR y decidir la promoción a preproducción y producción (el bucle solo despliega en desarrollo).

## Errores habituales {#limites}

- Usar la fábrica en tareas pequeñas.
- Pasar el plan resumido en prompts en vez de un fichero.
- Dejar que el implementador se revise a sí mismo o que el orquestador arregle fallos.
- Confiar en revisores con una spec floja.

## Fuentes {#fuentes}

- Anthropic, "Building effective agents" (diciembre 2024).
- "Best practices for Claude Code": verificación, planificar antes de codificar, revisor con contexto limpio.
- "Agent Skills", documentación de la plataforma de Claude.
