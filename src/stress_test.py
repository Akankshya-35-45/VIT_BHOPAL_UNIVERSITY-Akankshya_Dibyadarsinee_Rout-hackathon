import pandas as pd


# ============================================================
# EVENT-DRIVEN STRESS SCENARIO LIBRARY
# ============================================================
# Synthetic scenario assumptions created specifically for the
# hackathon prototype. These are NOT market forecasts.
#
# Values represent the approximate directional shock applied
# to each asset class under a 7/10 scenario intensity.
# ============================================================

SHOCKS = {

    "Geopolitical": {
        "equity": -0.10,
        "bond": -0.02,
        "loan": -0.04,
        "derivative": -0.06,
    },

    "Macroeconomic": {
        "equity": -0.08,
        "bond": -0.06,
        "loan": -0.03,
        "derivative": -0.05,
    },

    "Credit Event": {
        "equity": -0.12,
        "bond": -0.10,
        "loan": -0.15,
        "derivative": -0.12,
    },

    "Merger/Acquisition": {
        "equity": 0.06,
        "bond": 0.01,
        "loan": 0.00,
        "derivative": 0.03,
    },

    "Regulatory": {
        "equity": -0.06,
        "bond": -0.02,
        "loan": -0.04,
        "derivative": -0.05,
    },

    "Product Launch": {
        "equity": 0.05,
        "bond": 0.00,
        "loan": 0.00,
        "derivative": 0.02,
    },

    "Earnings": {
        "equity": -0.04,
        "bond": -0.01,
        "loan": -0.01,
        "derivative": -0.03,
    },

    "Other": {
        "equity": -0.03,
        "bond": -0.01,
        "loan": -0.01,
        "derivative": -0.02,
    },
}


# ============================================================
# SCENARIO METADATA
# ============================================================

SCENARIO_DESCRIPTIONS = {

    "Geopolitical":
        "Models portfolio sensitivity to geopolitical disruption, "
        "sanctions, conflict or supply-chain shocks.",

    "Macroeconomic":
        "Models the effect of inflation, interest-rate changes, "
        "economic slowdown or recessionary pressure.",

    "Credit Event":
        "Models portfolio exposure to defaults, downgrades, "
        "liquidity stress and credit deterioration.",

    "Merger/Acquisition":
        "Models potential portfolio effects from major corporate "
        "transactions and acquisition activity.",

    "Regulatory":
        "Models the effect of regulatory actions, compliance "
        "events, fines or antitrust intervention.",

    "Product Launch":
        "Models portfolio sensitivity to major product launches "
        "and associated market reactions.",

    "Earnings":
        "Models portfolio sensitivity to earnings surprises, "
        "guidance changes and corporate performance.",

    "Other":
        "Generic market stress scenario used when no specific "
        "event category is available.",
}


# ============================================================
# ASSET CLASS NORMALIZATION
# ============================================================

ASSET_TYPE_ALIASES = {

    "equities": "equity",
    "stocks": "equity",
    "stock": "equity",
    "equity": "equity",

    "bonds": "bond",
    "bond": "bond",
    "fixed income": "bond",

    "loans": "loan",
    "loan": "loan",
    "credit": "loan",

    "derivatives": "derivative",
    "derivative": "derivative",

}


def normalize_asset_type(asset_type):
    """
    Converts different asset-type spellings into the
    standardized internal representation.
    """

    if pd.isna(asset_type):
        return "unknown"

    value = str(asset_type).strip().lower()

    return ASSET_TYPE_ALIASES.get(value, value)


# ============================================================
# SCENARIO MULTIPLIER
# ============================================================

def scenario_multiplier(impact_score):
    """
    Converts a 1-10 impact score into a bounded scenario
    multiplier.

    7/10 = baseline scenario
    1-6  = progressively lower stress
    8-10 = progressively higher stress

    The multiplier is bounded to avoid unrealistic shocks.
    """

    try:
        impact_score = float(impact_score)
    except (TypeError, ValueError):
        impact_score = 7.0

    impact_score = max(1.0, min(10.0, impact_score))

    multiplier = impact_score / 7.0

    return max(0.5, min(1.5, multiplier))


