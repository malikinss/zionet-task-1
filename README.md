# ZioNet-HW-1: LLM Agent with Tool Calling

## Task Definition

Implement an LLM agent loop with tool calling and structured output using an LLM provider SDK.

Specifically:

1. Define 2-3 simple tools (`get_weather`, `calculator`, `get_current_time`)
2. Create a response schema for structured output
3. Implement an agent loop that handles sequential tool calls
4. Parse the final response into the response schema

---

## Description

This project implements a **Python agent capable of routing user requests to external tools**, with support for multiple LLM providers via a unified interface.

Key components:

- **`Agent` class** — Core agent managing conversation history, tool dispatching, and structured response building. Supports dependency injection for LLM client, tool registry, and logger.
- **`BaseLLMClient`** — Abstract interface for LLM providers. Implementations: `GroqClient`, `GeminiClient`.
- **`ToolRegistry`** — Central store that registers `BaseTool` instances, dispatches tool calls by name, and serializes tools into LLM-compatible schema.
- **`BaseTool`** — Abstract base class for all tools. Implementations: `WeatherTool`, `CalculatorTool`, `TimeTool`.
- **`AppLogger`** — Colored structured logger with domain-specific subloggers (`AgentLogger`, `ToolLogger`).

Project structure:

```
./
├── src/
│   ├── agent.py              # Agent loop (DI: llm, registry, logger)
│   ├── schemas.py            # Pydantic response schema
│   ├── prompts.py            # System prompt
│   ├── llm/
│   │   ├── base.py           # Abstract BaseLLMClient
│   │   ├── dto.py            # Data Transfer Objects
│   │   ├── groq_client.py    # Groq implementation
│   │   └── gemini_client.py  # Gemini implementation
│   ├── tools/
│   │   ├── base.py           # Abstract BaseTool
│   │   ├── schema.py         # ToolSchema, PropertySchema
│   │   ├── registry.py       # ToolRegistry
│   │   ├── weather.py        # WeatherTool (WeatherAPI + mock fallback)
│   │   ├── calculator.py     # CalculatorTool (safe AST eval)
│   │   └── time_tool.py      # TimeTool
│   ├── logger/
│   │   ├── app_logger.py     # AppLogger (lazy composition)
│   │   └── subloggers/       # ColoredFormatter, Logger, AgentLogger, ToolLogger
│   └── langgraph/
│       ├── agent.py          # Graph definition and run()
│       ├── nodes.py          # call_llm, call_tools, should_continue
│       ├── state.py          # AgentState
│       └── tools.py          # LangChain @tool wrappers
└── main.py                   # Entry point (runs both Agent and LangGraph)
```

---

## Purpose

1. **Tool calling loop** — LLM drives tool selection; agent executes and returns results iteratively.
2. **Structured output** — Model returns JSON, parsed via `AgentResponse.model_validate_json()`.
3. **Provider abstraction** — Swap Groq/Gemini without changing agent logic.
4. **Clean architecture** — KISS, DRY, OOP, Dependency Injection throughout.

---

## How It Works

1. **Initialization** — `Agent` loads LLM client, tool registry, and logger via DI.
2. **User prompt** — Added to conversation history with a system prompt.
3. **LLM call** — `BaseLLMClient.generate()` sends history + tool schema to the LLM.
4. **Tool calls** — If LLM requests tools, `ToolRegistry.run()` executes them and appends results to history.
5. **Loop** — Steps 3–4 repeat until LLM returns a final JSON answer or `MAX_ITERATIONS` is reached.
6. **Structured output** — Final answer parsed into `AgentResponse` (answer, tools_used, iterations).

---

## Tools

- `get_weather(city)` — real weather via [WeatherAPI](https://www.weatherapi.com); falls back to mock if `WEATHER_API_KEY` is not set
- `calculator(expr)` — safe math via AST parser (no `eval`)
- `get_current_time()` — current datetime

---

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

Create `.env`:

```
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key        # optional
WEATHER_API_KEY=your_weather_key      # optional, falls back to mock
```

---

## Run

```bash
python main.py
```

## Switching LLM provider

```python
from src.agent import Agent
from src.llm.gemini_client import GeminiClient

agent = Agent(llm=GeminiClient())
```

---

## Output Example

```
[22:18:23] [INFO] ============================================================
[22:18:23] [INFO] [AGENT] Starting
[22:18:23] [INFO] [AGENT] Prompt: What is the weather in London and Tokyo?...
[22:18:23] [INFO] ============================================================
[22:18:23] [INFO] [AGENT] Iteration 1
[22:18:24] [INFO] [TOOL] get_weather called with {'city': 'London'}
[22:18:24] [INFO] [TOOL] get_weather returned: London, UK: Patchy rain, 16.3°C
[22:18:24] [INFO] [TOOL] calculator called with {'expr': '25 * 48'}
[22:18:24] [INFO] [TOOL] calculator returned: 25 * 48 = 1200
[22:18:24] [INFO] [AGENT] Iteration 2
[22:18:25] [INFO] [AGENT] Final answer: The weather in London is patchy rain...
============================================================

[Agent] Final JSON Response:
{
  "answer": "...",
  "tools_used": ["get_weather", "get_weather", "calculator", "get_current_time"],
  "iterations": 2
}

[LangGraph] Final JSON Response:
{
  "answer": "...",
  "tools_used": ["get_weather", "get_weather", "calculator", "get_current_time"],
  "iterations": 2
}
```

---

## Bonus — LangGraph Implementation

Re-implementation of the same agent using LangGraph (`src/langgraph/`).

**What LangGraph hid:** the tool-calling loop, conditional edge routing, and message state accumulation — three things `Agent` implements manually are reduced to `add_edge`, `add_conditional_edges`, and `Annotated[list, add_messages]`.

---

## Dependencies

- Python 3.11+
- `groq` — Groq API client
- `google-genai` — Gemini API client
- `langgraph` + `langchain-groq` — LangGraph agent (Bonus)
- `requests` — HTTP client for WeatherAPI
- `pydantic` — Response schema validation
- `python-dotenv` — Environment variable loading

---

## Project Status

**Status:** ✅ Completed

- Agent loop with sequential tool calls implemented
- Structured JSON output parsed via `model_validate_json`
- System prompt for reproducible behavior
- Bounded loop with `MAX_ITERATIONS` guard
- Multiple LLM providers supported via abstraction
- Weather tool with mock fallback (no API key required)
- LangGraph re-implementation (Bonus)
- Colored structured logging with domain prefixes
- Clean OOP architecture with DI throughout

---

Made with ❤️ and Python by **Sam Malikin** 🎓
