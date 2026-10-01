"""Pydantic v2 schemas for API request/response bodies."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(..., min_length=1, max_length=4000)


class AgentStep(BaseModel):
    agent: str
    action: str
    summary: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    agent_trace: list[AgentStep]
    sources: list[str] = []


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    chunk_count: int


class ForecastRequest(BaseModel):
    target: str = Field(
        ..., description="Column name to forecast, e.g. 'churn' or 'incidents'"
    )
    horizon: int = Field(default=30, ge=1, le=365)


class ForecastPoint(BaseModel):
    period: str
    predicted: float
    lower: float
    upper: float


class ForecastResponse(BaseModel):
    target: str
    model_name: str
    metrics: dict[str, float]
    forecast: list[ForecastPoint]


class ExecutiveSummaryRequest(BaseModel):
    period: str = "last_30_days"
    focus_areas: list[str] = Field(default_factory=list)


class ExecutiveSummaryResponse(BaseModel):
    summary: str
    key_metrics: dict[str, float]
    risks: list[str]
    recommendations: list[str]
