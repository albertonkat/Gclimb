---
created: 2026-06-08
tags: [setup, import, hermes, claude, memory]
---

# Past Data Import

How to bring historical session data from Hermes and Claude.ai into the second brain so nothing is lost.

---

## Importing Hermes session history

Hermes stores session transcripts locally. Export them with:

```bash
# Export all sessions from the past year as markdown
hermes insights --days 365 --format markdown > ~/hermes-history-export.md

# Or export individual session summaries
hermes sessions list --limit 50
hermes sessions export --all --output ~/hermes-sessions/
```

Then place the export in the vault:
```bash
cp ~/hermes-history-export.md /path/to/Gclimb/second-brain/06-Sessions/hermes-history-import.md
```

After importing, run **Brain: Bulk-sync vault → brain** in Obsidian to index it for semantic search.

---

## Importing Claude.ai chat history

1. Go to **claude.ai → Settings → Data & Privacy → Export data**
2. Download the export archive (arrives by email within minutes)
3. Extract the archive — conversations are JSON files per chat
4. Convert to markdown (optional helper):

```bash
# Simple jq conversion (requires jq installed)
for f in ~/claude-export/conversations/*.json; do
  title=$(jq -r '.title' "$f")
  date=$(jq -r '.created_at' "$f" | cut -c1-10)
  slug=$(echo "$title" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-' | cut -c1-40)
  outfile="/path/to/Gclimb/second-brain/06-Sessions/${date}-claude-ai-${slug}.md"
  echo "---" > "$outfile"
  echo "created: $date" >> "$outfile"
  echo "agent: claude" >> "$outfile"
  echo "tags: [session, imported, claude-ai]" >> "$outfile"
  echo "---" >> "$outfile"
  echo "" >> "$outfile"
  echo "# $title" >> "$outfile"
  echo "" >> "$outfile"
  jq -r '.messages[] | "**\(.role):** \(.content)\n"' "$f" >> "$outfile"
done
```

5. After copying files, run **Brain: Bulk-sync vault → brain** in Obsidian.

---

## Importing from Claude Code sessions

Claude Code sessions are stored locally at:
```
~/.claude/projects/[project-hash]/[session-id].jsonl
```

The session for this Gclimb project is at:
```
~/.claude/projects/-home-user-Gclimb/
```

To extract readable summaries:
```bash
# List all session files for this project
ls ~/.claude/projects/-home-user-Gclimb/

# Convert a session JSONL to a readable log
cat ~/.claude/projects/-home-user-Gclimb/[session-id].jsonl \
  | jq -r 'select(.type=="message") | "\(.role): \(.content[0].text // "")"' \
  > ~/session-readable.md
```

Place summaries in `06-Sessions/` following the naming convention.

---

## After import: bulk sync

Once you've placed files in the vault:

1. **Obsidian**: Open vault → Command palette → **"Brain: Bulk-sync vault → brain"**
   This re-indexes all notes as semantic vectors.

2. **Verify semantic search works**:
   Ask Claude or Hermes: *"Search the brain for [topic you know is in the imported sessions]"*

3. **Tag imported files** — add `imported: true` to frontmatter so you can distinguish imported vs new session notes.

---

## Ongoing sync

Once past data is imported, the ongoing flow is automatic:
- Agents write new session summaries to `06-Sessions/` at end of every conversation
- Obsidian Git auto-pushes to GitHub every 5 minutes
- obsidian-brain re-indexes on vault changes (or on demand)

See [[03-Resources/brain-integration-setup]] for full setup instructions.
