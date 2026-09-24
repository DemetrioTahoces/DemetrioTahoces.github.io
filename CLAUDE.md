# CLAUDE

Este repositorio usa AGENTS.md como la guía principal para agentes y asistentes de coding.
Lee siempre AGENTS.md antes de realizar cambios o responder sobre este proyecto.

Referencia principal:

- [AGENTS.md](AGENTS.md)

## Evals del chatbot

- Las evals (`uv run pytest -m evals`, workflow `chatbot-evals.yml`) solo las ejecuta un humano a mano: gastan tokens de pago. Ningún agente, pipeline ni automatización las ejecuta ni las lanza. Ver AGENTS.md.

## Despliegue del chatbot (Vercel)

- Flujo: cambios vía PR; probar en el preview de la rama y seguir pusheando al PR hasta que funcione. No pushear a `main` salvo petición explícita.
- Los previews son públicos (Vercel Authentication desactivada): `GET /api/health` se prueba con `web_fetch_vercel_url`; para `POST /api/chat[/stream]` usar un Vercel Sandbox temporal con red limitada al dominio del preview y pararlo al terminar.
- Desde el entorno cloud de Claude Code, `*.vercel.app` está bloqueado por el proxy.
