# Gclimb — Multi-Model AI Coding Agent

Healthcare IoT Hub project using SmartThings, Z-Wave, and Zigbee.

## Agent System

```
agents/
├── orchestrator.py      # Claude master agent — plans, delegates, synthesizes
├── codex_agent.py       # OpenAI Codex — code generation & refactoring
├── gemini_agent.py      # Gemini CLI/SDK — research, review, validation
├── subagent_runner.py   # CLI entry point
└── __init__.py
```

### Run a task

```bash
# Install deps
pip install -r requirements.txt

# Authenticate Gemini CLI (one-time, for --mode cli)
gemini auth login

# Copy and fill in API keys
cp .env.example .env

# Run
source .env
python agents/subagent_runner.py "Write a Z-Wave MQTT payload parser in Python"

# Research-only (Gemini only, no code)
python agents/subagent_runner.py "What is the SmartThings Edge driver lifecycle?"

# Save output to file
python agents/subagent_runner.py "..." --output result.md

# Use Gemini SDK backend instead of CLI binary
python agents/subagent_runner.py "..." --mode sdk

# JSON output for piping
python agents/subagent_runner.py "..." --json
```

## Architecture Decision

**Option C (Hierarchical Subagent)** with **Option D (Specialist Routing)**:

- Claude classifies each task as CODE / RESEARCH / REVIEW / HYBRID
- Routes to the right subagents — avoids unnecessary API calls
- Gemini reviews all Codex output and can trigger a fix loop (up to `--fix-loops N`)
- Claude synthesizes the final answer

## Branch

Development: `claude/plan-ai-coding-agents-LSWZu`
