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
│
├── src/
│   ├── agent.py              # Agent loop (DI: llm, registry, logger)
│   ├── schemas.py            # Pydantic response schema
│   ├── llm/
│   │   ├── base.py           # Abstract BaseLLMClient
│   │   ├── dto.py            # Data Transfer Objects
│   │   ├── groq_client.py    # Groq implementation
│   │   └── gemini_client.py  # Gemini implementation
│   ├── tools/
│   │   ├── base.py           # Abstract BaseTool
│   │   ├── schema.py         # ToolSchema, PropertySchema
│   │   ├── registry.py       # ToolRegistry
│   │   ├── weather.py        # WeatherTool (WeatherAPI)
│   │   ├── calculator.py     # CalculatorTool (safe AST eval)
│   │   └── time_tool.py      # TimeTool
│   └── logger/
│       ├── app_logger.py     # AppLogger (lazy composition)
│       └── subloggers/       # ColoredFormatter, Logger, AgentLogger, ToolLogger
└── main.py                   # Entry point
```

---

## Purpose

1. **Tool calling loop** — LLM drives tool selection; agent executes and returns results iteratively.
2. **Structured output** — Final response is validated against a Pydantic schema.
3. **Provider abstraction** — Swap Groq/Gemini without changing agent logic.
4. **Clean architecture** — KISS, DRY, OOP, Dependency Injection throughout.

---

## How It Works

1. **Initialization** — `Agent` loads LLM client, tool registry, and logger via DI.
2. **User prompt** — Added to conversation history as a `HistoryEntry`.
3. **LLM call** — `BaseLLMClient.generate()` sends history + tool schema to the LLM.
4. **Tool calls** — If LLM requests tools, `ToolRegistry.run()` executes them and appends results to history.
5. **Loop** — Steps 3–4 repeat until LLM returns a final text answer.
6. **Structured output** — Final answer is parsed into `AgentResponse` (answer, tools_used, iterations).

---

## Tools

- `get_weather(city)` — real weather data via [WeatherAPI](https://www.weatherapi.com)
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
GEMINI_API_KEY=your_gemini_key
WEATHER_API_KEY=your_weather_key
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
[22:18:23] [INFO] [AGENT] Prompt: What is the weather in London and Tokyo? Also, what is 25 * 48? And what is the current time?
[22:18:23] [INFO] ============================================================
[22:18:23] [INFO] [AGENT] Iteration 1
[22:18:24] [INFO] [TOOL] get_weather called with {'city': 'London'}
[22:18:24] [INFO] [TOOL] get_weather returned: London, United Kingdom: Patchy rain, 16.3°C, humidity 55%, wind 15.8 kph
[22:18:24] [INFO] [TOOL] get_weather called with {'city': 'Tokyo'}
[22:18:24] [INFO] [TOOL] get_weather returned: Tokyo, Japan: Light rain shower, 19.2°C, humidity 94%, wind 7.2 kph
[22:18:24] [INFO] [TOOL] calculator called with {'expr': '25 * 48'}
[22:18:24] [INFO] [TOOL] calculator returned: 25 * 48 = 1200
[22:18:24] [INFO] [TOOL] get_current_time called with {}
[22:18:24] [INFO] [TOOL] get_current_time returned: 2026-06-08 22:18:24
[22:18:24] [INFO] [AGENT] Iteration 2
[22:18:25] [INFO] ============================================================
[22:18:25] [INFO] [AGENT] Final answer: The weather in London is patchy rain...
[22:18:25] [INFO] ============================================================

{
  "answer": "The weather in London is patchy rain nearby...",
  "tools_used": ["get_weather", "get_weather", "calculator", "get_current_time"],
  "iterations": 2
}
```

---

## Dependencies

- Python 3.11+
- `groq` — Groq API client
- `google-genai` — Gemini API client
- `requests` — HTTP client for WeatherAPI
- `pydantic` — Response schema validation
- `python-dotenv` — Environment variable loading

---

## Project Status

**Status:** ✅ Completed

- Agent loop with sequential tool calls implemented
- Structured JSON output validated via Pydantic
- Multiple LLM providers supported via abstraction
- Colored structured logging with domain prefixes
- Clean OOP architecture with DI throughout

---

Made with ❤️ and Python by **Sam Malikin** 🎓
