"""
Gemini subagent — uses Gemini CLI (subprocess) or google-generativeai SDK.

Strengths: web-grounded research, large-context document analysis, code review,
           multimodal understanding, validation against public documentation.
Called by the Claude orchestrator when a task needs research, review, or
fact-checking against external knowledge.
"""

from __future__ import annotations

import json
import os
import subprocess
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GeminiBackend(str, Enum):
    CLI = "cli"       # uses `gemini` CLI binary (google/gemini-cli npm package)
    SDK = "sdk"       # uses google-generativeai Python SDK


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

REVIEW_SYSTEM = textwrap.dedent("""
    You are a senior code-review agent. Your job:
    1. Identify bugs, security issues, and logic errors.
    2. Flag style violations and suggest minimal fixes.
    3. Confirm the code does what the task description says.
    4. Return structured JSON: {"issues": [...], "verdict": "pass"|"fail", "summary": "..."}
       Each issue: {"severity": "error"|"warning"|"info", "line": N or null, "message": "..."}
""").strip()


@dataclass
class GeminiResult:
    text: str
    backend: str
    model: str
    verdict: Optional[str] = None   # "pass" | "fail" — populated by review()
    issues: list = field(default_factory=list)


@dataclass
class GeminiAgent:
    api_key: str = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY", ""))
    model: str = GEMINI_MODEL
    backend: GeminiBackend = GeminiBackend.CLI
    temperature: float = 0.1

    def __post_init__(self) -> None:
        if self.backend == GeminiBackend.SDK:
            self._init_sdk()

    # ------------------------------------------------------------------
    # CLI backend
    # ------------------------------------------------------------------

    def _call_cli(self, prompt: str, system: str = "") -> str:
        """
        Invoke the `gemini` CLI binary.
        The google/gemini-cli tool reads GEMINI_API_KEY from the environment.
        Usage: gemini -p "<prompt>" [-m <model>]
        """
        env = os.environ.copy()
        if self.api_key:
            env["GEMINI_API_KEY"] = self.api_key

        cmd = ["gemini", "-p", prompt, "-m", self.model]
        if system:
            # gemini-cli supports --system-prompt flag
            cmd += ["--system-prompt", system]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"gemini CLI failed (exit {result.returncode}):\n{result.stderr}"
            )
        return result.stdout.strip()

    # ------------------------------------------------------------------
    # SDK backend
    # ------------------------------------------------------------------

    def _init_sdk(self) -> None:
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError("Run: pip install google-generativeai") from exc

        genai.configure(api_key=self.api_key)
        self._sdk = genai
        self._sdk_model = genai.GenerativeModel(
            model_name=self.model,
            generation_config={"temperature": self.temperature},
        )

    def _call_sdk(self, prompt: str, system: str = "") -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self._sdk_model.generate_content(full_prompt)
        return response.text.strip()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def _call(self, prompt: str, system: str = "") -> str:
        if self.backend == GeminiBackend.CLI:
            return self._call_cli(prompt, system)
        return self._call_sdk(prompt, system)

    def research(self, question: str) -> GeminiResult:
        """Use Gemini to research a technical question or fetch documentation context."""
        text = self._call(question)
        return GeminiResult(text=text, backend=self.backend.value, model=self.model)

    def review(self, code: str, task_description: str) -> GeminiResult:
        """
        Ask Gemini to review `code` against `task_description`.
        Returns structured verdict + issues list.
        """
        prompt = (
            f"Task description:\n{task_description}\n\n"
            f"Code to review:\n```\n{code}\n```\n\n"
            "Return ONLY valid JSON matching the schema in your instructions."
        )
        raw = self._call(prompt, system=REVIEW_SYSTEM)

        # Parse structured response; fall back gracefully
        verdict = None
        issues: list = []
        try:
            # Strip markdown fences if Gemini wraps JSON in them
            cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(cleaned)
            verdict = parsed.get("verdict")
            issues = parsed.get("issues", [])
            text = parsed.get("summary", raw)
        except (json.JSONDecodeError, AttributeError):
            text = raw

        return GeminiResult(
            text=text,
            backend=self.backend.value,
            model=self.model,
            verdict=verdict,
            issues=issues,
        )

    def summarize(self, document: str, focus: str = "") -> GeminiResult:
        """Summarize a long document, optionally focusing on a topic."""
        prompt = f"Summarize the following"
        if focus:
            prompt += f", focusing on: {focus}"
        prompt += f":\n\n{document}"
        text = self._call(prompt)
        return GeminiResult(text=text, backend=self.backend.value, model=self.model)
