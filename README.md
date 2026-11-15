# Tarea 3 – Ajuste de parámetros con Diseño de Experimentos (DOE)

Ajuste de la **temperatura inicial T0** del Recocido Simulado con 2-opt sobre el TSP
(Tarea 2, Ejercicio 4) mediante la **Opción A: diseño factorial completo** con 3 niveles de
temperatura × 3 tamaños de problema (n = 5, 10, 15) y 10 réplicas por punto de diseño
(90 corridas). Se analiza con ANOVA de dos factores y mediana bootstrap (IC 95 %).

## Estructura

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── config.py        # matrícula (semilla de r), rango de temperatura, réplicas
│   ├── tsp.py           # instancias, costo de recorrido y óptimo exacto (Held-Karp)
│   ├── recocido.py      # Recocido Simulado con 2-opt y enfriamiento geométrico
│   ├── anova.py         # ANOVA de dos factores (con verificación opcional en statsmodels)
│   ├── bootstrap.py     # mediana bootstrap con IC 95 %
│   ├── experimento.py   # corre todo el diseño y guarda tablas
│   └── graficas.py      # efectos principales, interacción y cajas
├── data/
│   └── resultados_corridas.csv      # las 90 corridas (semilla y costo de cada una)
├── resultados/
│   ├── figuras/                     # PNG usados en el reporte
│   ├── tablas/                      # ANOVA, bootstrap y temperatura óptima (CSV)
│   └── salida_experimento.txt       # salida de consola de la corrida
└── reporte/
    └── Reporte_Tarea3.docx
```

## Cómo reproducir

```bash
pip install -r requirements.txt
python -m src.experimento
python -m src.graficas
```

## Diseño en breve

- **Aleatoriedad de los niveles:** `random.seed(MATRICULA); r = random.random()` se calcula una sola vez.
  Niveles (fracción del rango): bajo = 0.3·r, medio = 0.3·r + 0.3, alto = 0.3·r + 0.6.
  Temperatura real: `T = T_MIN + fracción · (T_MAX − T_MIN)`, con rango [1, 200].
- **Variable de respuesta:** brecha porcentual del mejor costo encontrado respecto al óptimo exacto
  de cada instancia, para que los tamaños sean comparables.
- **Algoritmo fijo:** 300 iteraciones, enfriamiento geométrico con α = 0.99; solo varía T0.
- **Réplicas:** 10 semillas distintas por punto de diseño (todas quedan guardadas en el CSV).
