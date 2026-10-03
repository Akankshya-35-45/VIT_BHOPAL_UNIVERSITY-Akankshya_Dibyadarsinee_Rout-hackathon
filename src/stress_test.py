import pandas as pd

SHOCKS = {
    "Geopolitical": {"equity": -0.10, "bond": -0.02, "loan": -0.04, "derivative": -0.06},
    "Macroeconomic": {"equity": -0.08, "bond": -0.06, "loan": -0.03, "derivative": -0.05},
    "Credit Event": {"equity": -0.12, "bond": -0.10, "loan": -0.15, "derivative": -0.12},
    "Merger/Acquisition": {"equity": 0.06, "bond": 0.01, "loan": 0.00, "derivative": 0.03},
    "Regulatory": {"equity": -0.06, "bond": -0.02, "loan": -0.04, "derivative": -0.05},
    "Product Launch": {"equity": 0.05, "bond": 0.00, "loan": 0.00, "derivative": 0.02},
    "Earnings": {"equity": -0.04, "bond": -0.01, "loan": -0.01, "derivative": -0.03},
    "Other": {"equity": -0.03, "bond": -0.01, "loan": -0.01, "derivative": -0.02},
}

def run_stress(portfolio_df, event_type, impact_score):
    df = portfolio_df.copy()
    base = SHOCKS.get(event_type, SHOCKS["Other"])
    # Scale the base scenario around the 7/10 trigger.
    multiplier = max(0.5, min(1.5, impact_score / 7.0))
    df["shock_pct"] = df["asset_type"].map(base).fillna(-0.02) * multiplier
    df["stressed_value"] = df["market_value"] * (1 + df["shock_pct"])
    df["loss"] = df["stressed_value"] - df["market_value"]
    return df

def portfolio_summary(df):
    before = df["market_value"].sum()
    after = df["stressed_value"].sum()
    return {
        "before": round(before, 2),
        "after": round(after, 2),
        "pnl": round(after-before, 2),
        "loss_pct": round((after-before)/before*100, 2) if before else 0
    }