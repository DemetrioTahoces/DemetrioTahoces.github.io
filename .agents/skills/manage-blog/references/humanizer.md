# Humanizer para el blog

Submódulo adaptado de `blader/humanizer` para artículos del blog y borradores de LinkedIn. Debe usarse antes de cerrar cualquier artículo publicado.

## Objetivo

Hacer que el texto suene escrito por una persona con criterio técnico, no por una plantilla de IA. La prioridad es que el lector entienda rápido el contexto, quiera seguir leyendo y no detecte relleno, grandilocuencia o estructura mecánica.

## Proceso obligatorio

1. Leer el texto completo del artículo HTML y del draft de LinkedIn.
2. Si hay muestras previas del estilo del autor en el repo, usarlas para calibrar voz: longitud de frases, nivel de formalidad, forma de abrir párrafos, puntuación, transiciones y tono crítico.
3. Detectar patrones artificiales.
4. Reescribir, no borrar. Cubrir las mismas ideas importantes, pero con lenguaje natural.
5. Preservar significado técnico, precisión y fuentes.
6. Hacer una segunda pasada preguntando: "¿Qué suena todavía demasiado generado por IA?".
7. Corregir esos puntos antes de validar.

## Patrones a eliminar

- Inflar importancia: "crucial", "pivotal", "testament", "transformador", "revolucionario" si no hay evidencia concreta.
- Lenguaje promocional: "vibrante", "rico", "renombrado", "impresionante", "showcase", "landscape", "tapestry".
- Frases de anuncio: "vamos a explorar", "en este artículo veremos", "a continuación", "sin más preámbulos", "let's dive in".
- Fórmulas vacías: "no es solo X, es Y", "la clave está en", "en el corazón de", "lo que realmente importa", "la pregunta real es".
- Falsa profundidad con gerundios: "destacando", "subrayando", "reflejando", "fomentando", "mostrando" cuando solo añade barniz.
- Atribuciones vagas: "los expertos dicen", "algunos críticos sostienen", "la industria considera", "según varias fuentes" sin fuente concreta.
- Conclusiones genéricas: "el futuro es prometedor", "esto marca un antes y un después".
- Listas de tres forzadas cuando dos o cuatro puntos serían más naturales.
- Variación elegante artificial: alternar sin necesidad "clase", "componente", "artefacto", "entidad" para no repetir. Repetir el término correcto suele ser mejor.
- Rangos falsos: "desde X hasta Y" si X e Y no forman una escala real.
- Pasiva o frases sin sujeto cuando esconden el actor. Preferir "el sistema guarda" a "los datos son guardados" si es más claro.
- Negaciones paralelas tipo "no solo..., sino..." cuando suenan a fórmula. Reformular directo.
- Aphorismos vacíos: "X es el lenguaje de Y", "X se convierte en una trampa", "X no es una herramienta, es un espejo".
- Openers teatrales: "Honestamente?", "Mira,", "La cosa es", "Seamos sinceros" si solo fabrican cercanía.
- Tono de manual enciclopédico cuando el artículo necesita enganchar.
- Exceso de negritas, encabezados fragmentados, frases simétricas y cierres de póster.
- Em dash y en dash: `—` o `–`. Usar punto, coma, dos puntos o reformular.
- Vocabulario inflado: "landscape", "showcase", "underscore", "foster", "enhance", "robusto" por inercia, "profundo" sin concreción.

## Formato y puntuación

- Evitar exceso de negritas. La negrita mecánica es señal de texto generado.
- Evitar listas con encabezados inline en negrita tipo `**Rendimiento:** ...` salvo que aporten mucha claridad.
- Evitar title case en headings. En castellano, usar mayúscula inicial normal.
- No usar emojis decorativos en artículos ni borradores técnicos.
- Evitar comillas rizadas si se puede controlar el texto. Usar comillas rectas en ejemplos y citas.
- No dejar artefactos conversacionales: "Espero que te ayude", "claro", "por supuesto", "si quieres", "aquí tienes".
- No incluir disclaimers de conocimiento o falta de datos. Si algo no está documentado, se omite o se dice de forma concreta.
- Revisar pares con guion por inercia. Mantenerlos solo cuando sean naturales en contexto.

## Cómo humanizar artículos técnicos

- Abrir con una situación reconocible y sin ambigüedad. El primer párrafo debe dejar claro el contexto técnico antes del gancho: por ejemplo, "una clase de código", "un servicio backend", "un test de integración" o "un endpoint".
- Evitar comienzos que puedan tener doble lectura fuera del contexto técnico, como "una clase" sin aclarar si es una clase lectiva o una clase de código.
- Alternar frases cortas con explicaciones más largas.
- Usar ejemplos de vida real o de desarrollo cotidiano, pero sin inventar experiencias laborales concretas.
- Mantener una postura clara: cuándo aplicar el principio y cuándo no.
- Preferir verbos simples: "es", "tiene", "cambia", "rompe", "acopla".
- Dejar alguna frase con filo si ayuda a recordar la idea, pero sin convertir todo en aforismos.
- Recortar antes que rellenar. El objetivo del blog es 5-8 minutos de lectura.
- Evitar secciones tipo "retos y futuro" o "conclusión prometedora" si no aportan hechos.
- No narrar cambios del repo. El artículo debe leerse como pieza independiente, no como diff.
- Cuidar que el primer párrafo no requiera contexto previo del lector.

## Cómo humanizar drafts de LinkedIn

- Debe poder pegarse tal cual.
- Primera línea con gancho concreto, no grandilocuente.
- Párrafos cortos, respirables en móvil.
- Una idea por bloque.
- Evitar Markdown, notas editoriales y texto entre corchetes.
- Cerrar con una reflexión o pregunta natural, no con una llamada a la acción de marketing.
- Hashtags moderados y relevantes.
- El draft debe invitar a abrir el artículo sin vender humo.

## Falsos positivos que no deben forzar reescritura

- Texto pulido o gramaticalmente correcto no implica IA.
- Una frase corta para enfatizar puede ser humana; el problema es apilar muchas para fabricar drama.
- Una palabra formal puede ser adecuada si es precisa.
- Una transición común no es problema si no aparece como muletilla repetida.
- La falta de primera persona puede ser correcta en texto técnico.
- No aplanar detalles concretos o giros personales que hacen que el texto tenga voz.

## Auditoría final

Antes de terminar, comprobar:

- ¿Hay frases que podría haber escrito cualquier persona sobre cualquier tema?
- ¿Hay palabras infladas donde bastaba una palabra simple?
- ¿Hay em dash o en dash?
- ¿Hay signposting, conclusiones genéricas o punchlines fabricados?
- ¿El ejemplo ayuda o solo decora?
- ¿El texto tiene ritmo al leerlo en voz alta?
- ¿El draft de LinkedIn invita a abrir el artículo sin vender humo?

Si alguna respuesta falla, reescribir antes de entregar.
