import pandas as pd

from app.module_a_margin.etl import compute_margin, flag_high_risk


def test_compute_margin_adds_columns():
    df = pd.DataFrame(
        {
            "price": [100.0, 200.0],
            "cost": [40.0, 80.0],
            "logistics_cost": [10.0, 20.0],
            "return_rate": [0.1, 0.2],
        }
    )
    out = compute_margin(df)
    for col in ["gross_margin", "expected_return_cost", "net_margin", "net_margin_pct"]:
        assert col in out.columns


def test_net_margin_math():
    df = pd.DataFrame(
        {
            "price": [100.0],
            "cost": [40.0],
            "logistics_cost": [10.0],
            "return_rate": [0.0],
        }
    )
    out = compute_margin(df)
    assert out["gross_margin"].iloc[0] == 50.0
    assert out["expected_return_cost"].iloc[0] == 0.0
    assert out["net_margin"].iloc[0] == 50.0


def test_flag_high_risk_filters():
    df = pd.DataFrame(
        {
            "price": [100.0, 100.0],
            "cost": [40.0, 40.0],
            "logistics_cost": [10.0, 10.0],
            "return_rate": [0.05, 0.5],
        }
    )
    df = compute_margin(df)
    risky = flag_high_risk(df, threshold=0.25)
    assert len(risky) == 1
    assert risky["return_rate"].iloc[0] == 0.5