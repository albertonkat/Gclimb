# Skill Creator

Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.

## Overview

A Claude Code skill is a markdown file stored in `.claude/skills/<skill-name>.md`. When invoked via `/skill-name`, the file's instructions execute as a specialized prompt within the current session. Skills extend Claude Code with reusable, domain-specific behaviors.

## Skill File Format

```markdown
# Skill Name

One-sentence description used as the skill's trigger description.

## Overview
What this skill does and when to use it.

## Instructions
Step-by-step execution logic Claude follows when the skill runs.

## Examples
Concrete input/output examples showing expected behavior.
```

The description line (first paragraph after the title) is critical — it controls when the skill auto-triggers and appears in the skills list. It must be specific, action-oriented, and distinguish the skill from similar ones.

## Workflows

### Create a New Skill

1. **Clarify scope**: Ask the user what the skill should do, what inputs it accepts (if any), and what success looks like.
2. **Draft the skill file**:
   - Choose a short, hyphenated name: `<verb>-<noun>.md` (e.g., `review-migration.md`)
   - Write a precise description (1–2 sentences) that names the trigger conditions
   - Write `## Instructions` as numbered steps Claude will follow at runtime
   - Add `## Examples` showing at least one concrete use case
3. **Place the file** at `.claude/skills/<skill-name>.md`
4. **Register it** — if the project uses a skills index, add an entry; otherwise the file alone is sufficient.
5. **Run a smoke test**: invoke `/skill-name` with a representative input and verify the output matches expectations.

### Modify an Existing Skill

1. **Read the current file** to understand its intent and structure.
2. **Identify the gap**: Is the description causing wrong triggers? Are the instructions ambiguous? Is an example missing?
3. **Edit precisely** — change only what's needed. Do not refactor unrelated sections.
4. **Re-run the smoke test** after editing.

### Optimize a Skill's Description for Triggering Accuracy

The description controls both auto-triggering and discoverability. A poor description causes false positives (skill fires when it shouldn't) or false negatives (skill never fires when it should).

**Diagnostic checklist:**
- Does it name the concrete action the skill performs? ("Review the diff for bugs" vs. "Help with code")
- Does it name the input artifacts? ("given a migration file", "given a Figma URL")
- Does it exclude adjacent skills? If two skills have similar descriptions, add a distinguishing clause.
- Is it ≤ 2 sentences? Longer descriptions dilute signal.

**Optimization process:**
1. Collect 5–10 user prompts that should trigger the skill and 5–10 that should not.
2. For each false positive/negative, identify which word in the description caused the mismatch.
3. Rewrite the description to cover the true positives while excluding the negatives.
4. Re-test with the same prompt set.

### Run Evals

Evals verify a skill behaves correctly across a range of inputs.

1. **Define a test matrix**: list representative inputs (happy path, edge cases, boundary conditions).
2. **For each input**, invoke the skill and record: Did it complete? Was the output correct? Did it hallucinate or skip steps?
3. **Compute pass rate**: `passes / total`. A skill is considered stable at ≥ 90%.
4. **Document failures** with the exact input and expected vs. actual output. Use these to improve the skill's instructions.

### Benchmark Skill Performance with Variance Analysis

Variance analysis detects inconsistency — a skill that works 70% of the time is unreliable even if its average output looks good.

1. **Run the same input N ≥ 5 times** (use temperature > 0 or varied phrasing to expose variance).
2. **Score each run** on a 1–3 scale: 1 = wrong, 2 = partial, 3 = correct.
3. **Compute mean and standard deviation** of scores.
4. **Interpret**:
   - σ < 0.5: low variance, skill is consistent
   - 0.5 ≤ σ < 1.0: moderate variance, review ambiguous instruction steps
   - σ ≥ 1.0: high variance, the skill's instructions are underspecified — add constraints or examples
5. **Fix high-variance steps** by making instructions more deterministic: replace "consider doing X" with "always do X when Y".

## Skill Placement

| Location | Scope |
|---|---|
| `.claude/skills/<name>.md` | Project-level (checked into repo) |
| `~/.claude/skills/<name>.md` | User-level (available in all sessions) |

Project-level skills take precedence when names conflict.

## Anti-Patterns to Avoid

- **Vague descriptions**: "Help with things" — never triggers correctly.
- **Monolithic skills**: one skill doing five unrelated things — split into focused skills instead.
- **No examples**: skills without examples are harder to test and more likely to drift.
- **Overfitting to one input**: instructions written around a single concrete case break on variation.
- **Missing termination condition**: skills that loop or search indefinitely need explicit stop criteria.
