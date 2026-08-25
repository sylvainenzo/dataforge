import uuid
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai import AIMessage, AISession, MessageRole, TutorMode
from app.services.ai_tutor_prompts import SYSTEM_PROMPTS

MAX_HISTORY_MESSAGES = 20


class AITutorNotConfiguredError(Exception):
    pass


def _client() -> AsyncAnthropic:
    if not settings.anthropic_api_key:
        raise AITutorNotConfiguredError("ANTHROPIC_API_KEY is not set")
    return AsyncAnthropic(api_key=settings.anthropic_api_key)


async def create_session(db: AsyncSession, *, user_id: uuid.UUID, mode: TutorMode, context: dict) -> AISession:
    session = AISession(user_id=user_id, mode=mode, context=context)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID) -> AISession | None:
    result = await db.execute(
        select(AISession).where(AISession.id == session_id, AISession.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_message_history(db: AsyncSession, session_id: uuid.UUID) -> list[AIMessage]:
    result = await db.execute(
        select(AIMessage).where(AIMessage.session_id == session_id).order_by(AIMessage.created_at)
    )
    return list(result.scalars().all())


def _build_context_block(context: dict) -> str:
    parts = []
    if lesson_title := context.get("lesson_title"):
        parts.append(f"Current lesson: {lesson_title}")
    if code := context.get("code"):
        parts.append(f"Learner's current code:\n```\n{code}\n```")
    if error := context.get("error_message"):
        parts.append(f"Error they're seeing:\n```\n{error}\n```")
    if skill_level := context.get("skill_level"):
        parts.append(f"Learner's stated skill level: {skill_level}")
    return "\n\n".join(parts)


async def stream_reply(
    db: AsyncSession, *, session: AISession, user_message: str
) -> AsyncIterator[str]:
    """Persists the user message immediately, streams the assistant's reply
    token-by-token, then persists the full assistant reply once streaming
    completes. Raises AITutorNotConfiguredError before anything is
    persisted if no API key is set, so a misconfigured server doesn't leave
    a dangling user message with no reply."""

    client = _client()  # raises before persisting anything if unconfigured

    db.add(AIMessage(session_id=session.id, role=MessageRole.USER, content=user_message))
    await db.commit()

    history = await get_message_history(db, session.id)
    context_block = _build_context_block(session.context)

    messages = []
    if context_block:
        messages.append({"role": "user", "content": f"[Context]\n{context_block}"})
        messages.append({"role": "assistant", "content": "Understood, I have that context."})
    for msg in history[-MAX_HISTORY_MESSAGES:]:
        role = "user" if msg.role == MessageRole.USER else "assistant"
        messages.append({"role": role, "content": msg.content})

    full_reply = ""
    async with client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=SYSTEM_PROMPTS[session.mode],
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            full_reply += text
            yield text

    db.add(AIMessage(session_id=session.id, role=MessageRole.ASSISTANT, content=full_reply))
    await db.commit()
