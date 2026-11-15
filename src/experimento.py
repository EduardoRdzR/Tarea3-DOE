"""Experimento DOE (Opción A): factorial 3 x 3 con 10 réplicas, ANOVA de dos factores y bootstrap.

Uso (desde la raíz del repositorio):
    python -m src.experimento
"""
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from . import config as C
from .anova import anova_dos_factores, anova_statsmodels
from .bootstrap import mediana_bootstrap
from .recocido import recocido_simulado, ALPHA, ITERACIONES
from .tsp import generar_instancia, matriz_distancias, optimo_exacto

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data"
TABLAS = RAIZ / "resultados" / "tablas"
for carpeta in (DATOS, TABLAS):
    carpeta.mkdir(parents=True, exist_ok=True)


def niveles_temperatura():
    """Un solo r ~ U(0,1) fijado por la matrícula; niveles de la Opción A."""
    random.seed(C.MATRICULA)
    r = random.random()
    fracciones = {"bajo": 0.3 * r, "medio": 0.3 * r + 0.3, "alto": 0.3 * r + 0.6}
    temps = {k: C.T_MIN + f * (C.T_MAX - C.T_MIN) for k, f in fracciones.items()}
    return r, fracciones, temps


def main():
    r, fracciones, temps = niveles_temperatura()
    print(f"r = {r:.6f}")
    for k in temps:
        print(f"  {k}: fracción {fracciones[k]:.4f} -> T0 = {temps[k]:.2f}")

    # Instancias y óptimos exactos (para expresar el costo como brecha porcentual)
    d_por_n, optimo = {}, {}
    for n in C.TAMANOS:
        d_por_n[n] = matriz_distancias(generar_instancia(n, C.SEMILLA_INSTANCIA + n))
        optimo[n] = optimo_exacto(d_por_n[n])

    filas = []
    for n in C.TAMANOS:
        for k, T0 in temps.items():
            for rep in range(C.REPLICAS):
                semilla = 100000 * n + 1000 * list(temps).index(k) + rep
                mejor = recocido_simulado(d_por_n[n], T0, semilla)
                filas.append({
                    "tamano": n, "nivel": k, "temperatura": round(T0, 2), "replica": rep + 1,
                    "semilla": semilla, "costo_bruto": mejor,
                    "costo": 100 * (mejor / optimo[n] - 1),   # brecha % sobre el óptimo
                })
    df = pd.DataFrame(filas)
    df.to_csv(DATOS / "resultados_corridas.csv", index=False)

    # ANOVA de dos factores
    tabla = anova_dos_factores(df)
    tabla.to_csv(TABLAS / "anova_dos_factores.csv")
    print("\nANOVA de dos factores (variable: brecha %)\n", tabla.round(4))
    verif = anova_statsmodels(df)
    if verif is not None:
        print("\nVerificación con statsmodels:\n", verif.round(4))

    # Bootstrap por punto de diseño
    resumen = []
    for n in C.TAMANOS:
        for k, T0 in temps.items():
            v = df[(df.tamano == n) & (df.nivel == k)]["costo"].values
            med, lo, hi = mediana_bootstrap(v, C.B_BOOTSTRAP, semilla=n * 10 + list(temps).index(k))
            resumen.append({"tamano": n, "nivel": k, "temperatura": round(T0, 2),
                            "media": v.mean(), "desv_est": v.std(ddof=1),
                            "mediana_bootstrap": med, "ic95_inf": lo, "ic95_sup": hi})
    res = pd.DataFrame(resumen)
    res.to_csv(TABLAS / "bootstrap_por_punto.csv", index=False)

    # Análisis por tamaño: ANOVA de un factor y Kruskal-Wallis (robustez) sobre la temperatura
    por_tamano, optimos = [], []
    for n in C.TAMANOS:
        sub = df[df.tamano == n]
        grupos = [sub[sub.nivel == k]["costo"].values for k in temps]
        if all(np.ptp(g) == 0 for g in grupos) and len({g[0] for g in grupos}) == 1:
            p_anova = p_kw = float("nan")
        else:
            p_anova = stats.f_oneway(*grupos).pvalue
            p_kw = stats.kruskal(*grupos).pvalue
        por_tamano.append({"tamano": n, "p_anova_1f": p_anova, "p_kruskal": p_kw})
        # Regla de decisión: menor mediana bootstrap; desempate por menor media y luego menor T0
        sr = res[res.tamano == n].sort_values(["mediana_bootstrap", "media", "temperatura"])
        mejor = sr.iloc[0]
        empates = int((sr.mediana_bootstrap == mejor.mediana_bootstrap).sum())
        optimos.append({"tamano": n, "nivel_optimo": mejor.nivel, "T_optima": mejor.temperatura,
                        "mediana_bootstrap": mejor.mediana_bootstrap, "ic95_inf": mejor.ic95_inf,
                        "ic95_sup": mejor.ic95_sup, "niveles_empatados_en_mediana": empates})
    pd.DataFrame(por_tamano).to_csv(TABLAS / "pruebas_por_tamano.csv", index=False)
    pd.DataFrame(optimos).to_csv(TABLAS / "temperatura_optima.csv", index=False)
    print("\nPruebas por tamaño\n", pd.DataFrame(por_tamano))
    print("\nTemperatura óptima por tamaño\n", pd.DataFrame(optimos))

    meta = {"r": r, "fracciones": fracciones, "temperaturas": temps, "T_min": C.T_MIN, "T_max": C.T_MAX,
            "matricula_semilla": C.MATRICULA, "alpha_enfriamiento": ALPHA, "iteraciones": ITERACIONES,
            "optimos_exactos": {str(n): optimo[n] for n in C.TAMANOS}}
    (TABLAS / "meta.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
