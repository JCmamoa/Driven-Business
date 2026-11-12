import numpy as np
import pandas as pd
import pytest

from app.module_a_margin.simulator import simulate_scenario


@pytest.fixture()
def sample_df():
    return pd.DataFrame(
        {
            "sku": [f"SKU-{i}" for i in range(20)],
            "price": np.random.uniform(50, 500, 20),
            "cost": np.random.uniform(20, 200, 20),
            "logistics_cost": np.random.uniform(10, 40, 20),
            "return_rate": np.random.uniform(0.02, 0.45, 20),
        }
    )


def test_simulate_returns_expected_keys(sample_df):
    result = simulate_scenario(sample_df, return_reduction_pct=20, order_scale_pct=10)
    for key in [
        "mean_net_profit",
        "p10_net_profit",
        "p90_net_profit",
        "baseline_return_rate",
        "simulated_return_rate",
        "orders_simulated",
    ]:
        assert key in result


def test_return_reduction_lowers_simulated_rate(sample_df):
    result = simulate_scenario(sample_df, return_reduction_pct=50, order_scale_pct=0)
    assert result["simulated_return_rate"] == pytest.approx(
        result["baseline_return_rate"] * 0.5, rel=1e-6
    )


def test_order_scale_increases_orders(sample_df):
    result = simulate_scenario(sample_df, return_reduction_pct=0, order_scale_pct=100)
    assert result["orders_simulated"] == 2000


def test_percentile_ordering(sample_df):
    result = simulate_scenario(sample_df, return_reduction_pct=20, order_scale_pct=10)
    assert result["p10_net_profit"] <= result["mean_net_profit"] <= result["p90_net_profit"]