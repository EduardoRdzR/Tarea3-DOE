"""Instancias del TSP, evaluación de recorridos y solución exacta (Held-Karp)."""
import itertools
import math
import random


def generar_instancia(n, semilla):
    """Genera n ciudades con coordenadas enteras en [0, 100]. Una instancia por tamaño."""
    rng = random.Random(semilla)
    return [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(n)]


def matriz_distancias(ciudades):
    n = len(ciudades)
    return [[math.dist(ciudades[i], ciudades[j]) for j in range(n)] for i in range(n)]


def costo_recorrido(recorrido, d):
    """Longitud del ciclo cerrado definido por el recorrido."""
    n = len(recorrido)
    return sum(d[recorrido[i]][recorrido[(i + 1) % n]] for i in range(n))


def optimo_exacto(d):
    """Costo óptimo mediante programación dinámica de Held-Karp (válido para n <= 15)."""
    n = len(d)
    if n <= 3:
        return costo_recorrido(list(range(n)), d)
    dp = {}
    for j in range(1, n):
        dp[(1 << j, j)] = d[0][j]
    for tam in range(2, n):
        for subconj in itertools.combinations(range(1, n), tam):
            mascara = 0
            for j in subconj:
                mascara |= 1 << j
            for j in subconj:
                previa = mascara & ~(1 << j)
                dp[(mascara, j)] = min(dp[(previa, k)] + d[k][j] for k in subconj if k != j)
    completa = (1 << n) - 2
    return min(dp[(completa, j)] + d[j][0] for j in range(1, n))
