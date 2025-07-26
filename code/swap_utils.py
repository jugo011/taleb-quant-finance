import pandas as pd
import numpy as np

def pv_swap_full(nominal: float, fixed_rate: float, zeros: dict, freq: int = 1) -> float:
    """PV eines Pay-Fixed/Receive-Float Par-Swaps bei jährlicher Auszahlung."""
    fixed_leg = sum(fixed_rate / freq * nominal * df for df in zeros.values())
    float_leg = nominal * (1 - list(zeros.values())[-1])  # Par-Annahme
    return fixed_leg - float_leg  # positiv = Vorteil Pay-Fixed

def dv01_gamma_swap(nominal: float, fixed_rate: float, zeros: dict, freq: int = 1):
    """DV01 (€/bp) und Gamma (€/bp²) via ±1 bp-Bump."""
    bump = 0.0001  # 1 bp
    zeros_up   = {t: df * np.exp(-bump * t) for t, df in zeros.items()}
    zeros_down = {t: df * np.exp(+bump * t) for t, df in zeros.items()}

    pv0   = pv_swap_full(nominal, fixed_rate, zeros, freq)
    pv_up = pv_swap_full(nominal, fixed_rate, zeros_up, freq)
    pv_dn = pv_swap_full(nominal, fixed_rate, zeros_down, freq)

    dv01  = (pv_up - pv_dn) / 2          # €/bp
    gamma = (pv_up + pv_dn - 2 * pv0) / (bump ** 2)
    return dv01, gamma
