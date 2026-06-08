---
created: 2026-06-08
tags: [setup, integration, ruflo, hermes, obsidian-brain]
---

# Brain Integration Setup

Connect ruflo (Claude Code) and Hermes to this Obsidian vault so both agents can read from and write memories to the second brain.

## Architecture

```
second-brain/ (this vault, tracked in Git)
        ↕ obsidian-brain plugin (install in Obsidian)
        ↕ RuVector Brain (local services at 127.0.0.1:9876 + :9877)
        ↕ MCP protocol (SSE)
    ┌───┴─────┐
    ↓         ↓
 Claude     Hermes
 (ruflo)  (Nous Research)

Write path: agents write .md files directly to second-brain/
Read path:  agents query via brain_search / brain_query MCP tools
Sync:       Obsidian Git plugin keeps vault ↔ GitHub in sync
```

## Step 1 — Install obsidian-brain in Obsidian

1. Open Obsidian → Settings → Community Plugins → Browse
2. Search for **RuVector Brain** and install it
3. Enable the plugin
4. Open Settings → RuVector Brain — note the MCP endpoint URL (copy it)
5. Run: **Brain: Bulk-sync vault → brain** from the command palette
   This indexes all your notes as semantic vectors. Re-run after adding new notes.

If the plugin is not yet in the community directory, install manually:
```bash
# In your Obsidian vault's .obsidian/plugins/ folder
git clone https://github.com/ruvnet/obsidian-brain ruvector-brain
cd ruvector-brain && npm install && npm run build
```
Then enable it in Obsidian → Community Plugins.

## Step 2 — Start the brain services (if not auto-started by Obsidian)

```bash
# Install dependencies once
npm install -g ruvector@0.2.25
npm install -g @ruvector/pi-brain

# Start the brain MCP server (keep this running)
npx ruvector@0.2.25 server -p 9876
```

The obsidian-brain plugin starts these automatically when Obsidian is open.
For headless / CI use, run the server manually.

## Step 3 — Connect ruflo (Claude Code)

Create `.claude/settings.json` at the root of this repo:

```json
{
  "mcpServers": {
    "ruvector-brain": {
      "type": "sse",
      "url": "http://127.0.0.1:9876/sse",
      "description": "RuVector Brain — semantic search over the Obsidian second-brain vault"
    }
  }
}
```

Or via the CLI (run once):
```bash
claude mcp add ruvector-brain --transport sse http://127.0.0.1:9876/sse
```

Verify it's working:
```bash
claude mcp list
# should show: ruvector-brain  sse  http://127.0.0.1:9876/sse
```

## Step 4 — Connect Hermes

```bash
# Interactive picker
hermes mcp

# Or add directly
hermes mcp add ruvector-brain --url http://127.0.0.1:9876/sse

# Verify
hermes mcp list
```

Or add manually to `~/.hermes/config.yaml`:
```yaml
mcp:
  servers:
    ruvector-brain:
      url: http://127.0.0.1:9876/sse
      type: sse
      description: "RuVector Brain — Gclimb second-brain vault"
```

## Step 5 — Sync vault ↔ GitHub (Obsidian Git)

Install the **Obsidian Git** community plugin so your vault stays in sync with this repo.
When an agent writes a memory file to `second-brain/00-Inbox/`, Obsidian Git will pick it up on the next auto-pull.

Recommended settings:
- Auto pull interval: 5 minutes
- Auto push on commit: enabled
- Commit message: `vault sync {{date}}`

## Verification

Once all steps are done, test the connection from Claude Code:

```
/mcp
# should list: ruvector-brain
```

Then ask:
> "Search the brain for Z-Wave protocol notes"

Claude should return results grounded in your `03-Resources/Z-Wave Protocol.md` note.

From Hermes:
```
hermes
> /mcp-status
> search my second brain for healthcare IoT device categories
```

## Memory write-back

See [[00-Inbox/agent-memory-protocol]] for naming conventions and frontmatter rules.

Both agents write to `second-brain/00-Inbox/` → you process weekly into the right PARA folder.
Agents can also write directly to `03-Resources/` or `02-Areas/` when the destination is clear.
