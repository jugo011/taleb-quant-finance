import numpy as np, yaml, pathlib
from bootstrap import bootstrap_zero
from swap_utils import dv01_gamma_swap
from scipy.stats import t as student_t
df_t = 4          # Freiheitsgrade → Fat-Tail
scale = simulate.params["sigma"] * np.sqrt((df_t-2)/df_t)
# ---------- Parameter laden -------------------------------------------------
params = yaml.safe_load((pathlib.Path(__file__).parents[1] / "data/params.yaml").read_text())

# ---------- Zero-Kurve & Sensitivität ---------------------------------------
zeros = bootstrap_zero("data/par_swaps.csv")
dv01, gamma = dv01_gamma_swap(params["nominal"], params["fixed_rate"], zeros)
from swap_utils import pv_swap_full
pv0 = pv_swap_full(params["nominal"], params["fixed_rate"], zeros)

# ---------- Monte-Carlo -----------------------------------------------------
rng = np.random.default_rng(42)
loss_g, loss_j = [], []

sigma = params["sigma"]
p_jump = params["p_jump_daily"]
jump = params["jump_size"]
for _ in range(params["n_paths"]):
    dr = rng.normal(0, sigma)                               # Gaussian
    loss_g.append(-(dv01 * dr * 1e4 + 0.5 * gamma * (dr*1e4)**2))

    dr_j = dr + (jump if rng.random() < p_jump else 0.0)    # Taleb-Jump
    loss_j.append(-(dv01 * dr_j * 1e4 + 0.5 * gamma * (dr_j*1e4)**2))

loss_g = np.array(loss_g); loss_j = np.array(loss_j)

def risk(losses, q=0.99):
    var = np.quantile(losses, q)
    es  = losses[losses >= var].mean()
    return var, es

var_g, es_g = risk(loss_g)
var_j, es_j = risk(loss_j)
stress = -(dv01*jump*1e4 + 0.5*gamma*(jump*1e4)**2)

print(f"Gaussian  VaR99: {var_g:,.0f} € | ES99: {es_g:,.0f} €")
print(f"Taleb     VaR99: {var_j:,.0f} € | ES99: {es_j:,.0f} €")
print(f"Stress-Loss (+{jump*1e4:.0f} bp): {stress:,.0f} €")
# ganz unten, statt nur print()
def run_simulation():
    return loss_g, loss_j, var_g, var_j

if __name__ == "__main__":
    # nur beim direkten Aufruf prints ausgeben
    print(f"Gaussian  VaR99: {var_g:,.0f} € | ES99: {es_g:,.0f} €")
    print(f"Taleb     VaR99: {var_j:,.0f} € | ES99: {es_j:,.0f} €")
    print(f"Stress-Loss (+{jump*1e4:.0f} bp): {stress:,.0f} €")

