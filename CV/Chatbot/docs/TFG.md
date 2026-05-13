# Trabajo Fin de Grado (TFG): Procesado de Arrays de Antenas mediante Deep Learning

Este Trabajo Fin de Grado (TFG) investiga el uso de redes neuronales (NN) y técnicas de Deep Learning (DL) para resolver problemas de procesado de arrays de antenas, específicamente para obtener las alimentaciones necesarias que generen un diagrama de radiación deseado.

## Objetivos Principales
1. **Predicción de alimentaciones**: Desarrollar una herramienta capaz de estimar el módulo y la fase de los elementos de un array partiendo de un diagrama de radiación objetivo.
2. **Evaluación de eficiencia**: Comparar el rendimiento (error cuadrático medio y tiempo de entrenamiento) entre redes neuronales simples y redes con capas ocultas (Deep Learning).
3. **Compresión de información**: Analizar si es posible comprimir la información del array en las capas ocultas de la red.

## Metodología y Herramientas
- **Software**: Se utilizó Matlab y su herramienta especializada NNtoolbox.
- **Datos de entrenamiento**: Se generaron 1.000 patrones de entrenamiento aleatorios. Cada patrón consiste en un diagrama de radiación (entrada) y sus correspondientes alimentaciones de array (salida).
- **Algoritmos de entrenamiento**:
  - `trainlm` (Levenberg-Marquardt): Método rápido que requiere más memoria.
  - `trainrp` (Resilient backpropagation): Método más lento que utiliza menos memoria.
- **Funciones de activación**: Se probaron las funciones sigmoide y gaussiana en la capa de entrada, y la lineal pura (Identidad) en la de salida.

## Conclusiones y Resultados Clave
- **Configuración Óptima**: La mejor combinación para este problema resultó ser el método `trainlm` con la función de activación sigmoide y un número de 30 neuronas tanto en la capa de entrada como en las ocultas.
- **Deep Learning vs. NN Simple**: Se concluyó que el uso de Deep Learning no mejora el error en este problema específico e incluso puede empeorarlo, además de aumentar la complejidad y los tiempos de ejecución.
- **Tratamiento de la Fase**: La red presenta dificultades para procesar fases que superan los $2\pi$, por lo que se sugiere introducir la fase progresiva después del procesado en la red.
- **Flexibilidad del Array**: Una red entrenada para un array de $N$ elementos puede procesar diagramas de arrays con un número de elementos inferior, pero no superior.
- **Compresión**: Los intentos de compresión no fueron exitosos, concluyendo que los elementos del array ya forman una base fundamental para su diagrama de radiación.
