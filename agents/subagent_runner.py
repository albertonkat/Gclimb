"""
subagent_runner.py — CLI entry point for the multi-model agent system.

Usage:
    python subagent_runner.py "Write a Python function to parse Z-Wave MQTT payloads"
    python subagent_runner.py --mode sdk "Research SmartThings Edge driver architecture"
    python subagent_runner.py --task-file task.txt --output result.md

Environment variables required:
    ANTHROPIC_API_KEY   — Claude orchestrator
    OPENAI_API_KEY      — Codex code-generation subagent
    GEMINI_API_KEY      — Gemini review/research subagent (if using SDK backend)
                          (not needed if using CLI backend with `gemini auth login`)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

# Allow running from agents/ directory directly
sys.path.insert(0, str(Path(__file__).parent))

from gemini_agent import GeminiBackend
from orchestrator import ClaudeOrchestrator, OrchestratorResult


def _print_section(title: str, content: str, width: int = 72) -> None:
    bar = "─" * width
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)
    print(textwrap.indent(content, "  "))


def _format_result(result: OrchestratorResult, verbose: bool = False) -> str:
    lines = []

    lines.append(f"Task type  : {result.task_type}")
    lines.append(f"Routing    : {' → '.join(result.routing)}")

    if result.codex_result and verbose:
        lines.append(
            f"Codex model: {result.codex_result.model} "
            f"({result.codex_result.tokens_used} tokens)"
        )

    if result.gemini_result and verbose:
        lines.append(
            f"Gemini     : backend={result.gemini_result.backend}, "
            f"verdict={result.gemini_result.verdict}"
        )
        if result.gemini_result.issues:
            lines.append(f"  Issues   : {len(result.gemini_result.issues)}")
            for issue in result.gemini_result.issues:
                sev = issue.get("severity", "info").upper()
                msg = issue.get("message", "")
                lines.append(f"    [{sev}] {msg}")

    lines.append("")
    lines.append(result.synthesis)
    return "\n".join(lines)


def _save_result(result: OrchestratorResult, path: str) -> None:
    content = _format_result(result, verbose=True)
    Path(path).write_text(content, encoding="utf-8")
    print(f"\nResult saved to: {path}")


def _check_env() -> list[str]:
    missing = []
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        if not os.environ.get(var):
            missing.append(var)
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-model AI coding agent: Claude + Codex + Gemini"
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task description (or use --task-file)",
    )
    parser.add_argument(
        "--task-file",
        metavar="FILE",
        help="Read task from a text file",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Save full result to this file",
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "sdk"],
        default="cli",
        help="Gemini backend: 'cli' (gemini binary) or 'sdk' (google-generativeai)",
    )
    parser.add_argument(
        "--claude-model",
        default=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        help="Claude model ID",
    )
    parser.add_argument(
        "--fix-loops",
        type=int,
        default=1,
        help="Max Codex→Gemini fix cycles (default: 1)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show subagent metadata in output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit result as JSON",
    )

    args = parser.parse_args()

    # Resolve task text
    if args.task_file:
        task = Path(args.task_file).read_text(encoding="utf-8").strip()
    elif args.task:
        task = args.task
    else:
        parser.error("Provide a task as a positional argument or via --task-file")

    # Check environment
    missing = _check_env()
    if missing:
        print(f"Warning: missing env vars: {', '.join(missing)}", file=sys.stderr)
        print("Some subagents will be skipped.", file=sys.stderr)

    # Build orchestrator
    orchestrator = ClaudeOrchestrator(
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        claude_model=args.claude_model,
        gemini_backend=GeminiBackend(args.mode),
        max_fix_loops=args.fix_loops,
    )

    print(f"Running task: {task[:80]}{'...' if len(task) > 80 else ''}")
    print("Orchestrating subagents...")

    result = orchestrator.run(task)

    if args.json_output:
        out = {
            "task_type": result.task_type,
            "routing": result.routing,
            "synthesis": result.synthesis,
            "codex": {
                "code": result.codex_result.code,
                "model": result.codex_result.model,
                "tokens_used": result.codex_result.tokens_used,
            } if result.codex_result else None,
            "gemini": {
                "text": result.gemini_result.text,
                "verdict": result.gemini_result.verdict,
                "issues": result.gemini_result.issues,
            } if result.gemini_result else None,
        }
        print(json.dumps(out, indent=2))
    else:
        _print_section("RESULT", _format_result(result, verbose=args.verbose))

    if args.output:
        _save_result(result, args.output)


if __name__ == "__main__":
    main()
