import numpy as np, yaml, pathlib
from swap_utils import load_curve, bootstrap_zero, dv01_swap

def main():
    # --- Parameter & Kurve einlesen --------------------------------------
    params = yaml.safe_load(pathlib.Path("data/params.yaml").read_text())
    df_curve = load_curve()
    zeros = bootstrap_zero(df_curve)

    # DV01 berechnen
    dv01 = dv01_swap(params["nominal"], params["fixed_rate"], zeros)

    rng = np.random.default_rng(42)
    losses_gauss, losses_taleb = [], []

    for _ in range(params["n_paths"]):
        # Gaussian-Welt
        dr = rng.normal(0, params["sigma"])
        losses_gauss.append(-dv01 * dr * 10000)

        # Taleb-Welt
        dr_t = dr
        if params["use_jump"] and rng.random() < params["p_jump_daily"]:
            dr_t += params["jump_size"]
        losses_taleb.append(-dv01 * dr_t * 10000)

    # Kennzahlen-Funktion
    def risk_metrics(losses, alpha=0.99):
        var = np.quantile(losses, alpha)
        es = losses[losses >= var].mean()
        return var, es

    var_g, es_g = risk_metrics(np.array(losses_gauss))
    var_t, es_t = risk_metrics(np.array(losses_taleb))
    stress_loss = -dv01 * params["jump_size"]

    print(f"Gaussian  VaR99: {var_g:,.0f} €  |  ES99: {es_g:,.0f} €")
    print(f"Taleb     VaR99: {var_t:,.0f} €  |  ES99: {es_t:,.0f} €")
    print(f"Stress-Loss (+200 bp): {stress_loss:,.0f} €")

if __name__ == "__main__":
    main()
