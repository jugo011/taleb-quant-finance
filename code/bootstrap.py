import pandas as pd
import numpy as np

def bootstrap_zero(csv_path, freq=1):
    """
    Recursiv: diskontiert Par-Swaps (jährliche Kupons) zu Zero-DFs.
    csv_path: data/par_swaps.csv mit Spalten tenor, rate
    Rückgabe: dict tenor -> DF
    """
    swaps = pd.read_csv(csv_path).sort_values('tenor')
    zeros = {}

    for tenor, rate in swaps.values:
        n = int(tenor * freq)
        fixed_leg = 0.0
        for i in range(1, n):
            t_i = i / freq
            if t_i in zeros:
                fixed_leg += (rate / freq) * zeros[t_i]
        df_T = (1 - fixed_leg) / (1 + rate / freq)
        zeros[tenor] = df_T

    return zeros
