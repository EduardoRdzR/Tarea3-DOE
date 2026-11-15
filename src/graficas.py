"""Gráficas: efectos principales, interacción temperatura x tamaño y cajas por tamaño.

Uso: python -m src.graficas   (después de python -m src.experimento)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
FIG = RAIZ / "resultados" / "figuras"
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.3})
ROJO, NEGRO, GRIS = "#C0392B", "#1A1A1A", "#7F7F7F"
ESTILOS = {5: (NEGRO, "o", "-"), 10: (GRIS, "s", "--"), 15: (ROJO, "^", "-")}


def ic(serie):
    """Media y semiancho del IC 95 % (aprox. normal)."""
    return serie.mean(), 1.96 * serie.std(ddof=1) / np.sqrt(len(serie)) if len(serie) > 1 else 0


def main():
    df = pd.read_csv(RAIZ / "data" / "resultados_corridas.csv")
    temps = sorted(df.temperatura.unique())
    tamanos = sorted(df.tamano.unique())

    # 1) Efectos principales
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    m = [df[df.temperatura == t].costo.mean() for t in temps]
    e = [ic(df[df.temperatura == t].costo)[1] for t in temps]
    ax[0].errorbar(range(len(temps)), m, yerr=e, marker="o", color=ROJO, capsize=4)
    ax[0].set_xticks(range(len(temps)), [f"{t:.1f}" for t in temps])
    ax[0].set(title="Efecto principal de la temperatura", xlabel="Temperatura inicial T0", ylabel="Brecha media sobre el óptimo (%)")
    m = [df[df.tamano == n].costo.mean() for n in tamanos]
    e = [ic(df[df.tamano == n].costo)[1] for n in tamanos]
    ax[1].errorbar(range(len(tamanos)), m, yerr=e, marker="s", color=NEGRO, capsize=4)
    ax[1].set_xticks(range(len(tamanos)), [str(n) for n in tamanos])
    ax[1].set(title="Efecto principal del tamaño", xlabel="Tamaño del problema (n)", ylabel="Brecha media sobre el óptimo (%)")
    fig.tight_layout()
    fig.savefig(FIG / "efectos_principales.png", dpi=200)
    plt.close(fig)

    # 2) Interacción temperatura x tamaño
    fig, ax = plt.subplots(figsize=(6, 4))
    for n in tamanos:
        c, mk, ls = ESTILOS[n]
        sub = df[df.tamano == n]
        m = [sub[sub.temperatura == t].costo.mean() for t in temps]
        ax.plot(temps, m, color=c, marker=mk, linestyle=ls, label=f"n = {n}")
    ax.set(title="Interacción temperatura × tamaño", xlabel="Temperatura inicial T0", ylabel="Brecha media sobre el óptimo (%)")
    ax.set_xticks(temps)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "interaccion.png", dpi=200)
    plt.close(fig)

    # 3) Distribución por punto de diseño
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.4), sharey=False)
    for a, n in zip(ax, tamanos):
        sub = df[df.tamano == n]
        a.boxplot([sub[sub.temperatura == t].costo for t in temps], tick_labels=[f"{t:.1f}" for t in temps],
                  medianprops={"color": ROJO, "linewidth": 2}, boxprops={"color": GRIS}, whiskerprops={"color": GRIS}, capprops={"color": GRIS}, flierprops={"markeredgecolor": NEGRO})
        a.set(title=f"n = {n}", xlabel="Temperatura inicial T0")
    ax[0].set_ylabel("Brecha sobre el óptimo (%)")
    fig.tight_layout()
    fig.savefig(FIG / "cajas_por_tamano.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
