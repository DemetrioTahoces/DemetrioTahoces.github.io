---
type: cv
title: "TFG - Procesado de Arrays de Antenas"
route: "/CV/tfg.html"
tags: ["cv", "tfg", "telecomunicacion"]
---

# TFG: Procesado de Arrays de Antenas mediante Deep Learning
Grado en Ingeniería Telecomunicación — Universidad de Oviedo (2017)

Investigación sobre redes neuronales (NN) y Deep Learning (DL) para procesado de arrays de antenas: obtener alimentaciones que generen un diagrama de radiación deseado.

## Objetivos
1. Predicción alimentaciones: estimar módulo y fase de elementos del array partiendo de diagrama radiación objetivo.
2. Evaluación eficiencia: comparar rendimiento (error cuadrático medio, tiempo entrenamiento) entre NN simples y DL (capas ocultas).
3. Compresión información: analizar si las capas ocultas pueden comprimir información del array.

## Metodología
- Software: Matlab + NNtoolbox.
- Datos: 1.000 patrones entrenamiento aleatorios (entrada: diagrama radiación, salida: alimentaciones array).
- Algoritmos: trainlm (Levenberg-Marquardt, rápido, más memoria) y trainrp (Resilient backpropagation, lento, menos memoria).
- Funciones activación: sigmoide y gaussiana (entrada), lineal pura (salida).

## Resultados
- Configuración óptima: trainlm + sigmoide + 30 neuronas (entrada y ocultas).
- DL no mejora error vs NN simple en este problema; incluso puede empeorarlo, añadiendo complejidad y tiempo.
- Dificultad con fases >2π: se sugiere introducir fase progresiva post-procesado.
- Red para N elementos procesa arrays con menos elementos, pero no más.
- Compresión no exitosa: elementos del array ya forman base fundamental para su diagrama.
