"""ANOVA de dos factores (temperatura, tamaño, interacción).

Reproduce la tabla de sm.stats.anova_lm(ols("costo ~ C(temperatura) * C(tamano)"), typ=2).
Como el diseño es balanceado (10 réplicas por celda), las sumas de cuadrados tipo I, II y III
coinciden y se calculan directamente. Si statsmodels está instalado se usa como verificación.
"""
import pandas as pd
from scipy import stats


def anova_dos_factores(df, y="costo", a="temperatura", b="tamano"):
    media_g = df[y].mean()
    ss_total = ((df[y] - media_g) ** 2).sum()
    n_a, n_b = df[a].nunique(), df[b].nunique()
    r = len(df) // (n_a * n_b)
    media_a = df.groupby(a)[y].mean()
    media_b = df.groupby(b)[y].mean()
    media_ab = df.groupby([a, b])[y].mean()

    ss_a = r * n_b * ((media_a - media_g) ** 2).sum()
    ss_b = r * n_a * ((media_b - media_g) ** 2).sum()
    ss_celdas = r * ((media_ab - media_g) ** 2).sum()
    ss_ab = ss_celdas - ss_a - ss_b
    ss_e = ss_total - ss_celdas
    gl_e = len(df) - n_a * n_b
    ms_e = ss_e / gl_e

    filas = []
    for nombre, ss, g in [("C(" + a + ")", ss_a, n_a - 1), ("C(" + b + ")", ss_b, n_b - 1),
                          ("C(" + a + "):C(" + b + ")", ss_ab, (n_a - 1) * (n_b - 1))]:
        F = (ss / g) / ms_e
        filas.append((nombre, ss, g, F, stats.f.sf(F, g, gl_e)))
    filas.append(("Residual", ss_e, gl_e, float("nan"), float("nan")))
    return pd.DataFrame(filas, columns=["fuente", "sum_sq", "df", "F", "PR(>F)"]).set_index("fuente")


def anova_statsmodels(df):
    """Verificación cruzada con statsmodels (opcional)."""
    try:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
    except ImportError:
        return None
    modelo = ols("costo ~ C(temperatura) * C(tamano)", data=df).fit()
    return sm.stats.anova_lm(modelo, typ=2)
