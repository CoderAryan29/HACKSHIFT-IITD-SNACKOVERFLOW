from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent_service.graph.state import AgentState
from agent_service.system_prompts import AGENT_PROMPT
from agent_service.tools.langchain_tool_register import agent_tools
from agent_service.llm import get_model


def _agent_messages(state: AgentState) -> list[BaseMessage]:
    language = state.get("language", "en")
    prompt = f"""{AGENT_PROMPT}
Respond in language: {language}.
Farmer profile: {state.get("farmer_profile")}
Farm context: {state.get("farm")}
Crop context: {state.get("crop")}
"""
    return [SystemMessage(content=prompt), *state["messages"]]


def agent_node(
    state: AgentState, config: RunnableConfig
) -> dict[str, list[BaseMessage]]:
    response = get_model().bind_tools(agent_tools).invoke(
        _agent_messages(state), config=config
    )
    return {"messages": [response]}


def build_agent(checkpointer: BaseCheckpointSaver):
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(agent_tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=checkpointer)