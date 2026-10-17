import json
import logging
from collections.abc import AsyncIterator
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from agent_service.graph.runtime import get_agent
from agent_service.config import langsmith_project
from agent_service.tools.thread_tools import ensure_thread_record

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
    user_uid: str = Field(min_length=1)
    lang: Literal["hi", "en", "hinglish"] | None = None


def _sse(event: str, payload: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _message_content(message: object) -> str:
    content = getattr(message, "content", "")
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)


async def _chat_stream(request: ChatRequest) -> AsyncIterator[str]:
    try:
        try:
            thread = ensure_thread_record(request.thread_id, request.user_uid)
        except IntegrityError:
            yield _sse(
                "error",
                {
                    "code": "user_not_found",
                    "message": "The supplied user account was not found.",
                },
            )
            return
        if "error" in thread:
            yield _sse("error", {"code": "thread_access_denied", "message": thread["error"]})
            return

        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "user_uid": request.user_uid,
            },
            "recursion_limit": 12,
            "run_name": "kisansetu-chat",
            "tags": ["kisansetu", "agent-service", "chat"],
            "metadata": {
                "project": langsmith_project(),
                "thread_id": request.thread_id,
                "user_uid": request.user_uid,
                "language": request.lang or "auto",
            },
        }
        state = {"messages": [HumanMessage(content=request.message)]}
        if request.lang is not None:
            state["language"] = request.lang

        final_message = None
        for update in get_agent().stream(state, config=config, stream_mode="updates"):
            node_name, node_state = next(iter(update.items()))
            yield _sse("step", {"name": node_name, "status": "complete"})
            messages = node_state.get("messages", [])
            if node_name == "agent" and messages:
                candidate = messages[-1]
                if not getattr(candidate, "tool_calls", None):
                    final_message = candidate

        if final_message is None:
            yield _sse(
                "error",
                {
                    "code": "agent_no_response",
                    "message": "The agent did not produce a final response.",
                },
            )
            return
        yield _sse("token", {"text": _message_content(final_message)})
        yield _sse("done", {"status": "complete"})
    except Exception:
        logger.exception("KisanSetu agent request failed")
        yield _sse(
            "error",
            {
                "code": "agent_execution_error",
                "message": "The agent request could not be completed.",
            },
        )


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        _chat_stream(request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )