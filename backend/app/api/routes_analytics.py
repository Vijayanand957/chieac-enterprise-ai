from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import forecasting_agent, reporting_agent, sql_agent
from app.database import get_db
from app.schemas import (
    ExecutiveSummaryRequest,
    ExecutiveSummaryResponse,
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
)

router = APIRouter(tags=["analytics"])


@router.get("/analytics/metrics")
async def list_metrics(db: AsyncSession = Depends(get_db)):
    return {"metrics": await sql_agent.available_metrics(db)}


@router.post("/forecast", response_model=ForecastResponse)
async def forecast(payload: ForecastRequest, db: AsyncSession = Depends(get_db)) -> ForecastResponse:
    result = await forecasting_agent.run(db, payload.target, horizon=payload.horizon)
    points = [
        ForecastPoint(period=f"t+{p['step']}", predicted=p["predicted"], lower=p["lower"], upper=p["upper"])
        for p in result["forecast"]
    ]
    return ForecastResponse(
        target=payload.target,
        model_name="holt-linear-trend",
        metrics={"periods_forecasted": len(points)},
        forecast=points,
    )


@router.post("/reports/executive-summary", response_model=ExecutiveSummaryResponse)
async def executive_summary(payload: ExecutiveSummaryRequest, db: AsyncSession = Depends(get_db)) -> ExecutiveSummaryResponse:
    metrics = await sql_agent.available_metrics(db)
    findings = {"period": payload.period, "focus_areas": payload.focus_areas, "available_metrics": metrics}

    risks = [f"Insufficient recent data for: {m}" for m in payload.focus_areas if m not in metrics] or [
        "No critical data gaps identified."
    ]
    summary_text = reporting_agent.summarize(findings)
    recommendations = reporting_agent.recommend(findings, risks)

    return ExecutiveSummaryResponse(
        summary=summary_text,
        key_metrics={m: 0.0 for m in metrics[:5]},
        risks=risks,
        recommendations=recommendations,
    )
