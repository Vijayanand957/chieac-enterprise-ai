"""Thin wrapper around the Anthropic API shared by all agents. Centralizing
this makes it a one-line swap to Azure OpenAI or Bedrock in a different
deployment target."""

from __future__ import annotations

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

settings = get_settings()
_client = Anthropic(api_key=settings.anthropic_api_key)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def complete(system: str, user: str, max_tokens: int | None = None) -> str:
    response = _client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens or settings.llm_max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
