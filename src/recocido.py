"""Recocido Simulado con vecindario 2-opt para el TSP (versión de la Tarea 2, Ejercicio 4).

El enfriamiento es geométrico: T <- alpha * T en cada iteración. El parámetro que se
ajusta en este experimento es la temperatura inicial T0.
"""
import math
import random

from .tsp import costo_recorrido

ALPHA = 0.99          # factor de enfriamiento geométrico (fijo en todo el experimento)
ITERACIONES = 300     # presupuesto corto y fijo: con más iteraciones todas las temperaturas llegan al óptimo


def recocido_simulado(d, T0, semilla, iteraciones=ITERACIONES, alpha=ALPHA):
    """Devuelve el mejor costo encontrado en una corrida."""
    rng = random.Random(semilla)
    n = len(d)
    actual = list(range(n))
    rng.shuffle(actual)
    costo_actual = costo_recorrido(actual, d)
    mejor = costo_actual
    T = T0
    for _ in range(iteraciones):
        i, j = sorted(rng.sample(range(n), 2))
        candidato = actual[:i] + actual[i:j + 1][::-1] + actual[j + 1:]  # movimiento 2-opt
        costo_cand = costo_recorrido(candidato, d)
        delta = costo_cand - costo_actual
        if delta < 0 or rng.random() < math.exp(-delta / T):
            actual, costo_actual = candidato, costo_cand
            if costo_actual < mejor:
                mejor = costo_actual
        T *= alpha
    return mejor
