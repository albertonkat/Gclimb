"""
Claude orchestrator — the master agent that plans, delegates, and synthesizes.

Architecture (Option C — Hierarchical Subagent):

  User task
      │
      ▼
  Claude Orchestrator
  ├── classify task type
  ├── spawn CodexAgent   → generates code
  ├── spawn GeminiAgent  → reviews code / researches context
  └── synthesize final answer

Option D routing is also built in: if the task is pure research, only Gemini
is called; if the task is pure code with no ambiguity, only Codex is called.
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

try:
    import anthropic
except ImportError as exc:
    raise ImportError("Run: pip install anthropic") from exc

from codex_agent import CodexAgent, CodexResult
from gemini_agent import GeminiAgent, GeminiBackend, GeminiResult


CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

ORCHESTRATOR_SYSTEM = textwrap.dedent("""
    You are a master AI orchestrator. You coordinate two specialist subagents:
      - Codex: writes and refactors code
      - Gemini: researches, reviews, and validates

    Your job at each step:
    1. Classify the incoming task into one of: CODE | RESEARCH | REVIEW | HYBRID
    2. Decide which subagents to invoke and what instructions to give them.
    3. Receive their outputs and synthesize a final, coherent answer.

    When synthesizing:
    - Prefer Codex output for the final code artifact.
    - Incorporate Gemini's issues list into your synthesis.
    - If Gemini verdict is "fail", instruct Codex to fix and loop once.
    - Always explain your routing decision briefly in your final response.

    Respond in this JSON format:
    {
      "task_type": "CODE|RESEARCH|REVIEW|HYBRID",
      "routing": ["codex", "gemini"],   // which subagents to call
      "codex_prompt": "...",            // instruction for Codex (or null)
      "gemini_prompt": "...",           // instruction for Gemini (or null)
      "context_for_codex": "..."        // optional existing code / constraints
    }
""").strip()

SYNTHESIS_SYSTEM = textwrap.dedent("""
    You are synthesizing the outputs of two specialist AI subagents into a
    single, polished response for the user.

    Guidelines:
    - Lead with the final code artifact (if any), inside a fenced block.
    - Summarize what Codex did and what Gemini found.
    - If Gemini flagged issues, note whether they were fixed.
    - Keep the synthesis concise — the user wants the result, not a transcript.
""").strip()


class TaskType(str, Enum):
    CODE = "CODE"
    RESEARCH = "RESEARCH"
    REVIEW = "REVIEW"
    HYBRID = "HYBRID"


@dataclass
class OrchestratorResult:
    task_type: str
    codex_result: Optional[CodexResult]
    gemini_result: Optional[GeminiResult]
    synthesis: str
    routing: list[str]


@dataclass
class ClaudeOrchestrator:
    anthropic_api_key: str = field(
        default_factory=lambda: os.environ["ANTHROPIC_API_KEY"]
    )
    openai_api_key: str = field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")
    )
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "")
    )
    claude_model: str = CLAUDE_MODEL
    gemini_backend: GeminiBackend = GeminiBackend.CLI
    max_fix_loops: int = 1  # how many Codex→Gemini fix cycles to allow

    def __post_init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        self._codex = CodexAgent(api_key=self.openai_api_key) if self.openai_api_key else None
        self._gemini = GeminiAgent(
            api_key=self.gemini_api_key,
            backend=self.gemini_backend,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _claude(self, system: str, messages: list[dict]) -> str:
        response = self._client.messages.create(
            model=self.claude_model,
            max_tokens=2048,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()

    def _plan(self, user_task: str) -> dict:
        """Ask Claude to classify the task and build a routing plan."""
        import json

        raw = self._claude(
            system=ORCHESTRATOR_SYSTEM,
            messages=[{"role": "user", "content": user_task}],
        )

        # Strip markdown fences if present
        cleaned = (
            raw.strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )
        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback: treat as HYBRID if Claude's JSON is malformed
            return {
                "task_type": "HYBRID",
                "routing": ["codex", "gemini"],
                "codex_prompt": user_task,
                "gemini_prompt": f"Review this task and any code produced: {user_task}",
                "context_for_codex": "",
            }

    def _synthesize(
        self,
        user_task: str,
        plan: dict,
        codex_result: Optional[CodexResult],
        gemini_result: Optional[GeminiResult],
    ) -> str:
        parts = [f"Original task:\n{user_task}\n"]
        if codex_result:
            parts.append(f"Codex output (model={codex_result.model}):\n{codex_result.code}")
        if gemini_result:
            parts.append(
                f"Gemini output (backend={gemini_result.backend}, verdict={gemini_result.verdict}):\n"
                f"{gemini_result.text}"
            )
            if gemini_result.issues:
                issues_str = "\n".join(
                    f"  [{i['severity'].upper()}] {i.get('message','')}"
                    for i in gemini_result.issues
                )
                parts.append(f"Gemini issues:\n{issues_str}")

        combined = "\n\n---\n\n".join(parts)
        return self._claude(
            system=SYNTHESIS_SYSTEM,
            messages=[{"role": "user", "content": combined}],
        )

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, user_task: str) -> OrchestratorResult:
        """
        Execute the full multi-agent pipeline for `user_task`.
        Returns an OrchestratorResult with all intermediate and final outputs.
        """
        plan = self._plan(user_task)
        routing: list[str] = plan.get("routing", ["codex", "gemini"])
        task_type: str = plan.get("task_type", "HYBRID")

        codex_result: Optional[CodexResult] = None
        gemini_result: Optional[GeminiResult] = None

        # --- Step 1: Research (Gemini) if needed first ---
        if "gemini" in routing and plan.get("gemini_prompt"):
            gemini_mode = task_type in (TaskType.RESEARCH, TaskType.REVIEW)
            if gemini_mode or task_type == TaskType.HYBRID:
                gemini_result = self._gemini.research(plan["gemini_prompt"])

        # --- Step 2: Code generation (Codex) ---
        if "codex" in routing and plan.get("codex_prompt") and self._codex:
            ctx = plan.get("context_for_codex", "")
            if gemini_result:
                ctx = f"{ctx}\n\nResearch context from Gemini:\n{gemini_result.text}".strip()
            codex_result = self._codex.generate(plan["codex_prompt"], context=ctx)

        # --- Step 3: Code review (Gemini) if code was produced ---
        if codex_result and task_type in (TaskType.CODE, TaskType.HYBRID):
            gemini_result = self._gemini.review(
                code=codex_result.code,
                task_description=plan.get("codex_prompt", user_task),
            )

            # --- Step 4: Fix loop if Gemini says "fail" ---
            loops = 0
            while (
                gemini_result.verdict == "fail"
                and loops < self.max_fix_loops
                and self._codex
            ):
                issues_text = "\n".join(
                    f"- [{i['severity']}] {i.get('message','')}"
                    for i in gemini_result.issues
                )
                fix_prompt = (
                    f"Fix the following issues in the code:\n{issues_text}\n\n"
                    f"Original code:\n{codex_result.code}"
                )
                codex_result = self._codex.generate(fix_prompt)
                gemini_result = self._gemini.review(
                    code=codex_result.code,
                    task_description=plan.get("codex_prompt", user_task),
                )
                loops += 1

        # --- Step 5: Claude synthesizes everything ---
        synthesis = self._synthesize(user_task, plan, codex_result, gemini_result)

        return OrchestratorResult(
            task_type=task_type,
            codex_result=codex_result,
            gemini_result=gemini_result,
            synthesis=synthesis,
            routing=routing,
        )
