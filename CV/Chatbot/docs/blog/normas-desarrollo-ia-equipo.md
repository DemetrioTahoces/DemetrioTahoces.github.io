---
type: blog_post
title: "Normas para desarrollar con IA: el agente resuelve el ahora, el equipo decide el futuro"
route: "/blog/posts/normas-desarrollo-ia-equipo.html"
date: "2026-10-08"
tags: ["IA", "Agentes", "Deuda técnica", "AGENTS.md", "Skills", "Arquitectura", "Ventana de contexto"]
summary: "Por qué un agente de código necesita por escrito las normas del equipo y por qué la visión de futuro, sobre todo en los datos, es trabajo del desarrollador; ejemplo con identificadores fiscales (NIF y VAT)"
---

# Normas para desarrollar con IA: el agente resuelve el ahora, el equipo decide el futuro

## Idea central {#la-tarea-funciona}

Un agente de código cumple la tarea (compila, los tests pasan), pero sin el contexto del equipo la resuelve a su manera: nombres fuera de convención, validación en la capa equivocada, datos en formatos no canónicos, tests mínimos. No es un fallo del agente: le falta información.

## La ventana de contexto {#lo-que-cabe-en-la-ventana}

El agente trabaja con la tarea, los ficheros que lee y las instrucciones que recibe, mucho menos de lo que sabe una persona con tiempo en el equipo. Cada sesión empieza con una ventana nueva y solo persiste lo escrito (CLAUDE.md, AGENTS.md). Llenar la ventana no lo arregla: el contexto es un recurso finito con rendimientos decrecientes. Con poco contexto relevante elige la solución local, pensada para el ahora.

## El presente: normas del equipo {#el-presente-normas-del-equipo}

Lo ya decidido tiene que estar escrito donde el agente lo lea:

- Convenciones: nombres, estructura de paquetes, logs, commits.
- Estructuración de datos: formatos canónicos (fechas, importes, identificadores), qué se normaliza y dónde.
- Arquitectura: capas, dependencias, dónde vive la validación, eventos frente a llamadas síncronas.
- Testing: tests obligatorios por capa, qué se mockea, qué debe pasar antes de una PR.

Reglas generales cortas y verificables en AGENTS.md o CLAUDE.md; conocimiento específico en skills, que se cargan cuando la tarea lo pide. El agente trata esas instrucciones como contexto, no como configuración obligatoria: lo que pueda comprobar una herramienta (formato, dependencias entre capas, tests mínimos) se comprueba en CI.

## El futuro no está en la tarea {#el-futuro-no-esta-en-la-tarea}

La tarea no dice cómo va a crecer el producto y el agente no conoce el roadmap ni el negocio. Ver el futuro es trabajo del desarrollador en los puntos críticos: forma de los datos, qué capa asume responsabilidades que crecerán, contratos que consumirán otros. Los datos son lo más delicado: un formato ya guardado y repartido por servicios pide una migración.

## Ejemplo: identificadores fiscales {#ejemplo-identificadores-fiscales}

Experiencia del autor con NIF (España) y VAT (Europa). La especificación pedía normalizarlos y verificarlos para ciertos países. El agente, siguiendo sus skills, normalizó y verificó correctamente en los value objects del dominio del backend. No escalaba: cada país nuevo añadiría al backend reglas de normalización para todos sus formatos de entrada. Decisión del equipo: un formato común, el del número de IVA intracomunitario que valida VIES (prefijo de país y número sin separadores); el frontend normaliza la entrada según el país (por ejemplo, 12.345.678-z pasa a ES12345678Z) y el backend verifica ese único formato y rechaza el resto. Es discutible (hay quien prefiere un frontend lo más simple posible), pero un agente no la habría tomado solo: requiere saber cómo crecerá el producto.

## Escribir la decisión en el momento {#escribir-la-decision}

La decisión se escribe en la skill o en AGENTS.md en el mismo momento, con su motivo, o la siguiente sesión repetirá la solución anterior. La regla nueva sustituye a la antigua: si dos instrucciones se contradicen, el agente puede seguir cualquiera.

## Conclusión {#conclusion}

El agente resuelve el ahora; el equipo aporta el antes (normas escritas y comprobadas por herramientas) y el después (visión de futuro, que no se delega). Escribir cada decisión evita que la IA acumule deuda técnica.

## Fuentes {#fuentes}

- "How Claude remembers your project", documentación de Claude Code: sesiones con contexto nuevo, CLAUDE.md y AGENTS.md como contexto y no configuración obligatoria, instrucciones concretas y sin contradicciones.
- Anthropic, "Effective context engineering for AI agents" (septiembre 2025): el contexto como recurso finito.
- AGENTS.md, formato abierto de instrucciones para agentes de código.
- "Agent Skills", documentación de la plataforma de Claude.
- Comisión Europea, "VIES on-the-Web": validación de números de IVA intracomunitario.
