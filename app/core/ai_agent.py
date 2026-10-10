import os
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.prebuilt import create_react_agent

from app.common.logger import get_logger
from app.core.multi_agent import run_multi_agent_system

logger = get_logger(__name__)


def _make_groq_llm(llm_id: str):
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Missing GROQ_API_KEY environment variable.")
    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install langchain-groq to use Groq models.") from exc
    return ChatGroq(model=llm_id)


def _make_tavily_tool():
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("Missing TAVILY_API_KEY environment variable.")
    try:
        from langchain_tavily import TavilySearch
    except ImportError as exc:
        raise RuntimeError("Missing dependency: install langchain-tavily to enable Tavily search.") from exc
    return TavilySearch(max_results=10)


def get_response_from_ai_agents(
    llm_id: str,
    query,
    allow_search: bool,
    system_prompt: str,
    mode: str = "single",
) -> str | None:

    try:
        if not isinstance(query, str):
            if isinstance(query, list):
                query = "\n".join(map(str, query))
            else:
                query = str(query)

        if mode == "multi":
            return run_multi_agent_system(
                llm_id=llm_id,
                query=query,
                allow_search=allow_search,
                system_prompt=system_prompt,
            )

        if mode != "single":
            return "Error while processing the request: invalid mode. Use 'single' or 'multi'."

        llm = _make_groq_llm(llm_id)
        tools = [_make_tavily_tool()] if allow_search else []

        clean_prompt = system_prompt or """
You are a helpful AI assistant.

Rules:
- Use tools only if absolutely necessary
- DO NOT expose Thought, Action, Observation
- DO NOT mention tools or searches
- Provide a clean, final answer only
"""

        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=clean_prompt,
        )

        state = {
            "messages": [
                HumanMessage(content=query),
            ]
        }

        response = agent.invoke(state)
        messages = response.get("messages", [])

        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                if not any(
                    k in msg.content.lower()
                    for k in ["thought:", "action:", "observation:"]
                ):
                    return msg.content.strip()

        return None

    except Exception as e:
        logger.exception("Failed to get response from AI agents")
        return f"Error while processing the request: {str(e)}"
