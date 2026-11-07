---
type: sitio
title: Asistente del CV y servidor MCP
route: /CV/chatbot.html
summary: Cómo funciona el asistente del CV y cómo conectar un agente propio (Claude, ChatGPT, un IDE) al CV mediante su servidor MCP público de solo lectura.
tags: [asistente, mcp, agentes]
order: 900
---

# Asistente del CV y servidor MCP

## Conectar tu propio agente por MCP

- El CV, la experiencia, la formación y los artículos del blog de Demetrio están disponibles para cualquier agente mediante un servidor MCP público, de solo lectura y sin autenticación (Streamable HTTP): https://demetrio-tahoces-cv-chatbot.vercel.app/api/mcp
- En Claude Code se añade con: `claude mcp add --transport http demetrio-tahoces-cv https://demetrio-tahoces-cv-chatbot.vercel.app/api/mcp`
- En otros clientes compatibles con MCP (Claude, ChatGPT, asistentes de IDE) basta con añadir un conector MCP remoto con esa URL.
- Herramientas: `search` (busca en todas las secciones y devuelve la URL de cada una para citarla), `list_documents` y `get_document`. Prompts: `evaluar_encaje` (contrasta una oferta con el perfil) y `presentar_perfil`.
- Hay además una herramienta privada, `usage_stats`, con métricas de uso agregadas por mes (visitas, preguntas al asistente y conexiones al MCP) para el propio Demetrio. Requiere su clave, no guarda IP ni texto de las preguntas y no contiene información del perfil.
- En la página del asistente, el botón «MCP» muestra la URL y el comando para copiarlos.
- También hay un índice del sitio para LLMs en https://demetriotahoces.github.io/llms.txt

## Cómo funciona el asistente {#como-funciona}

- Es un proyecto propio de Demetrio: Python, FastAPI y LangChain/LangGraph, desplegado en Vercel.
- Responde solo con la información publicada en su CV y en su blog, y cada dato enlaza a la sección de la web que lo respalda.
- Las preguntas se procesan con Anthropic y se guardan sin IP 24 horas (180 días si se valora la respuesta), solo para mejorar el asistente; por eso conviene no escribir datos personales. Tiene un límite de preguntas por hora y por día.
