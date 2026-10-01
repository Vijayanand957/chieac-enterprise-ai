from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import handle_message
from app.database import get_db
from app.models import Conversation, Message
from app.schemas import AgentStep, ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    conversation = None
    if payload.conversation_id:
        conversation = await db.get(Conversation, payload.conversation_id)
    if conversation is None:
        conversation = Conversation(title=payload.message[:60])
        db.add(conversation)
        await db.flush()

    db.add(Message(conversation_id=conversation.id, role="user", content=payload.message))

    result = await handle_message(db, payload.message)

    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            agent_trace=str(result["trace"]),
        )
    )
    await db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result["answer"],
        agent_trace=[AgentStep(**step) for step in result["trace"]],
        sources=result["sources"],
    )


@router.get("/{conversation_id}/history")
async def history(conversation_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    rows = (await db.execute(stmt)).scalars().all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in rows]
