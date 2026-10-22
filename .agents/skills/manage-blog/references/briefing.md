# Briefing del artículo

Objetivo: llegar a un esquema aprobado con el mínimo de rondas. Las preguntas van siempre como encuesta cerrada con opciones (`AskUserQuestion`), con un máximo de 4 por ronda. Nunca listas de preguntas abiertas por chat: el usuario ya ha pedido que no se haga. Una ronda de brainstorm (solo si no hay idea) y una de briefing como mucho; después, esquema.

## 1. ¿Hay idea definida?

- **Sí.** Pedir que cuente el mecanismo en pocas líneas y devolverlo con las suposiciones explícitas ("doy por hecho que X, ¿correcto?"). Las opciones de la encuesta construidas sobre una suposición falsa son ruido: se corrige primero y se encuesta después.
- **No.** Brainstorm con datos del propio usuario: leer `blog/index.html`, `blog/posts/*`, las fichas de `CV/Chatbot/docs/` (experiencia y stack públicos) y, si ayuda, `CV.md`. Proponer 6-8 ideas, cada una con su ángulo, lo que aporta frente a los posts ya publicados y el riesgo de confidencialidad. Después, encuesta para elegir una o varias (el usuario siempre puede escribir otra). Si las ideas elegidas solapan con un post existente, decirlo.

## 2. Ronda de briefing (una encuesta, máximo 4 preguntas)

Siempre se preguntan estas dos:

- **Minutos de lectura.** Opciones 3, 5 y 7 (o las que encajen con el tema). Presupuesto de palabras de `.article-prose`: minutos × 220, con un margen de ±10 %. Con pocos minutos se recorta el alcance a 3-4 ideas; no se comprime todo.
- **Qué se puede contar.** Por defecto nada: ni empresa, cliente, compañeros, productos internos ni métricas reales. Si el usuario nombra términos prohibidos (una empresa, un producto), se pasan a `check_post.py --forbid TERM` en cada validación. La lista no se guarda en el repo público: `scripts/forbidden-terms.local.txt` (ignorado por git) es opcional.

Hasta dos preguntas más, según el tema: el mecanismo que decide el artículo (cómo se resuelve X), el ángulo o la tesis, o el público. Las opciones se deducen del tema y de lo que el usuario ya ha contado. Si responde con texto libre, la premisa falló: reformular y repetir una sola vez.

## 3. Esquema con huecos

Proponer título, slug, secciones con su `id`, idea del diagrama, minutos objetivo con su presupuesto de palabras y los huecos (ejemplos reales que faltan). Pedir un ejemplo real o confirmar que se usará uno hipotético marcado como tal. Basta una aprobación corta; si el usuario ya ha dicho que se publique, se sigue.

## 4. Ejemplos y afirmaciones

- No inventar experiencias, incidentes ni métricas. Un ejemplo hipotético solo vale si el texto lo presenta como tal ("Supón que...") y se avisa en el resumen final.
- Apuntar qué afirmaciones sobre el trabajo del usuario salen solo de la encuesta, para repasarlas con él.

## 5. Resumen final

Siempre, al cerrar el artículo: enlace público, ejemplos hipotéticos, afirmaciones basadas solo en el briefing, minutos reales frente a los pedidos y evals pendientes (las ejecuta un humano).
