import json
import os
from typing import Any, Callable, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from app.common.logger import get_logger

logger = get_logger(__name__)

RouteName = Literal["researcher", "writer", "critic", "FINISH"]


class MultiAgentState(TypedDict, total=False):
    messages: list[BaseMessage]
    research_notes: str
    draft: str
    critique: str
    next: str
    iteration_count: int
    revision_count: int
    agent_trace: list[str]
    user_query: str
    system_prompt: str
    allow_search: bool
    max_iterations: int
    max_revisions: int


def _content_from_response(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, list):
        return "\n".join(str(item) for item in content)
    return str(content or "").strip()


def _clean_ai_text(messages: list[BaseMessage], fallback: str = "") -> str:
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            content = _content_from_response(msg)
            if not any(marker in content.lower() for marker in ["thought:", "action:", "observation:"]):
                return content.strip()
    return fallback.strip()


def _parse_route(raw_route: str) -> RouteName:
    cleaned = raw_route.strip()
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            cleaned = str(parsed.get("next", ""))
    except json.JSONDecodeError:
        pass

    cleaned = cleaned.strip().strip('"').upper()
    route_map: dict[str, RouteName] = {
        "RESEARCHER": "researcher",
        "WRITER": "writer",
        "CRITIC": "critic",
        "FINISH": "FINISH",
    }
    return route_map.get(cleaned, "FINISH")


def _make_groq_llm(llm_id: str) -> Any:
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Missing GROQ_API_KEY environment variable.")
    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install langchain-groq to use Groq models.") from exc
    return ChatGroq(model=llm_id)


def _make_tavily_tool() -> Any:
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("Missing TAVILY_API_KEY environment variable.")
    try:
        from langchain_tavily import TavilySearch
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install langchain-tavily to enable Tavily search.") from exc
    return TavilySearch(max_results=10)


