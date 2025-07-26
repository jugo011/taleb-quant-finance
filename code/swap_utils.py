import numpy as np
import pandas as pd

def load_curve(path="data/curve.csv"):
    """CSV → DataFrame mit 'tenor' und 'rate'."""
    return pd.read_csv(path)

def bootstrap_zero(df_curve):
    """
    Minimale Zero-Kurve: Diskontfaktor = exp(-rate * tenor)
    (reicht für Demo-Zwecke).
    """
    zeros = {}
    for tenor, rate in df_curve.values:
        zeros[tenor] = np.exp(-rate * tenor)
    return zeros

def pv_swap(nominal, fixed_rate, zeros, freq=1):
    """PV = Fixed-Leg – Float-Leg (vereinfachte Par-Annahme)."""
    fixed_leg = sum(fixed_rate / freq * nominal * df
                    for df in zeros.values())
    float_leg = nominal * (1 - list(zeros.values())[-1])
    return fixed_leg - float_leg

def dv01_swap(nominal, fixed_rate, zeros, freq=1):
    """DV01 via 1-bp-Bump."""
    bump = 0.0001  # 1 bp
    zeros_b = {t: np.exp(-(-np.log(df)/t + bump) * t)
               for t, df in zeros.items()}
    pv_base = pv_swap(nominal, fixed_rate, zeros, freq)
    pv_bump = pv_swap(nominal, fixed_rate, zeros_b, freq)
    return pv_bump - pv_base  # € pro bp
