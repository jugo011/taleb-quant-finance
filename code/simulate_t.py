import numpy as np, yaml, pathlib
from bootstrap import bootstrap_zero
from swap_utils import dv01_gamma_swap, pv_swap_full
from scipy.stats import t as student_t
from numpy.random import default_rng

# ---------------------------------------------------------------------------  
# 0)   Parameter & Kurve
# ---------------------------------------------------------------------------  
params = yaml.safe_load((pathlib.Path(__file__).parents[1] /
                         "data/params.yaml").read_text())

zeros = bootstrap_zero("data/par_swaps.csv")
dv01, gamma = dv01_gamma_swap(params["nominal"],
                              params["fixed_rate"], zeros)
pv0  = pv_swap_full(params["nominal"], params["fixed_rate"], zeros)

sigma     = params["sigma"]            # 0.0005  (5 bp)
p_jump    = params["p_jump_daily"]     # 0.00004
jump      = params["jump_size"]        # 0.02  (+200 bp)
n_paths   = params["n_paths"]

# Student-t Skalierung (gleiche Varianz wie Gaussian)
df_t  = 4
scale = sigma * np.sqrt((df_t - 2) / df_t)

# ---------------------------------------------------------------------------  
# 1)   Monte-Carlo
# ---------------------------------------------------------------------------  
rng = default_rng(42)

loss_g, loss_j   = [], []          # Gaussian   & Gaussian+Jump
loss_t, loss_tj  = [], []          # Student-t  & Student-t+Jump

for _ in range(n_paths):
    # ----- Gaussian --------------------------------------------------------
    dr_g = rng.normal(0, sigma)
    loss_g.append(-(dv01*dr_g*1e4 + 0.5*gamma*(dr_g*1e4)**2))

    dr_gj = dr_g + (jump if rng.random() < p_jump else 0.0)
    loss_j.append(-(dv01*dr_gj*1e4 + 0.5*gamma*(dr_gj*1e4)**2))

    # ----- Student-t -------------------------------------------------------
    dr_t = student_t.rvs(df=df_t) * scale
    loss_t.append(-(dv01*dr_t*1e4 + 0.5*gamma*(dr_t*1e4)**2))

    dr_tj = dr_t + (jump if rng.random() < p_jump else 0.0)
    loss_tj.append(-(dv01*dr_tj*1e4 + 0.5*gamma*(dr_tj*1e4)**2))

loss_g  = np.array(loss_g);  loss_j  = np.array(loss_j)
loss_t  = np.array(loss_t);  loss_tj = np.array(loss_tj)

# ---------------------------------------------------------------------------  
# 2)   Kennzahlen
# ---------------------------------------------------------------------------  
def risk(arr, q=0.99):
    var = np.quantile(arr, q)
    es  = arr[arr >= var].mean()
    return var, es

var_g,  es_g  = risk(loss_g)
var_j,  es_j  = risk(loss_j)
var_t,  es_t  = risk(loss_t)
var_tj, es_tj = risk(loss_tj)

stress = -(dv01*jump*1e4 + 0.5*gamma*(jump*1e4)**2)

# ---------------------------------------------------------------------------  
# 3)   API-Funktionen für Notebook
# ---------------------------------------------------------------------------  
def run_gauss_jump():
    """Gibt Gaussian & Taleb-Jump Arrays + Kennzahlen zurück."""
    return loss_g, loss_j, var_g, es_g, var_j, es_j

def run_student_t():
    """Gibt Student-t (ohne / mit Jump) Arrays + Kennzahlen zurück."""
    return loss_t, loss_tj, var_t, es_t, var_tj, es_tj

def get_metrics():
    """Komplette Kennzahlen-Dikt (inkl. PV/DV01/Gamma/Stress)"""
    return {
        "PV": pv0, "DV01": dv01, "Gamma": gamma, "Stress": stress,
        "VaR_G": var_g,  "ES_G": es_g,
        "VaR_T": var_t,  "ES_T": es_t,
        "VaR_J": var_j,  "ES_J": es_j,
        "VaR_TJ": var_tj,"ES_TJ": es_tj
    }

# ---------------------------------------------------------------------------  
# 4)   Konsolenausgabe beim direkten Aufruf
# ---------------------------------------------------------------------------  
if __name__ == "__main__":
    print(f"PV: {pv0:,.0f} €  |  DV01: {dv01:,.0f} €/bp  |  Gamma: {gamma:,.0f} €/bp²")
    print(f"Stress-Loss (+200 bp): {stress:,.0f} €\n")

    print(f"Gaussian    VaR99: {var_g:,.0f} €  | ES99: {es_g:,.0f} €")
    print(f"Taleb-Jump  VaR99: {var_j:,.0f} €  | ES99: {es_j:,.0f} €\n")

    print(f"Student-t   VaR99: {var_t:,.0f} €  | ES99: {es_t:,.0f} €")
    print(f"t + Jump    VaR99: {var_tj:,.0f} € | ES99: {es_tj:,.0f} €")
