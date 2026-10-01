"""Generates a synthetic customer-churn dataset and a synthetic operational
metrics time series, purely for local development/demo/training purposes."""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# --- Churn dataset for XGBoost training ---
n = 2000
tenure_months = rng.integers(1, 72, n)
monthly_spend = rng.normal(70, 25, n).clip(10, 300)
support_tickets = rng.poisson(1.5, n)
satisfaction_score = rng.normal(7, 2, n).clip(1, 10)

churn_prob = (
    0.35
    - 0.004 * tenure_months
    + 0.002 * support_tickets * 5
    - 0.02 * satisfaction_score
    + 0.001 * (monthly_spend - 70)
)
churn_prob = churn_prob.clip(0.02, 0.9)
churn = rng.binomial(1, churn_prob)

churn_df = pd.DataFrame(
    {
        "tenure_months": tenure_months,
        "monthly_spend": monthly_spend.round(2),
        "support_tickets": support_tickets,
        "satisfaction_score": satisfaction_score.round(1),
        "churn": churn,
    }
)
churn_df.to_csv("churn_sample.csv", index=False)

# --- Operational metrics time series (for forecasting agent demo) ---
days = pd.date_range("2025-01-01", periods=180, freq="D")
base_incident = 8 + 0.03 * np.arange(180) + rng.normal(0, 1.5, 180)
metrics_df = pd.DataFrame(
    {
        "metric_name": "incidents",
        "dimension": "overall",
        "value": base_incident.clip(0).round(1),
        "recorded_at": days,
    }
)
metrics_df.to_csv("operational_metrics_sample.csv", index=False)

print("Wrote churn_sample.csv and operational_metrics_sample.csv")