# ============================================================
# MAIN STRESS TEST ENGINE
# ============================================================

def run_stress(portfolio_df, event_type, impact_score):
    """
    Applies an event-driven stress scenario to a portfolio.

    Parameters
    ----------
    portfolio_df : pandas.DataFrame
        Portfolio containing at minimum:
        asset_id, asset_type, market_value

    event_type : str
        Scenario category.

    impact_score : int
        Scenario severity from 1 to 10.

    Returns
    -------
    pandas.DataFrame
        Original portfolio enriched with stress-test outputs.
    """

    if portfolio_df is None or portfolio_df.empty:
        return pd.DataFrame()

    required_columns = {
        "asset_id",
        "asset_type",
        "market_value",
    }

    missing_columns = required_columns - set(portfolio_df.columns)

    if missing_columns:
        raise ValueError(
            f"Portfolio is missing required columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    df = portfolio_df.copy()

    # --------------------------------------------------------
    # Normalize asset classes
    # --------------------------------------------------------

    df["normalized_asset_type"] = (
        df["asset_type"]
        .apply(normalize_asset_type)
    )

    # --------------------------------------------------------
    # Select scenario
    # --------------------------------------------------------

    base_shocks = SHOCKS.get(
        event_type,
        SHOCKS["Other"]
    )

    multiplier = scenario_multiplier(
        impact_score
    )

    # --------------------------------------------------------
    # Apply asset-specific shocks
    # --------------------------------------------------------

    df["base_shock_pct"] = (
        df["normalized_asset_type"]
        .map(base_shocks)
        .fillna(-0.02)
    )

    df["shock_pct"] = (
        df["base_shock_pct"] * multiplier
    )

    # --------------------------------------------------------
    # Calculate stressed market value
    # --------------------------------------------------------

    df["market_value"] = pd.to_numeric(
        df["market_value"],
        errors="coerce"
    ).fillna(0)

    df["stressed_value"] = (
        df["market_value"]
        * (1 + df["shock_pct"])
    )

    # --------------------------------------------------------
    # Calculate P&L impact
    # --------------------------------------------------------

    df["loss"] = (
        df["stressed_value"]
        - df["market_value"]
    )

    # --------------------------------------------------------
    # Calculate absolute loss
    # --------------------------------------------------------

    df["absolute_loss"] = df["loss"].abs()

    # --------------------------------------------------------
    # Portfolio exposure percentage
    # --------------------------------------------------------

    total_market_value = df["market_value"].sum()

    if total_market_value > 0:

        df["portfolio_weight"] = (
            df["market_value"]
            / total_market_value
            * 100
        )

    else:

        df["portfolio_weight"] = 0.0

    # --------------------------------------------------------
    # Loss contribution
    # --------------------------------------------------------

    total_absolute_loss = df["absolute_loss"].sum()

    if total_absolute_loss > 0:

        df["loss_contribution_pct"] = (
            df["absolute_loss"]
            / total_absolute_loss
            * 100
        )

    else:

        df["loss_contribution_pct"] = 0.0

    # --------------------------------------------------------
    # Risk contribution
    # --------------------------------------------------------

    df["risk_contribution"] = (
        df["portfolio_weight"]
        * df["shock_pct"].abs()
    )

    # --------------------------------------------------------
    # Add scenario metadata
    # --------------------------------------------------------

    df["scenario"] = event_type

    df["scenario_impact_score"] = impact_score

    df["scenario_multiplier"] = round(
        multiplier,
        4
    )

    return df


# ============================================================
# PORTFOLIO SUMMARY
# ============================================================

def portfolio_summary(df):
    """
    Produces portfolio-level stress-test metrics.

    Existing dashboard fields are preserved:
        before
        after
        pnl
        loss_pct

    Additional metrics are provided for the upgraded
    dashboard and future analysis.
    """

    if df is None or df.empty:

        return {
            "before": 0,
            "after": 0,
            "pnl": 0,
            "loss_pct": 0,
            "absolute_loss": 0,
            "worst_asset": "N/A",
            "worst_asset_loss": 0,
            "largest_exposure": "N/A",
            "largest_exposure_pct": 0,
        }

    before = float(
        df["market_value"].sum()
    )

    after = float(
        df["stressed_value"].sum()
    )

    pnl = after - before

    loss_pct = (
        (pnl / before) * 100
        if before != 0
        else 0
    )

    # --------------------------------------------------------
    # Worst affected asset
    # --------------------------------------------------------

    worst_index = df["loss"].idxmin()

    worst_asset = str(
        df.loc[worst_index, "asset_id"]
    )

    worst_asset_loss = float(
        df.loc[worst_index, "loss"]
    )

    # --------------------------------------------------------
    # Largest portfolio exposure
    # --------------------------------------------------------

    if "portfolio_weight" in df.columns:

        exposure_index = (
            df["portfolio_weight"].idxmax()
        )

        largest_exposure = str(
            df.loc[
                exposure_index,
                "asset_id"
            ]
        )

        largest_exposure_pct = float(
            df.loc[
                exposure_index,
                "portfolio_weight"
            ]
        )

    else:

        largest_exposure = "N/A"
        largest_exposure_pct = 0

    # --------------------------------------------------------
    # Total absolute loss
    # --------------------------------------------------------

    absolute_loss = float(
        df["absolute_loss"].sum()
        if "absolute_loss" in df.columns
        else abs(pnl)
    )

    return {

        "before": round(
            before,
            2
        ),

        "after": round(
            after,
            2
        ),

        "pnl": round(
            pnl,
            2
        ),

        "loss_pct": round(
            loss_pct,
            2
        ),

        "absolute_loss": round(
            absolute_loss,
            2
        ),

        "worst_asset": worst_asset,

        "worst_asset_loss": round(
            worst_asset_loss,
            2
        ),

        "largest_exposure": largest_exposure,

        "largest_exposure_pct": round(
            largest_exposure_pct,
            2
        ),
    }


# ============================================================
# EVENT IMPACT SUMMARY
# ============================================================

def event_impact_summary(df):
    """
    Aggregates stress-test results by asset class.

    Useful for explaining WHERE portfolio risk originates.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby("normalized_asset_type")
        .agg(
            exposure=(
                "market_value",
                "sum"
            ),

            stressed_value=(
                "stressed_value",
                "sum"
            ),

            pnl=(
                "loss",
                "sum"
            ),

            average_shock=(
                "shock_pct",
                "mean"
            ),
        )
        .reset_index()
    )

    summary["loss_pct"] = (
        summary["pnl"]
        / summary["exposure"]
        * 100
    ).fillna(0)

    return summary


# ============================================================
# RISK CONCENTRATION ANALYSIS
# ============================================================

def concentration_analysis(df):
    """
    Identifies the asset classes contributing most to
    portfolio stress.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    grouped = (
        df.groupby("normalized_asset_type")
        .agg(
            market_value=(
                "market_value",
                "sum"
            ),

            loss=(
                "loss",
                "sum"
            ),

            risk_contribution=(
                "risk_contribution",
                "sum"
            ),
        )
        .reset_index()
    )

    total_value = grouped["market_value"].sum()

    if total_value > 0:

        grouped["portfolio_weight"] = (
            grouped["market_value"]
            / total_value
            * 100
        )

    else:

        grouped["portfolio_weight"] = 0

    total_loss = grouped["loss"].abs().sum()

    if total_loss > 0:

        grouped["loss_contribution_pct"] = (
            grouped["loss"].abs()
            / total_loss
            * 100
        )

    else:

        grouped["loss_contribution_pct"] = 0

    return grouped.sort_values(
        "loss_contribution_pct",
        ascending=False
    )


# ============================================================
# SCENARIO INFORMATION
# ============================================================

def get_scenario_info(event_type):
    """
    Returns human-readable information about a scenario.
    """

    return {

        "event": event_type,

        "description": SCENARIO_DESCRIPTIONS.get(
            event_type,
            SCENARIO_DESCRIPTIONS["Other"]
        ),

        "baseline": "7/10",

        "assumption":
            "Asset-class shocks are synthetic "
            "scenario assumptions for demonstration.",
    }