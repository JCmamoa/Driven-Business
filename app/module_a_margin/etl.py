import pandas as pd
from sqlalchemy import text

from app.db import engine


def load_product_history() -> pd.DataFrame:
    query = text("""
        SELECT sku, category, size, price, cost, logistics_cost, return_rate
        FROM products
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def compute_margin(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["gross_margin"] = df["price"] - df["cost"] - df["logistics_cost"]
    df["expected_return_cost"] = df["return_rate"] * (df["logistics_cost"] * 2 + df["cost"] * 0.1)
    df["net_margin"] = df["gross_margin"] - df["expected_return_cost"]
    df["net_margin_pct"] = df["net_margin"] / df["price"]
    return df


def flag_high_risk(df: pd.DataFrame, threshold: float = 0.25) -> pd.DataFrame:
    return df[df["return_rate"] > threshold].sort_values("return_rate", ascending=False)