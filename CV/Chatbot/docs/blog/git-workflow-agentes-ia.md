---
type: blog_post
title: "Git workflow con agentes: una PR, su destino real y una cascada que nadie olvida"
route: "/blog/posts/git-workflow-agentes-ia.html"
date: "2026-10-23"
tags: ["IA", "Agentes", "Git", "GitFlow", "CI/CD", "Skills", "Automatización"]
summary: "Diseño propuesto de flujo de ramas para equipos con agentes de código: cada cambio entra por una sola PR en la rama más antigua afectada y una cascada de merges determinista, con CI sobre el merge, lo propaga a las ramas más nuevas; lo que mueve ramas es determinista, lo que escribe código es del agente y lo que asume riesgo es humano"
---

# Git workflow con agentes: una PR, su destino real y una cascada que nadie olvida

Es un diseño propuesto, no la descripción de un sistema en producción; el ejemplo de las versiones 2.4 y 2.5 es hipotético.

## Idea central {#el-fix-que-desaparece}

Con agentes hay más PRs, más ramas vivas y más fixes en vuelo. El riesgo principal: un hotfix entra en main pero no llega a la release en curso ni a develop; al promocionar la release, el fix desaparece de producción y el bug vuelve. Un fix de staging que no llega a develop provoca una regresión una release después. Reparto propuesto: lo que mueve ramas es determinista (Actions y rulesets), lo que escribe código es del agente y lo que asume riesgo es humano.

## Tres ramas, tres entornos {#tres-ramas-tres-entornos}

develop se despliega en dev, release/x.y en staging (el cluster inactivo de un blue-green) y main en producción. Build once, deploy many: producción recibe la misma imagen validada en staging. Tras promocionar, main avanza por fast-forward a la release, así main es siempre lo que hay en producción. Ese fast-forward solo es posible si la release contiene todo main.

## Una PR, su destino real {#una-pr-su-destino}

Regla única: un cambio entra por una PR en la rama más antigua afectada (main si el bug está en producción, la release si solo existe en staging, develop para features y fixes de lo no publicado) y se propaga automáticamente hacia las ramas más nuevas. No se abren PRs duplicadas a mano por rama. Clasificar algo como hotfix lo decide un humano; el agente lo propone con su diagnóstico.

## Cinco formas de propagar {#formas-de-propagar}

- Manual (GitFlow clásico): depende de que alguien se acuerde; Driessen ya prevé mergear el hotfix en la release abierta en lugar de en develop.
- Backport por cherry-pick con bot por etiquetas (por ejemplo korthout/backport-action): propaga en paralelo, pero crea copias con SHAs distintos que git no relaciona y cada una resuelve sus conflictos por separado. Es la herramienta correcta para backports reales a releases antiguas mantenidas.
- Upstream first (fix en develop y cherry-pick hacia release y main): develop nunca se queda sin el fix, pero la latencia hasta producción es alta y el fix se escribe sobre otro código.
- Cascada de merges con PR automática (main a release a develop): mismos commits, una resolución por salto que se hereda; precio, PRs de bot.
- Merge directo en cascada sin PR (integrado en algunas plataformas): sin ruido de PRs, pero sin CI sobre el resultado antes del merge.

Matiz: el número de PRs entre backport y cascada es parecido; la cascada gana por un solo commit por cambio, una sola resolución por conflicto y trazabilidad. Opción propuesta: híbrida, merge directo si el salto es limpio y el CI previo está verde, y PR de cascada si hay conflicto o CI rojo.

## La cascada en la práctica {#la-cascada-en-la-practica}

Al mergear en main o en una release, una GitHub Action crea una rama temporal (cascade/main-to-release-sha) con el merge y lanza el CI sobre ese commit, porque un merge sin conflictos puede romper el build (función renombrada en develop que el hotfix llama por su nombre viejo). Si sale verde, el bot hace push sin PR, como una merge queue de un elemento, y reintenta si el destino se movió. La GitHub App del bot es el único bypass actor de la regla de PR obligatoria del ruleset. Si hay conflicto o CI rojo, abre una PR desde la rama temporal, nunca con main como head. PRs normales con squash; la cascada siempre con merge commit, para que las ramas no diverjan. Puerta de promoción: no se promociona si git merge-base --is-ancestor main release/x.y falla.

## Latencia y conflictos {#latencia-y-conflictos}

La cascada es secuencial: si un salto se bloquea, develop sigue divergiendo. Mitigaciones: arranque inmediato al mergear, atajo main a develop si el salto a la release lleva horas bloqueado (seguro con merges, imposible limpio con cherry-pick), plazo con alerta y resolución del conflicto por el agente en cuanto aparece. Una PR con conflicto resuelto por el agente pierde el auto-merge y exige aprobación humana (CODEOWNERS o etiqueta) en cada salto con conflicto. Migraciones con timestamp para evitar colisiones de numeración, y expand/contract en hotfixes de esquema porque el otro cluster lee la misma base de datos.

## Skills para lo que pide criterio {#skills-para-el-criterio}

Determinista: nombres y base de rama, cascada, merge directo con CI previo, check de promoción, corte de release, versionado, tags y changelog (release-please o similar con conventional commits). Agente (skills de feature, fix y hotfix): implementar con test que reproduzca el bug, conventional commits, descripción de PR, migraciones compatibles, resolver conflictos de cascada y proponer hotfixes. Humano: clasificar hotfixes, aprobar PRs con conflictos resueltos por IA y promover a staging y producción. Lo que el agente no debe hacer (merge, push a ramas protegidas, tags) se impide con permisos del token y rulesets, no con texto en la skill.

## Y trunk-based {#y-trunk-based}

main hace de develop, las releases se cortan de main y producción es un tag: una rama larga menos y casi sin cascada (los fixes van a main y se cherry-pickean a la release, backport real), a cambio de feature flags para lo que no está listo. Driessen añadió en 2020 una nota recomendando flujos más simples para software con entrega continua. Tendría sentido cambiar con feature flags maduros y sin releases largas en staging.

## Conclusión {#conclusion}

Cada cambio entra una vez en la rama más antigua afectada, una cascada determinista lo lleva a las más nuevas (directa con CI verde, con PR si no) y ninguna release se promociona sin contener main. El agente escribe y resuelve conflictos; el humano decide hotfixes, aprueba resoluciones de la IA y promociona.

## Fuentes {#fuentes}

- Vincent Driessen, "A successful Git branching model" (2010, nota de reflexión de marzo de 2020): hotfix a master y develop, o a la release abierta; recomendación de flujos más simples con entrega continua.
- Trunk Based Development, "Branch for release": fix en trunk con test y cherry-pick a la rama de release.
- korthout/backport-action: backport por etiquetas con cherry-pick y una PR por rama destino.
- GitHub Docs: rulesets (bypass list con GitHub Apps), merge queue, auto-merge y code owners.
- Git, git-merge-base (--is-ancestor).
- googleapis/release-please: changelog, versión y tags a partir de conventional commits.
