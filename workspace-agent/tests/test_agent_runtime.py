from __future__ import annotations

from uuid import uuid4

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
import pytest
from sqlalchemy.exc import IntegrityError

from agent_service.graph.builder import build_agent
from agent_service.config import ConfigurationError, configure_langsmith
from agent_service.api.chat import ChatRequest, _chat_stream
from agent_service.graph.runtime import get_checkpointer
from agent_service.tools.price_tools import get_mandi_prices_tool
from agent_service.tools.weather_tools import get_weather_tool
from agent_service.tools.geocoding import geocode_location


class FakeModel:
    def bind_tools(self, _tools):
        return self

    def invoke(self, _messages):
        return AIMessage(content="उत्तर तैयार है।")


def test_single_agent_graph_compiles_and_terminates(monkeypatch) -> None:
    monkeypatch.setattr("agent_service.graph.builder.get_model", lambda: FakeModel())
    agent = build_agent(MemorySaver())

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "मौसम कैसा है?"}]},
        config={"configurable": {"thread_id": "test-thread", "user_uid": "user-1"}},
    )

    assert result["messages"][-1].content == "उत्तर तैयार है।"


def test_weather_tool_returns_real_provider_payload(monkeypatch) -> None:
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "timezone": "Asia/Kolkata",
                "daily": {"time": ["2026-10-18"], "weather_code": [1]},
            }

    captured = {}

    def fake_get(url, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return Response()

    monkeypatch.setattr("agent_service.tools.weather_tools.httpx.get", fake_get)
    result = get_weather_tool.invoke(
        {"latitude": 28.6139, "longitude": 77.2090, "days": 1}
    )

    assert result["source"] == "Open-Meteo"
    assert result["daily"]["weather_code"] == [1]
    assert captured["url"] == "https://api.open-meteo.com/v1/forecast"


def test_weather_tool_rejects_invalid_coordinates() -> None:
    result = get_weather_tool.invoke(
        {"latitude": 100, "longitude": 77.2090, "days": 1}
    )

    assert result == {"error": "Invalid latitude or longitude"}


def test_geocode_resolves_location_to_coordinates(monkeypatch) -> None:
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": [
                    {
                        "name": "Meerut",
                        "latitude": 28.9845,
                        "longitude": 77.7064,
                        "country": "India",
                        "admin1": "Uttar Pradesh",
                    }
                ]
            }

    captured = {}

    def fake_get(url, params, timeout):
        captured.update(url=url, params=params, timeout=timeout)
        return Response()

    monkeypatch.setattr("agent_service.tools.geocoding.httpx.get", fake_get)
    result = geocode_location.invoke({"location": "Meerut"})

    assert result["results"][0]["latitude"] == 28.9845
    assert result["results"][0]["longitude"] == 77.7064
    assert captured["url"] == "https://geocoding-api.open-meteo.com/v1/search"


def test_geocode_reports_unknown_location(monkeypatch) -> None:
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {}

    monkeypatch.setattr("agent_service.tools.geocoding.httpx.get", lambda *args, **kwargs: Response())
    result = geocode_location.invoke({"location": "unknown-place"})

    assert result == {"error": "No location found for 'unknown-place'"}


def test_price_tool_validates_query_before_database_access() -> None:
    result = get_mandi_prices_tool.invoke({"commodity": "", "days": 30})

    assert result == {"error": "commodity is required"}


def test_langsmith_tracing_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    assert configure_langsmith() is False


def test_langsmith_tracing_requires_api_key_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="LANGCHAIN_API_KEY"):
        configure_langsmith()


def test_chat_reports_missing_database_user(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent_service.api.chat.ensure_thread_record",
        lambda _thread_id, _user_uid: (_ for _ in ()).throw(
            IntegrityError("statement", {}, Exception("foreign key"))
        ),
    )

    request = ChatRequest(
        message="hello",
        thread_id="thread-test",
        user_uid="missing-user",
        lang="en",
    )

    async def collect() -> list[str]:
        return [event async for event in _chat_stream(request)]

    import asyncio

    events = asyncio.run(collect())
    assert '"code": "user_not_found"' in events[0]
    assert "foreign key" not in events[0]


def test_chat_uses_sync_stream_for_postgres_checkpointer(monkeypatch) -> None:
    class FakeAgent:
        def stream(self, _state, config, stream_mode):
            assert config["configurable"]["thread_id"] == "thread-stream"
            assert stream_mode == "updates"
            yield {
                "agent": {
                    "messages": [AIMessage(content="Test response")]
                }
            }

    monkeypatch.setattr(
        "agent_service.api.chat.ensure_thread_record",
        lambda _thread_id, _user_uid: {"thread_id": _thread_id},
    )
    monkeypatch.setattr("agent_service.api.chat.get_agent", lambda: FakeAgent())

    request = ChatRequest(
        message="hello",
        thread_id="thread-stream",
        user_uid="user-stream",
        lang="en",
    )

    async def collect() -> list[str]:
        return [event async for event in _chat_stream(request)]

    import asyncio

    events = asyncio.run(collect())
    assert any("event: token" in event for event in events)
    assert any("event: done" in event for event in events)


def test_postgres_checkpointer_persists_graph_state(monkeypatch) -> None:
    class PersistentFakeModel(FakeModel):
        def invoke(self, messages):
            return AIMessage(content=f"messages={len(messages)}")

    monkeypatch.setattr(
        "agent_service.graph.builder.get_model",
        lambda: PersistentFakeModel(),
    )
    checkpointer = get_checkpointer()
    agent = build_agent(checkpointer)
    thread_id = f"checkpointer-test-{uuid4().hex}"
    config = {"configurable": {"thread_id": thread_id, "user_uid": "0000"}}

    first = agent.invoke(
        {"messages": [{"role": "user", "content": "पहला संदेश"}]},
        config=config,
    )
    second = agent.invoke(
        {"messages": [{"role": "user", "content": "दूसरा संदेश"}]},
        config=config,
    )

    assert first["messages"][-1].content == "messages=2"
    assert second["messages"][-1].content == "messages=4"
