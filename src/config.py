"""Parámetros del experimento."""

MATRICULA = 2116554        # matrícula usada como semilla de r
TAMANOS = [5, 10, 15]      # bloque: tamaño del problema TSP
REPLICAS = 10              # corridas por punto de diseño
T_MIN, T_MAX = 1.0, 200.0  # rango de temperatura inicial definido para el problema
SEMILLA_INSTANCIA = 2026   # semilla de las instancias (una por tamaño)
B_BOOTSTRAP = 10000
ALFA = 0.05
