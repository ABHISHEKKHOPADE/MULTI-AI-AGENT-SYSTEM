# MULTI AI Agent System

A Streamlit + FastAPI application that can run in either single-agent mode or multi-agent mode.

- **Single agent:** the original LangGraph ReAct assistant with optional Tavily search.
- **Multi-agent:** a LangGraph `StateGraph` with a supervisor, researcher, writer, and critic working over shared state.

## Setup

Create and activate a virtual environment if needed, then install the project:

```powershell
pip install -e .
```

Set these environment variables in your shell or `.env` file:

```powershell
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

`TAVILY_API_KEY` is only required when web search is enabled.

## Run

```powershell
python app/main.py
```

This starts:

- FastAPI backend: `http://127.0.0.1:9999`
- Streamlit frontend: usually `http://localhost:8501`

In the Streamlit UI:

1. Enter an optional agent definition/system prompt.
2. Select a Groq model.
3. Enable or disable web search.
4. Choose **Single agent** or **Multi-agent**.
5. Enter a query and click **Ask Agent**.

## API

`POST /chat`

```json
{
  "model_name": "llama-3.1-8b-instant",
  "system_prompt": "You are a helpful assistant.",
  "message": "Explain LangGraph.",
  "allow_search": false,
  "mode": "multi"
}
```

`mode` is optional and defaults to `"single"`. Supported values are `"single"` and `"multi"`.

## Multi-Agent Architecture

Multi-agent mode uses:

- **Supervisor:** routes to `researcher`, `writer`, `critic`, or `FINISH`.
- **Researcher:** gathers notes; uses Tavily only when web search is enabled.
- **Writer:** drafts the final answer from the query, system prompt, and research notes.
- **Critic:** checks the draft for correctness, completeness, and unsupported claims.

Stop conditions:

- Invalid supervisor route falls back to `FINISH`.
- `max_iterations` defaults to `6`.
- Critic-to-writer revisions are capped at `2`.

## Test

```powershell
python -m compileall app
pytest
```

The tests use fake LLMs and do not require network access or API keys.

## Notes

- Multi-agent mode uses more LLM calls than single-agent mode, so it has higher latency and token usage.
- Web search requires `TAVILY_API_KEY` and the `langchain-tavily` dependency.
- Nothing is committed automatically; changes remain in the local working tree.
