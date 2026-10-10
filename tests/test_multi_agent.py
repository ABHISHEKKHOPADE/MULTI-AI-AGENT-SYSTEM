from langchain_core.messages import AIMessage

from app.core import ai_agent
from app.core.multi_agent import invoke_multi_agent_graph


class FakeLLM:
    def __init__(self, supervisor_routes, critic_responses=None):
        self.supervisor_routes = list(supervisor_routes)
        self.critic_responses = list(critic_responses or ["APPROVE"])

    def invoke(self, messages):
        prompt = messages[-1].content
        if "Choose exactly one next step" in prompt:
            route = self.supervisor_routes.pop(0) if self.supervisor_routes else "FINISH"
            return AIMessage(content=f'{{"next": "{route}"}}')
        if "You are a research agent" in prompt:
            return AIMessage(content="No live web search was used. Research notes.")
        if "You are the writer agent" in prompt:
            return AIMessage(content="Draft answer.")
        if "You are the critic agent" in prompt:
            response = self.critic_responses.pop(0) if self.critic_responses else "APPROVE"
            return AIMessage(content=response)
        return AIMessage(content="Single agent answer.")


class FakeSingleAgent:
    def invoke(self, state):
        return {"messages": [AIMessage(content="Single agent answer.")]}


def test_supervisor_routing_order():
    fake_llm = FakeLLM(["researcher", "writer", "critic", "FINISH"], ["APPROVE"])

    state = invoke_multi_agent_graph(
        llm_id="fake",
        query="What is this?",
        allow_search=False,
        system_prompt="Be helpful.",
        llm_factory=lambda _: fake_llm,
    )

    assert state["agent_trace"] == [
        "supervisor:researcher",
        "researcher",
        "supervisor:writer",
        "writer",
        "supervisor:critic",
        "critic",
        "supervisor:FINISH:approved",
    ]
    assert state["draft"] == "Draft answer."


def test_max_iterations_stops_loop():
    fake_llm = FakeLLM(["researcher", "researcher", "researcher", "researcher"])

    state = invoke_multi_agent_graph(
        llm_id="fake",
        query="Loop?",
        allow_search=False,
        system_prompt="",
        llm_factory=lambda _: fake_llm,
        max_iterations=2,
    )

    assert state["next"] == "FINISH"
    assert "supervisor:FINISH:max_iterations" in state["agent_trace"]


def test_critic_to_writer_revision_loop_is_capped():
    fake_llm = FakeLLM(
        ["researcher", "writer", "critic", "writer", "critic", "writer", "critic"],
        ["Add detail.", "Still unsupported.", "Needs more."],
    )

    state = invoke_multi_agent_graph(
        llm_id="fake",
        query="Needs review",
        allow_search=False,
        system_prompt="",
        llm_factory=lambda _: fake_llm,
        max_iterations=10,
        max_revisions=2,
    )

    assert state["revision_count"] == 2
    assert state["next"] == "FINISH"
    assert "supervisor:FINISH:revision_cap" in state["agent_trace"]


def test_single_mode_still_uses_existing_react_path(monkeypatch):
    monkeypatch.setattr(ai_agent, "_make_groq_llm", lambda _: FakeLLM([]))
    monkeypatch.setattr(ai_agent, "_make_tavily_tool", lambda: object())
    monkeypatch.setattr(ai_agent, "create_react_agent", lambda **_: FakeSingleAgent())

    response = ai_agent.get_response_from_ai_agents(
        "fake",
        "hello",
        False,
        "",
        mode="single",
    )

    assert response == "Single agent answer."
