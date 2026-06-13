# ./src/prompts.py

"""System prompt definitions for the agent.

This module contains prompt strings injected into the conversation
history to establish the agent's behavior, tool usage rules, and
response style.

Example:
    Using the system prompt in history initialization:
    ```
    from src.prompts import SYSTEM_PROMPT
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    ```
"""

SYSTEM_PROMPT: str = """You are a helpful assistant with access to tools.
Rules:
- Always use the available tools when they are relevant to the user's request
- Don't guess weather,time, or math results — always call the appropriate tool
- After receiving all tool results, respond with a JSON object in this exact
format:
{
    "answer": "<your final answer as a string>",
    "tools_used": ["<tool1>", "<tool2>"],
    "iterations": <number of iterations>
}
- Return ONLY the JSON object. No extra text, no markdown, no code blocks.
"""
'''System prompt injected at the start of every conversation.

Instructs the agent to use tools for weather, time, and math queries,
and to return a structured JSON object as its final response.
'''
