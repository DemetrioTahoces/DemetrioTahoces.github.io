---
type: blog_post
title: "Blue-green con estado: aislar las colas, disciplinar la base de datos"
route: "/blog/posts/blue-green-con-estado.html"
date: "2026-10-22"
tags: ["Despliegues", "Mensajería", "Bases de datos", "Blue-green", "Expand/contract", "Broker de mensajería", "Rollback"]
summary: "Cómo desplegar con dos clusters de producción que comparten broker y base de datos: colas con prefijo por cluster y cambios de esquema con expand/contract, sin borrar nada mientras se pueda volver atrás"
---

# Blue-green con estado: aislar las colas, disciplinar la base de datos

## Idea central {#dos-clusters-un-interruptor}

Con dos clusters de producción (par e impar), uno activo y otro donde se despliega y se prueba la release nueva antes de mover el tráfico, el rollback es un interruptor, pero los dos clusters comparten broker y base de datos y dos versiones del código conviven sobre los mismos datos. La compatibilidad entre versiones no hace falta en todas partes: lo que se puede aislar se aísla y lo que no se disciplina.

## La mensajería se aísla {#la-mensajeria-se-aisla}

El broker de mensajería es el mismo para los dos clusters, pero exchanges y colas llevan un prefijo con el entorno y el cluster (por ejemplo prod-par.* y prod-impar.*). Cada cluster publica y consume solo en lo suyo, así que un mensaje de la versión N solo lo consume la versión N y los contratos de los eventos no cruzan la frontera entre versiones. Alternativas como eventos versionados o consumidores tolerantes funcionan, pero exigen disciplina en cada cambio. Al cambiar el tráfico, el cluster saliente drena sus colas antes de apagarse; volver a él no mezcla versiones. Precio: duplicar la topología (dos juegos de exchanges y colas por servicio).

## La base de datos no se duplica {#la-base-de-datos-no-se-duplica}

La base de datos es lo único que los dos clusters comparten de verdad. Una por cluster obligaría a sincronizarlas y se perderían transacciones (lo advierte Martin Fowler). Regla: cada cambio de esquema debe funcionar con la versión en producción y con la siguiente, y en las dos direcciones: la nueva entiende lo que dejó la anterior y la anterior entiende lo que escribe la nueva, porque en un rollback será ella la que lea. El patrón es expand/contract (parallel change): ampliar el esquema para soportar lo viejo y lo nuevo, migrar el código poco a poco y retirar lo viejo al final.

## Ejemplo: renombrar una columna {#ejemplo-renombrar-columna}

Ejemplo ilustrativo de renombrar phone a contact_phone en cuatro releases: expand (añadir la columna nullable, escribir en las dos, leer la vieja, backfill); migrate (leer la nueva, seguir escribiendo en las dos); dejar de usar la vieja; contract (eliminarla con una migración). Los pasos 3 y 4 van separados porque el cluster activo, en la release del paso 2, todavía escribe la columna vieja: se borra una release después, cuando ninguna versión desplegada la toca. Hacerlo en una sola release rompería a la versión anterior.

## El contract espera {#el-contract-espera}

Lo destructivo (borrar una columna, endurecer una restricción) solo se ejecuta cuando el cluster anterior deja de ser destino de rollback. Se espera de verdad: mientras una versión pueda volver a recibir tráfico, la base de datos tiene que seguir entendiéndola. Lo que se añade se puede quitar más tarde; lo que se borra no vuelve.

## Lo que cuesta y lo que da {#lo-que-cuesta}

Coste: un cambio de esquema pasa de una release a varias (un backfill grande se planifica aparte), la infraestructura se duplica y cada PR que toca la base de datos debe responder si funciona con la versión anterior; cambiar el significado de un valor sin cambiar su tipo no lo detecta ninguna migración, solo la revisión. Beneficio: la release nueva se prueba con infraestructura real antes de recibir usuarios y el rollback es el mismo interruptor de tráfico en sentido contrario.

## Conclusión {#conclusion}

Con estado compartido, blue-green se resuelve en lo que compartes y no en el despliegue: aislar la mensajería con prefijos por cluster y disciplinar la base de datos con expand/contract, sin borrar hasta que nadie pueda volver atrás.

## Fuentes {#fuentes}

- Martin Fowler, "BlueGreenDeployment" (marzo 2010): el patrón, el rollback por router y las bases de datos como reto, con la recomendación de separar los cambios de esquema del despliegue de la aplicación.
- Danilo Sato, "ParallelChange" (mayo 2014): expand, migrate y contract; la mayoría de refactorizaciones de bases de datos siguen este patrón.
