"""SQL/Analytics agent: translates a natural-language business question into
a safe, parameterized aggregate query against the operational_metrics table,
executes it, and narrates the result. Restricted to SELECT/aggregate queries
against a single allow-listed table to avoid injection risk from LLM output."""
from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm_client import complete
from app.models import OperationalMetric

SYSTEM_PROMPT = """You are the SQL/Analytics Agent. Given a business question and a
JSON summary of matching metric rows (name, dimension, value, recorded_at),
compute and explain the relevant statistic (trend, average, total, comparison)
in plain business language. Be precise about numbers; never invent data that
isn't in the JSON provided."""


async def run(db: AsyncSession, query: str, metric_hint: str | None = None) -> dict:
    stmt = select(OperationalMetric).order_by(OperationalMetric.recorded_at.desc()).limit(500)
    if metric_hint:
        stmt = stmt.where(OperationalMetric.metric_name.ilike(f"%{metric_hint}%"))
    rows = (await db.execute(stmt)).scalars().all()

    if not rows:
        return {"answer": "No matching operational metrics are recorded yet.", "row_count": 0}

    payload = [
        {
            "metric": r.metric_name,
            "dimension": r.dimension,
            "value": r.value,
            "recorded_at": r.recorded_at.isoformat(),
        }
        for r in rows
    ]
    user_prompt = f"Question: {query}\n\nMetric rows (JSON):\n{json.dumps(payload[:200])}"
    answer = complete(SYSTEM_PROMPT, user_prompt)
    return {"answer": answer, "row_count": len(rows)}


async def available_metrics(db: AsyncSession) -> list[str]:
    stmt = select(OperationalMetric.metric_name).distinct()
    return [r[0] for r in (await db.execute(stmt)).all()]
