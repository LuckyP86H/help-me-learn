from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_session
from ..services.usage import run_chat

router = APIRouter(prefix="/api", tags=["chat"])


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    provider: str
    model: str | None = None
    messages: list[ChatMessage] = Field(min_length=1)


class ChatResponse(BaseModel):
    text: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    try:
        logged = run_chat(
            session,
            req.provider,
            [m.model_dump() for m in req.messages],
            req.model,
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e.args[0]))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")
    return ChatResponse(
        text=logged.result.text,
        provider=logged.provider,
        model=logged.result.model,
        input_tokens=logged.result.input_tokens,
        output_tokens=logged.result.output_tokens,
        latency_ms=logged.latency_ms,
    )
