import json
import logging
import asyncio
from asyncio import to_thread
from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from agent_service.graph.runtime import get_agent
from agent_service.config import langsmith_project
from agent_service.auth import AuthenticatedUser, get_current_user
from agent_service.tools.thread_tools import ensure_thread_record

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
    lang: Literal["hi", "en", "hinglish"] | None = None


def _sse(event: str, payload: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _message_content(message: object) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_blocks = [
            block["text"]
            for block in content
            if isinstance(block, Mapping)
            and block.get("type", "text") == "text"
            and isinstance(block.get("text"), str)
        ]
        return "\n".join(text_blocks)
    return ""


def _stream_agent_events(
    agent: Any,
    state: dict[str, object],
    config: dict[str, object],
    loop: asyncio.AbstractEventLoop,
    events: asyncio.Queue[str | None],
) -> None:
    def send(event: str) -> None:
        loop.call_soon_threadsafe(events.put_nowait, event)

    try:
        final_message = None
        for mode, item in agent.stream(
            state,
            config=config,
            stream_mode=["updates", "messages"],
        ):
            if mode == "messages":
                chunk, metadata = item
                if metadata.get("langgraph_node") == "agent":
                    text = _message_content(chunk)
                    if text:
                        send(_sse("token", {"text": text}))
                continue

            for node_name, node_state in item.items():
                send(_sse("step", {"name": node_name, "status": "complete"}))
                messages = node_state.get("messages", [])
                if node_name == "agent" and messages:
                    candidate = messages[-1]
                    if not getattr(candidate, "tool_calls", None):
                        final_message = candidate

        if final_message is None:
            send(
                _sse(
                    "error",
                    {
                        "code": "agent_no_response",
                        "message": "The agent did not produce a final response.",
                    },
                )
            )
        else:
            send(_sse("done", {"status": "complete"}))
    except Exception:
        logger.exception("KisanSetu agent request failed")
        send(
            _sse(
                "error",
                {
                    "code": "agent_execution_error",
                    "message": "The agent request could not be completed.",
                },
            )
        )
    finally:
        send(None)


async def _chat_stream(request: ChatRequest, user_uid: str) -> AsyncIterator[str]:
    try:
        try:
            thread = await to_thread(
                ensure_thread_record, request.thread_id, user_uid
            )
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
                "user_uid": user_uid,
            },
            "recursion_limit": 12,
            "run_name": "kisansetu-chat",
            "tags": ["kisansetu", "agent-service", "chat"],
            "metadata": {
                "project": langsmith_project(),
                "thread_id": request.thread_id,
                "user_uid": user_uid,
                "language": request.lang or "auto",
            },
        }
        state = {"messages": [HumanMessage(content=request.message)]}
        if request.lang is not None:
            state["language"] = request.lang

        agent = await to_thread(get_agent)
        events: asyncio.Queue[str | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()
        worker = asyncio.create_task(
            to_thread(_stream_agent_events, agent, state, config, loop, events)
        )
        while True:
            event = await events.get()
            if event is None:
                break
            yield event
        await worker
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
async def chat(
    request: ChatRequest,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> StreamingResponse:
    return StreamingResponse(
        _chat_stream(request, user["uid"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )