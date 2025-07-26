import pandas as pd
import numpy as np

def bootstrap_zero(csv_path: str, freq: int = 1) -> dict:
    """
    Bootstrapt Zero-Discountfaktoren aus jährlichen Par-Swap-Sätzen.
    csv_path: data/par_swaps.csv  (Spalten tenor, rate)
    Rückgabe: dict {tenor: DF}
    """
    swaps = pd.read_csv(csv_path).sort_values('tenor')
    zeros = {}  # tenor -> DF

    for tenor, rate in swaps.values:
        n = int(tenor * freq)
        accrual = rate / freq
        fixed_leg = sum(accrual * zeros[i / freq] for i in range(1, n))
        df_T = (1 - fixed_leg) / (1 + accrual)
        zeros[tenor] = df_T

    return zeros
