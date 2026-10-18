from __future__ import annotations

from contextlib import contextmanager
from uuid import uuid4

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
import pytest
from sqlalchemy.exc import IntegrityError

from agent_service.graph.builder import build_agent
from agent_service.config import ConfigurationError, configure_langsmith, gemini_model
from agent_service.api.chat import ChatRequest, _chat_stream, _message_content
from agent_service.llm.model import get_model
from agent_service.graph.runtime import get_checkpointer
from agent_service.tools.price_tools import get_mandi_prices_tool
from agent_service.tools.weather_tools import get_weather_tool
from agent_service.tools.geocoding import geocode_location
from agent_service.tools.thread_tools import Thread


class FakeModel:
    def bind_tools(self, _tools):
        return self

    def invoke(self, _messages, config=None):
        del config
        return AIMessage(content="उत्तर तैयार है।")


def test_single_agent_graph_compiles_and_terminates(monkeypatch) -> None:
    monkeypatch.setattr("agent_service.graph.builder.get_model", lambda: FakeModel())
    agent = build_agent(MemorySaver())

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "मौसम कैसा है?"}]},
        config={"configurable": {"thread_id": "test-thread", "user_uid": "user-1"}},
    )

    assert result["messages"][-1].content == "उत्तर तैयार है।"


def test_thread_model_metadata_does_not_require_users_mapping() -> None:
    assert Thread.__table__ in Thread.metadata.sorted_tables


def test_message_content_extracts_text_without_provider_metadata() -> None:
    message = AIMessage(
        content=[
            {
                "type": "text",
                "text": "Hello! I am KisanSetu.",
                "extras": {"signature": "provider-signature"},
            }
        ]
    )

    result = _message_content(message)

    assert result == "Hello! I am KisanSetu."
    assert "provider-signature" not in result


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


def test_price_tool_filters_by_mandi_and_matches_plural_commodity(monkeypatch) -> None:
    class FakeResult:
        def mappings(self):
            return self

        def all(self):
            return [{"commodity": "Tomato", "mandi": "Azadpur", "modal_price": 1800}]

    class FakeDatabase:
        statement = ""
        parameters = {}

        def execute(self, statement, parameters):
            self.statement = str(statement)
            self.parameters = parameters
            return FakeResult()

    database = FakeDatabase()

    @contextmanager
    def fake_session_scope():
        yield database

    monkeypatch.setattr(
        "agent_service.tools.price_tools.session_scope", fake_session_scope
    )

    result = get_mandi_prices_tool.invoke(
        {
            "commodity": "tomatoes",
            "mandi_name": "Azadpur",
            "district": "North Delhi",
            "days": 14,
        }
    )

    assert result["prices"][0]["mandi"] == "Azadpur"
    assert "JOIN mandis AS m" in database.statement
    assert "regexp_replace(lower(trim(p.commodity))" in database.statement
    assert database.parameters["mandi_name"] == "%Azadpur%"
    assert database.parameters["district"] == "%North Delhi%"
    assert database.parameters["days"] == 14


def test_langsmith_tracing_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    assert configure_langsmith() is False


def test_gemini_model_uses_configured_model(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.8-flash")

    assert gemini_model() == "gemini-3.8-flash"


def test_gemini_model_has_sufficient_stream_timeout(monkeypatch) -> None:
    captured = {}

    class FakeChatModel:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(
        "agent_service.llm.model.ChatGoogleGenerativeAI",
        FakeChatModel,
    )

    get_model()

    assert captured["timeout"] == 60
    assert captured["streaming"] is True


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
        lang="en",
    )

    async def collect() -> list[str]:
        return [event async for event in _chat_stream(request, "missing-user")]

    import asyncio

    events = asyncio.run(collect())
    assert '"code": "user_not_found"' in events[0]
    assert "foreign key" not in events[0]


def test_chat_uses_sync_stream_for_postgres_checkpointer(monkeypatch) -> None:
    class FakeAgent:
        def stream(self, _state, config, stream_mode):
            assert config["configurable"]["thread_id"] == "thread-stream"
            assert stream_mode == ["updates", "messages"]
            yield ("messages", (AIMessage(content="Test response"), {"langgraph_node": "agent"}))
            yield ("updates", {"agent": {"messages": [AIMessage(content="Test response")]}})

    monkeypatch.setattr(
        "agent_service.api.chat.ensure_thread_record",
        lambda _thread_id, _user_uid: {"thread_id": _thread_id},
    )
    monkeypatch.setattr("agent_service.api.chat.get_agent", lambda: FakeAgent())

    request = ChatRequest(
        message="hello",
        thread_id="thread-stream",
        lang="en",
    )

    async def collect() -> list[str]:
        return [event async for event in _chat_stream(request, "user-stream")]

    import asyncio

    events = asyncio.run(collect())
    assert any("event: token" in event for event in events)
    assert any("event: done" in event for event in events)


def test_postgres_checkpointer_persists_graph_state(monkeypatch) -> None:
    class PersistentFakeModel(FakeModel):
        def invoke(self, messages, config=None):
            del config
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
