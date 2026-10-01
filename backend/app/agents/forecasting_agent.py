"""Forecasting agent: wraps the ML forecasting layer and narrates results in
business language (risk direction, magnitude, confidence)."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm_client import complete
from app.ml.forecasting import time_series_forecast
from app.models import OperationalMetric

SYSTEM_PROMPT = """You are the Forecasting Agent. Given a metric name and a list
of forecasted future values with confidence bands, explain in 3-5 sentences
what the trend means operationally (e.g. rising churn risk, stabilizing
incident rate) and one concrete recommended action. Be concise and concrete,
citing the specific numbers."""


async def run(db: AsyncSession, metric_name: str, horizon: int = 30) -> dict:
    stmt = (
        select(OperationalMetric)
        .where(OperationalMetric.metric_name == metric_name)
        .order_by(OperationalMetric.recorded_at.asc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    if len(rows) < 4:
        return {
            "answer": f"Not enough history for '{metric_name}' to forecast (need >= 4 data points).",
            "forecast": [],
        }

    series = pd.Series([r.value for r in rows])
    forecast = time_series_forecast(series, horizon=horizon)

    summary_input = (
        f"Metric: {metric_name}\n"
        f"Last observed value: {series.iloc[-1]}\n"
        f"Forecast (first 5 of {len(forecast)} periods): {forecast[:5]}"
    )
    narrative = complete(SYSTEM_PROMPT, summary_input)
    return {"answer": narrative, "forecast": forecast}