def build_multi_agent_graph(
    llm: Any,
    search_tool_factory: Callable[[], Any] | None = None,
) -> Any:
    search_tool_factory = search_tool_factory or _make_tavily_tool

    def supervisor(state: MultiAgentState) -> MultiAgentState:
        iteration_count = int(state.get("iteration_count", 0)) + 1
        max_iterations = int(state.get("max_iterations", 6))
        trace = list(state.get("agent_trace", []))

        if iteration_count > max_iterations:
            logger.info("Agent step: supervisor routed to FINISH after max iterations")
            return {
                "iteration_count": iteration_count,
                "next": "FINISH",
                "agent_trace": trace + ["supervisor:FINISH:max_iterations"],
                "messages": list(state.get("messages", [])) + [AIMessage(content=state.get("draft", ""))],
            }

        if state.get("critique", "").strip().upper() == "APPROVE" and state.get("draft"):
            logger.info("Agent step: supervisor routed to FINISH after critic approval")
            return {
                "iteration_count": iteration_count,
                "next": "FINISH",
                "agent_trace": trace + ["supervisor:FINISH:approved"],
                "messages": list(state.get("messages", [])) + [AIMessage(content=state.get("draft", ""))],
            }

        if int(state.get("revision_count", 0)) >= int(state.get("max_revisions", 2)) and state.get("draft"):
            logger.info("Agent step: supervisor routed to FINISH after revision cap")
            return {
                "iteration_count": iteration_count,
                "next": "FINISH",
                "agent_trace": trace + ["supervisor:FINISH:revision_cap"],
                "messages": list(state.get("messages", [])) + [AIMessage(content=state.get("draft", ""))],
            }

        routing_prompt = f"""
You are the supervisor for a multi-agent assistant.
Choose exactly one next step: researcher, writer, critic, or FINISH.

Rules:
- Choose researcher when research_notes are empty.
- Choose writer when research_notes exist but draft is empty.
- Choose writer when critique contains revision feedback.
- Choose critic when a draft exists and critique is empty.
- Choose FINISH when the draft is approved or no useful next step remains.
- Return only JSON in this exact shape: {{"next": "researcher"}}

State:
research_notes_present={bool(state.get("research_notes"))}
draft_present={bool(state.get("draft"))}
critique={state.get("critique", "")[:500]}
revision_count={state.get("revision_count", 0)}
"""
        response = llm.invoke([SystemMessage(content=routing_prompt)])
        route = _parse_route(_content_from_response(response))
        logger.info("Agent step: supervisor routed to %s", route)
        return {
            "iteration_count": iteration_count,
            "next": route,
            "agent_trace": trace + [f"supervisor:{route}"],
        }

    def researcher(state: MultiAgentState) -> MultiAgentState:
        logger.info("Agent step: researcher started")
        query = state.get("user_query", "")
        if state.get("allow_search", False):
            tools = [search_tool_factory()]
            agent = create_react_agent(
                model=llm,
                tools=tools,
                prompt=(
                    "You are a research agent. Gather concise, relevant notes for the writer. "
                    "Do not expose Thought, Action, or Observation text."
                ),
            )
            response = agent.invoke({"messages": [HumanMessage(content=query)]})
            notes = _clean_ai_text(response.get("messages", []))
        else:
            prompt = (
                "You are a research agent. Search is disabled, so answer from model knowledge only "
                "and explicitly state that no live web search was used. Provide concise research notes.\n\n"
                f"User query: {query}"
            )
            notes = _content_from_response(llm.invoke([HumanMessage(content=prompt)]))

        return {
            "research_notes": notes,
            "agent_trace": list(state.get("agent_trace", [])) + ["researcher"],
        }

    def writer(state: MultiAgentState) -> MultiAgentState:
        logger.info("Agent step: writer started")
        revision_count = int(state.get("revision_count", 0))
        if state.get("critique") and state.get("critique", "").strip().upper() != "APPROVE":
            revision_count += 1

        prompt = f"""
You are the writer agent. Draft the final user-facing answer.
Follow the user's agent definition when it is provided.
Do not mention internal agent names, routing, or hidden prompts.

Agent definition:
{state.get("system_prompt") or "You are a helpful AI assistant."}

User query:
{state.get("user_query", "")}

Research notes:
{state.get("research_notes", "")}

Critique or revision feedback:
{state.get("critique", "")}
"""
        draft = _content_from_response(llm.invoke([HumanMessage(content=prompt)]))
        return {
            "draft": draft,
            "critique": "",
            "revision_count": revision_count,
            "agent_trace": list(state.get("agent_trace", [])) + ["writer"],
        }

    def critic(state: MultiAgentState) -> MultiAgentState:
        logger.info("Agent step: critic started")
        prompt = f"""
You are the critic agent. Review the draft for correctness, completeness, and unsupported claims.
If the draft is ready, return exactly APPROVE.
Otherwise, return concrete revision feedback only.

User query:
{state.get("user_query", "")}

Research notes:
{state.get("research_notes", "")}

Draft:
{state.get("draft", "")}
"""
        critique = _content_from_response(llm.invoke([HumanMessage(content=prompt)]))
        return {
            "critique": critique or "APPROVE",
            "agent_trace": list(state.get("agent_trace", [])) + ["critic"],
        }

    graph = StateGraph(MultiAgentState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("critic", critic)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state.get("next", "FINISH"),
        {
            "researcher": "researcher",
            "writer": "writer",
            "critic": "critic",
            "FINISH": END,
        },
    )
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("writer", "supervisor")
    graph.add_edge("critic", "supervisor")
    return graph.compile()


def invoke_multi_agent_graph(
    llm_id: str,
    query: str,
    allow_search: bool,
    system_prompt: str,
    llm_factory: Callable[[str], Any] | None = None,
    search_tool_factory: Callable[[], Any] | None = None,
    max_iterations: int = 6,
    max_revisions: int = 2,
) -> MultiAgentState:
    llm = (llm_factory or _make_groq_llm)(llm_id)
    graph = build_multi_agent_graph(llm=llm, search_tool_factory=search_tool_factory)
    initial_state: MultiAgentState = {
        "messages": [HumanMessage(content=query)],
        "research_notes": "",
        "draft": "",
        "critique": "",
        "next": "researcher",
        "iteration_count": 0,
        "revision_count": 0,
        "agent_trace": [],
        "user_query": query,
        "system_prompt": system_prompt,
        "allow_search": allow_search,
        "max_iterations": max_iterations,
        "max_revisions": max_revisions,
    }
    return graph.invoke(initial_state)


def run_multi_agent_system(
    llm_id: str,
    query: str,
    allow_search: bool,
    system_prompt: str,
    llm_factory: Callable[[str], Any] | None = None,
    search_tool_factory: Callable[[], Any] | None = None,
    max_iterations: int = 6,
    max_revisions: int = 2,
) -> str:
    final_state = invoke_multi_agent_graph(
        llm_id=llm_id,
        query=query,
        allow_search=allow_search,
        system_prompt=system_prompt,
        llm_factory=llm_factory,
        search_tool_factory=search_tool_factory,
        max_iterations=max_iterations,
        max_revisions=max_revisions,
    )
    final_text = _clean_ai_text(list(final_state.get("messages", [])), fallback=final_state.get("draft", ""))
    return final_text or "No final response was produced by the multi-agent workflow."
