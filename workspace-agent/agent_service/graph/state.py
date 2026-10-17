from __future__ import annotations

from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


Language = Literal["hi", "en", "hinglish"]
ToolName = Literal["diagnose", "weather", "price", "market", "treatment_rag"]
PlanConfidence = Literal["high", "medium", "low", "trend_only"]
ActionWhen = Literal["today", "next_3_days", "selling_window"]
ActionPriority = Literal["high", "medium", "low"]


class ActionSource(BaseModel):
    label: str
    url: str | None = None
    date: str | None = None


class Action(BaseModel):
    when: ActionWhen
    title: str
    reason: str
    priority: ActionPriority
    sources: list[ActionSource] = Field(default_factory=list)


class ActionPlan(BaseModel):
    language: Language
    summary: str
    actions: list[Action] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: PlanConfidence
    data_as_of: dict[str, str | None] = Field(
        default_factory=lambda: {"prices": None, "weather": None}
    )


class ToolResult(BaseModel):
    status: Literal["ok", "unavailable", "error"]
    tool: ToolName
    message: str
    timestamp: str
    source: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class AgentFlags(TypedDict, total=False):
    low_confidence: bool
    missing_info: bool
    blocked_reason: str | None


class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    user_uid: str
    thread_id: str
    language: Language
    farmer_profile: dict[str, Any] | None
    farm: dict[str, Any] | None
    crop: str | None
    image_ref: str | None
    tool_results: dict[ToolName, ToolResult]
    plan: ActionPlan | None
    flags: AgentFlags