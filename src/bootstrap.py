"""Mediana bootstrap con intervalo de confianza percentil del 95 %."""
import numpy as np


def mediana_bootstrap(valores, B=10000, nivel=0.95, semilla=0):
    rng = np.random.default_rng(semilla)
    valores = np.asarray(valores, dtype=float)
    medianas = np.median(rng.choice(valores, size=(B, len(valores)), replace=True), axis=1)
    alfa = (1 - nivel) / 2
    return float(np.median(medianas)), float(np.quantile(medianas, alfa)), float(np.quantile(medianas, 1 - alfa))
