import numpy as np
import pandas as pd


def simulate_scenario(
    df: pd.DataFrame,
    return_reduction_pct: float,
    order_scale_pct: float,
    n_simulations: int = 5000,
) -> dict:
    base_orders = 1000
    orders = base_orders * (1 + order_scale_pct / 100)

    base_return = df["return_rate"].mean()
    new_return = base_return * (1 - return_reduction_pct / 100)

    unit_margin = (df["price"] - df["cost"] - df["logistics_cost"]).mean()
    return_cost = df["logistics_cost"].mean() * 2 + df["cost"].mean() * 0.1

    noise = np.random.normal(1.0, 0.05, n_simulations)
    margins = (orders * unit_margin * noise) - (orders * new_return * return_cost * noise)

    return {
        "mean_net_profit": float(margins.mean()),
        "p10_net_profit": float(np.percentile(margins, 10)),
        "p90_net_profit": float(np.percentile(margins, 90)),
        "baseline_return_rate": float(base_return),
        "simulated_return_rate": float(new_return),
        "orders_simulated": orders,
    }