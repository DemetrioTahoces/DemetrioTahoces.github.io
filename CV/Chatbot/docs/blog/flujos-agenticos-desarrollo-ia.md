---
type: blog_post
title: "Flujos agénticos de desarrollo: el humano decide, el agente ejecuta"
route: "/blog/posts/flujos-agenticos-desarrollo-ia.html"
date: "2026-09-24"
tags: ["IA", "Agentes", "Desarrollo de software", "Claude Code", "Spec-driven development", "Code review", "Skills"]
summary: "Fábrica de tareas con agentes: spec en disco como contrato, implementación por capas, puertas deterministas, verificación en paralelo y triage, con decisiones humanas"
---

# Flujos agénticos de desarrollo: el humano decide, el agente ejecuta

## Idea central {#la-escena-tipica}

Si el mismo agente analiza, programa y da su trabajo por bueno, la única verificación independiente es la persona leyendo todo al final. Una fábrica de tareas separa responsabilidades con una regla: el humano decide, el agente ejecuta.

## Dónde decide el humano {#donde-decide-el-humano}

La persona pone el qué y el cuándo; los agentes, el cómo. Lo irreversible (subir a producción) queda fuera del bucle.

- Al arrancar: define la tarea (con análisis inicial de requisitos opcional), decide si merece el flujo y da un visto bueno único.
- Tras el análisis: dudas abiertas de la spec.
- Durante el bucle: permisos y credenciales, cuando hacen falta.
- Al final: con el informe final, verificar y aceptar el desarrollo, revisar la PR y decidir la promoción a preproducción y producción (el bucle solo despliega en desarrollo).

## Piezas del flujo

### Orquestador {#un-orquestador-que-no-programa}
No analiza, no programa ni revisa: reparte fases, juzga resultados, lleva la cuenta de fase y vueltas y decide si hay otra. No arregla nada él mismo. Es el único que habla con la persona. Cada fase usa un subagente nuevo, sin heredar el contexto (ni el sesgo) de la anterior.

### Analista y spec en disco {#la-spec-como-contrato}
Diseño, análisis y planificación con el modelo más capaz, una vez. La spec recoge cambio y motivo, diseño, escenarios WHEN/THEN con id estable, contexto por capa y servicio y lista de tareas (estructura similar a OpenSpec). Las fases la reciben por ruta, nunca resumida. No entra en el repositorio del código, pero queda registrada para revisar en cualquier momento las decisiones de diseño que tomó la IA. Las dudas abiertas se resuelven con la persona antes de implementar.

### Implementación por capas {#implementar-por-capas}
Un agente por capa hexagonal y servicio: dominio (entidades, reglas, eventos), aplicación (casos de uso sobre puertos) e infraestructura (REST, persistencia, listeners y publishers); servicios en paralelo. Modelo más barato, sin investigar: si falta contexto, se corrige la spec. Un script verifica que no usan git ni salen de su capa.

### Qué necesita cada agente {#que-necesita-cada-agente}
Cada agente necesita contexto de la tarea (la spec), conocimiento del sistema y del dominio, guías de desarrollo y buenas prácticas del equipo, y herramientas para hacer su trabajo. En Claude Code: el contexto general del proyecto en `CLAUDE.md`; conocimiento y guías en skills (carpeta con `SKILL.md`, referencias y scripts, que el agente carga solo cuando la tarea lo pide); herramientas acotadas por papel en la definición de cada subagente, junto con su modelo y las skills que precarga (el implementador edita y compila sin git, el revisor solo lee, el de pruebas accede al entorno de desarrollo, por ejemplo con un servidor MCP). Las convenciones (arquitectura, endpoints, mensajería, logging, testing, documentación) se escriben una vez como skills y revisores e implementadores cargan las mismas.

### Puertas y verificación {#puertas-y-verificacion}
Puerta determinista (build y tests) antes de revisar; en rojo no se sigue. Después, en paralelo y cada una con su subagente: revisión contra la spec (solo hallazgos defendibles), pruebas en entorno de desarrollo con matriz de escenarios (modelo algo más capaz que el de implementación), seguridad si toca superficie sensible, mantenibilidad y escalabilidad (introducido frente a preexistente) y documentación.

### Triage y "terminado" {#el-triage}
Tres destinos: código → implementador de la capa; spec → el analista la enmienda; expectativa del test → se corrige la prueba. Terminado = puerta verde, sin hallazgos abiertos y cada escenario con prueba que pasa o no probable justificado. Máximo cinco vueltas; si no, vuelve a la persona. Cierra con un informe final para la persona.

## Errores habituales {#limites}

- Usar la fábrica en tareas pequeñas.
- Pasar el plan resumido en prompts en vez de un fichero.
- Dejar que el implementador se revise a sí mismo o que el orquestador arregle fallos.
- Confiar en revisores con una spec floja.

## Un equipo de software hecho de agentes {#conclusion}

Es el reparto de un equipo de software (definición, análisis, desarrollo, QA, seguridad, deuda técnica, documentación y decisión de salida a producción) llevado a agentes coordinados, cada uno con un papel, su modelo, su contexto, sus skills y sus herramientas. La persona ocupa el sitio de quien dirige el equipo.

## Fuentes {#fuentes}

- Anthropic, "Building effective agents" (diciembre 2024).
- "Best practices for Claude Code": verificación, planificar antes de codificar, revisor con contexto limpio.
- "Agent Skills", documentación de la plataforma de Claude.
- OpenSpec (Fission-AI), framework de spec-driven development.
