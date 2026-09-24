---
type: blog_post
title: "Flujos agénticos de desarrollo: el humano decide, el agente ejecuta"
route: "/blog/posts/flujos-agenticos-desarrollo-ia.html"
date: "2026-09-24"
tags: ["IA", "Agentes", "Desarrollo de software", "Claude Code", "Skills", "Code review"]
summary: "Cómo organizar un ciclo de desarrollo con agentes especializados y verificación independiente, dejando las decisiones en manos humanas"
---

# Flujos agénticos de desarrollo: el humano decide, el agente ejecuta

## Idea central {#de-asistente-a-flujo}

Con agentes de código, escribir deja de ser el cuello de botella y lo pasa a ser la revisión. Un flujo agéntico organiza el trabajo en fases con entrada, salida y criterio de paso comprobable. Regla: el humano decide (qué construir, qué es "terminado", qué entra en main) y el agente ejecuta (código, tests, revisión de convenciones, documentación).

## El ciclo {#el-ciclo}

### Definir antes de delegar {#definir-antes-de-delegar}
Un agente ayuda a convertir la petición en una tarea con alcance, ficheros afectados, fuera de alcance y criterios de aceptación verificables. La persona la aprueba antes de implementar.

### Implementación repartida {#implementacion-repartida}
Varios agentes con contextos pequeños (dominio, adaptador, tests). Un contexto pequeño se equivoca menos.

### Verificación independiente {#verificacion-independiente}
Quien implementa no aprueba. Revisores separados con contexto limpio: funcionalidad frente a criterios, seguridad, mantenibilidad y convenciones, más tests en entorno de desarrollo.

### El bucle {#el-bucle}
Los hallazgos vuelven a implementación hasta pasar todos los filtros. Pedir solo hallazgos que afecten a corrección o a criterios (evita sobreingeniería) y limitar vueltas: si no converge, el problema suele estar en la definición y decide un humano.

## Skills {#skills-conocimiento-del-equipo}

Carpetas con instrucciones, plantillas y scripts que el agente carga bajo demanda. Codifican convenciones del equipo: organización del código, listeners/publishers de mensajería, endpoints REST, logging, testing. Se versionan, se revisan en PR y se distribuyen al equipo (por ejemplo, plugins).

## Qué no delegar {#que-no-delegar}

- Aprobar definición y criterios de aceptación.
- Decisiones de diseño con impacto fuera del cambio (contratos, modelos de datos, dependencias).
- Tradeoffs de negocio, gasto y acciones en producción.
- El merge.

## Errores habituales {#limites}

- Aplicar el ciclo completo a tareas triviales: cada revisor cuesta una ejecución de modelo.
- Confiar en la verificación automática con tests flojos o skills desactualizadas.
- Olvidar que mantener skills, agentes y criterios de salida es trabajo nuevo.

## Fuentes {#fuentes}

- Anthropic, "Building effective agents" (diciembre 2024): patrón evaluator-optimizer y empezar simple.
- "Best practices for Claude Code": verificación, explorar y planificar antes de codificar, revisor en contexto limpio.
- "Agent Skills", documentación de la plataforma de Claude: skills como carpetas cargadas bajo demanda.
