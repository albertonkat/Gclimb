"""
Codex subagent — delegates code generation tasks to OpenAI's model.

Strengths: raw code synthesis, completions, refactoring, boilerplate generation.
Called by the Claude orchestrator when a task is primarily about writing new code.
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from typing import Optional

try:
    from openai import OpenAI
except ImportError as exc:
    raise ImportError("Run: pip install openai") from exc


CODEX_MODEL = os.getenv("CODEX_MODEL", "gpt-4o")

SYSTEM_PROMPT = textwrap.dedent("""
    You are a specialist code-generation agent.
    Your only job is to produce correct, minimal, well-named code.

    Rules:
    - Write only the requested code — no prose, no markdown fences unless asked.
    - Prefer clarity over cleverness.
    - Add a comment only when the WHY is non-obvious.
    - Never introduce features not explicitly requested.
    - If the task is ambiguous, make a safe conservative choice and note it briefly.
""").strip()


@dataclass
class CodexResult:
    code: str
    model: str
    tokens_used: int
    note: Optional[str] = None


@dataclass
class CodexAgent:
    api_key: str = field(default_factory=lambda: os.environ["OPENAI_API_KEY"])
    model: str = CODEX_MODEL
    temperature: float = 0.2
    max_tokens: int = 4096

    def __post_init__(self) -> None:
        self._client = OpenAI(api_key=self.api_key)

    def generate(self, task: str, context: str = "") -> CodexResult:
        """
        Ask Codex to write code for `task`.
        `context` is optional prior code or constraints the orchestrator passes down.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append({
                "role": "user",
                "content": f"Context / existing code:\n\n{context}",
            })
            messages.append({
                "role": "assistant",
                "content": "Understood. I have the context.",
            })

        messages.append({"role": "user", "content": task})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        choice = response.choices[0]
        return CodexResult(
            code=choice.message.content.strip(),
            model=response.model,
            tokens_used=response.usage.total_tokens,
        )

    def refactor(self, code: str, instructions: str) -> CodexResult:
        """Ask Codex to refactor existing code according to instructions."""
        task = f"Refactor the following code.\n\nInstructions: {instructions}\n\nCode:\n{code}"
        return self.generate(task)

    def explain(self, code: str) -> CodexResult:
        """Ask Codex to explain what a piece of code does."""
        task = (
            f"Explain what this code does in 3–5 concise bullet points:\n\n{code}"
        )
        return self.generate(task)
