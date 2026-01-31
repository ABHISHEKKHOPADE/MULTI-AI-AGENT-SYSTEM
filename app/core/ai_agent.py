from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

def get_response_from_ai_agents(
    llm_id: str,
    query,
    allow_search: bool,
    system_prompt: str
) -> str | None:

    try:
      
        if not isinstance(query, str):
            if isinstance(query, list):
                query = "\n".join(map(str, query))
            else:
                query = str(query)

        # LLM
        llm = ChatGroq(model=llm_id)

        # Tools
        tools = [TavilySearch(max_results=10)] if allow_search else []

        
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
            prompt=clean_prompt
        )

        
        state = {
            "messages": [
                HumanMessage(content=query)
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
