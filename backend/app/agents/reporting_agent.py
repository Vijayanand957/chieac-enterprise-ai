"""Reporting agent: synthesizes outputs from other agents into an executive
summary. Recommendation agent: turns findings into prioritized action items."""
from __future__ import annotations

import json

from app.agents.llm_client import complete

SUMMARY_SYSTEM_PROMPT = """You are the Reporting Agent for an executive audience.
Given raw findings (metrics, forecasts, retrieved facts) from other agents,
produce a tight executive summary: 1 headline sentence, 3-5 key metric bullet
points, and a short risks section. Avoid jargon. Return plain text, no markdown
headers."""

RECOMMENDATION_SYSTEM_PROMPT = """You are the Recommendation Agent. Given a set
of findings and identified risks, produce 3-5 prioritized, concrete
recommendations an operations leader could act on this week. Each
recommendation should be one sentence, action-oriented, and specific."""


def summarize(findings: dict) -> str:
    return complete(SUMMARY_SYSTEM_PROMPT, json.dumps(findings, default=str))


def recommend(findings: dict, risks: list[str]) -> list[str]:
    payload = json.dumps({"findings": findings, "risks": risks}, default=str)
    raw = complete(RECOMMENDATION_SYSTEM_PROMPT, payload)
    # Split into clean bullet items regardless of how the model formats them
    lines = [ln.strip("-• \t") for ln in raw.splitlines() if ln.strip()]
    return lines[:5]
