---
type: blog_post
title: "Outcomes, no output: el deploy en verde no es el resultado"
route: "/blog/posts/impact-driven-growth-outcomes.html"
date: "2026-10-30"
tags: ["Producto", "Métricas", "IA", "Ingeniería", "Impact-Driven Growth", "CPVM", "Hipótesis", "Experimentos"]
summary: "Por qué, con agentes de IA que abaratan construir, un equipo de ingeniería debe medir outcomes (cambios de comportamiento del usuario) y no output; cadena output, outcome e impacto de Impact-Driven Growth, CPVM, métricas leading y vanidosas, e hipótesis que puedan fracasar"
---

# Outcomes, no output: el deploy en verde no es el resultado

## Idea central {#contexto}

Con agentes de IA construir es cada vez más barato; lo caro es construir algo que no cambia el comportamiento de nadie. Muchos equipos de ingeniería miden output (tickets, deploys, features). Caso público: Humane levantó más de 200 millones de dólares para el AI Pin; según The Verge (agosto de 2024) las devoluciones diarias superaban a las ventas, y en febrero de 2025 HP compró la mayor parte de la empresa por 116 millones y los pines dejaron de conectarse a sus servidores. El artículo plantea como hipótesis, no como hecho, que un Mago de Oz con unos veinte usuarios durante dos semanas lo habría detectado mucho más barato. La pregunta clave es si se debería construir, no si se puede.

## Output, outcome, impacto {#cadena-causal}

Framework Impact-Driven Growth (IDG) de Carlos Iglesias (Runroom): empezar por el impacto de negocio y trabajar hacia atrás.

- Output: lo que el equipo entrega (feature, endpoint, deploy).
- Outcome: cambio observable en el comportamiento del usuario.
- Impacto: resultado financiero o estratégico.

Ejemplo hipotético: app de presupuestos con IA para instaladores. Output, el generador; outcome, el instalador envía el presupuesto sin modificar partidas; impacto, menos churn. Caso Klarna: en febrero de 2024 anunció 2,3 millones de conversaciones del asistente de IA en su primer mes (dos tercios de los chats, equivalente a 700 agentes, resolución en menos de 2 minutos frente a 11); en mayo de 2025 su CEO reconoció a Bloomberg que el coste había pesado demasiado, que la calidad era más baja y que volvían a contratar personas. Subió el volumen, no la calidad percibida.

## CPVM: una métrica que no se pueda inflar {#cpvm}

La CPVM (Customer Perceived Value Metric) de IDG mide el valor concreto entregado al cliente en un reto: local y temporal, frente a una North Star única y estable para todo el producto. Test de inflación: si la métrica puede subir sin que el cliente reciba valor, no sirve. Ejemplo hipotético: "presupuestos de IA enviados sin retoques sustanciales" (menos de 3 minutos de edición o menos de 2 partidas modificadas).

## Señales tempranas y métricas vanidosas {#metricas}

- Lagging (margen trimestral, churn mensual, NPS) confirman tarde; leading se observan en días.
- Métricas vanidosas (Eric Ries): acumulados que siempre suben y no dicen qué hacer. Accionables: ratios ligados a un comportamiento.
- One Metric That Matters (Lean Analytics, Croll y Yoskovitz) y embudo AARRR (Dave McClure).
- Ejemplo hipotético: SaaS con 6 % de churn mensual y 55 % de usuarios en prueba que nunca envían un presupuesto: problema de activación (no se fían de la IA). Leading: M1, porcentaje de presupuestos enviados en menos de 2 horas desde la visita; M2, porcentaje de partidas no modificadas en la primera revisión.

## Hipótesis que puedan fracasar {#hipotesis}

- Evitar decidir por HIPPO. Plantilla: "Creemos que si implementamos [iniciativa], provocará [outcome], lo que moverá [métrica]".
- Hypothesis Prioritization Canvas (Jeff Gothelf): valor percibido frente a riesgo; alto valor y alto riesgo se experimenta primero, alto valor y bajo riesgo se construye y mide, poco valor y mucho riesgo se descarta.
- Truth Curve (Giff Constable): cuanto más real el experimento, más creíble el resultado; a menos evidencia, menos inversión. Experimentos de barato a caro: conversación con artefacto, puerta falsa, Mago de Oz, conserje, prueba de precio, A/B con grupo de control.
- Ejemplo hipotético: una garantía económica si la IA se equivoca no hace que los instaladores envíen sin revisar; el freno es reputacional (boca a boca local), no económico.
- Fijar umbrales de éxito antes de ver los datos para evitar el sesgo de confirmación.

## Qué cambia para quien escribe el código {#ingenieria}

- La definition of done incluye cómo se medirá el outcome.
- La instrumentación (eventos) es parte del ticket.
- El feature flag es herramienta de experimento con grupo de control, no solo de despliegue.
- Si la hipótesis falla, la feature se borra.
- Con agentes de IA el output se multiplica; medir el outcome sigue siendo trabajo de ingeniería.

## Fuentes {#fuentes}

- The Verge, "Humane's daily returns are outpacing sales" (agosto 2024) y "Humane is shutting down the AI Pin and selling its remnants to HP" (febrero 2025).
- Klarna, nota de prensa del asistente de IA (febrero 2024); Fortune sobre la rectificación del CEO (mayo 2025).
- Runroom, metodología Impact-Driven Growth; Carlos Iglesias, libro "Impact-Driven Growth".
- Amplitude, North Star Metric.
- Eric Ries, "Vanity Metrics vs. Actionable Metrics" y principios de The Lean Startup.
- Lean Analytics, "The One Metric That Matters"; Dave McClure, "Startup Metrics for Pirates".
- Jeff Gothelf, "The Hypothesis Prioritization Canvas"; Giff Constable, "The Truth Curve" y "Testing with Humans".
