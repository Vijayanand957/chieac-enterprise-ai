"""Orchestrator agent: the entry point for the /chat endpoint. It classifies
the user's intent with a cheap LLM call, routes to one or more specialist
agents (retrieval / SQL / forecasting / reporting), and synthesizes a final
answer with a visible agent trace for transparency/debuggability -- a common
production pattern for multi-agent systems.
"""

from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import forecasting_agent, reporting_agent, retrieval_agent, sql_agent
from app.agents.llm_client import complete

ROUTER_SYSTEM_PROMPT = """You are a routing classifier for an enterprise AI
operations assistant. Given a user question, decide which specialist
agent(s) should handle it. Respond with ONLY a JSON array of one or more of:
"retrieval" (questions about uploaded documents/policies/reports),
"sql" (questions about historical operational metrics/trends/comparisons),
"forecast" (questions asking to predict/forecast future values or risk),
"general" (greetings, small talk, or anything not covered above).
Example response: ["sql", "forecast"]"""


def _classify(message: str) -> list[str]:
    raw = complete(ROUTER_SYSTEM_PROMPT, message, max_tokens=50)
    try:
        intents = json.loads(raw.strip())
        valid = {"retrieval", "sql", "forecast", "general"}
        intents = [i for i in intents if i in valid]
        return intents or ["general"]
    except (json.JSONDecodeError, TypeError):
        return ["general"]


async def handle_message(db: AsyncSession, message: str) -> dict:
    trace: list[dict] = []
    intents = _classify(message)
    trace.append(
        {
            "agent": "orchestrator",
            "action": "classify_intent",
            "summary": f"Routed to: {', '.join(intents)}",
        }
    )

    findings: dict = {}
    sources: list[str] = []

    if "retrieval" in intents:
        result = retrieval_agent.run(message)
        findings["retrieval"] = result["answer"]
        sources.extend(result["sources"])
        trace.append(
            {
                "agent": "retrieval",
                "action": "search_documents",
                "summary": f"Found {len(result['sources'])} source(s)",
            }
        )

    if "sql" in intents:
        result = await sql_agent.run(db, message)
        findings["analytics"] = result["answer"]
        trace.append(
            {
                "agent": "sql_analytics",
                "action": "query_metrics",
                "summary": f"Analyzed {result['row_count']} metric rows",
            }
        )

    if "forecast" in intents:
        metric_guess = _guess_metric_name(message)
        result = await forecasting_agent.run(db, metric_guess)
        findings["forecast"] = result["answer"]
        trace.append(
            {
                "agent": "forecasting",
                "action": "generate_forecast",
                "summary": f"Forecast for '{metric_guess}'",
            }
        )

    if "general" in intents and not findings:
        answer = complete(
            "You are a helpful enterprise operations assistant. Answer briefly and helpfully.",
            message,
        )
        trace.append(
            {
                "agent": "general",
                "action": "direct_answer",
                "summary": "Answered directly",
            }
        )
        return {"answer": answer, "trace": trace, "sources": []}

    # Synthesize a single coherent answer from whichever agents contributed
    if len(findings) == 1:
        final_answer = next(iter(findings.values()))
    else:
        final_answer = reporting_agent.summarize(findings)
        trace.append(
            {
                "agent": "reporting",
                "action": "synthesize",
                "summary": "Combined multi-agent findings into one answer",
            }
        )

    return {"answer": final_answer, "trace": trace, "sources": sources}


def _guess_metric_name(message: str) -> str:
    """Very lightweight heuristic; a production version would look this up
    against the distinct metric_name values in the DB via sql_agent.available_metrics."""
    lowered = message.lower()
    for keyword in ["churn", "incident", "revenue", "latency", "risk", "ticket"]:
        if keyword in lowered:
            return keyword
    return "churn"
