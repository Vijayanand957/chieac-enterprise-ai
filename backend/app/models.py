"""ORM models for structured operational data used by the SQL/analytics agent."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, default="upload")
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    title: Mapped[str] = mapped_column(String, default="New conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String)  # user | assistant | agent:<name>
    content: Mapped[str] = mapped_column(Text)
    agent_trace: Mapped[str] = mapped_column(
        Text, default="[]"
    )  # JSON list of agent steps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class OperationalMetric(Base):
    """Generic fact table the SQL agent queries for business questions
    (e.g. 'what was our incident rate last month?')."""

    __tablename__ = "operational_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    metric_name: Mapped[str] = mapped_column(String, index=True)
    dimension: Mapped[str] = mapped_column(
        String, default="overall"
    )  # e.g. region, product
    value: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    model_name: Mapped[str] = mapped_column(String)
    target: Mapped[str] = mapped_column(String)
    input_rows: Mapped[int] = mapped_column(Integer)
    metrics_json: Mapped[str] = mapped_column(Text)  # JSON: {"rmse":..., "auc":...}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
