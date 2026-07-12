---
name: learn-vis-matplot
description: Progressive, hands-on guide for learning matplotlib to speed up data visualization and build custom aesthetic charts. Use when the user wants to practice, learn, or level up matplotlib skills in this repo.
---

# Learn Vis Matplot

Teach matplotlib progressively through this repo

## Startup

Before doing anything else (teaching or summarizing), read `.claude/learning-matplot-progress.md` if it exists. Use it to recall what's been covered, what's in progress, and what's next — don't restart concepts already covered, and don't ask the user to re-explain context that's already logged there. If the file doesn't exist yet, this is a fresh start.

## Approach

- Treat this as a teaching session, not a one-shot task: explain the "why" behind each API choice, not just the "what".
- dont edit the code, give me code so i can write on my own, i can ask you to write it for me if i need
- move step by step, dont overteach
- Prefer short runnable scripts/snippets over long explanations. Have the user run and see the plot before moving on.
- After each concept, suggest one small variation for the user to try themselves before advancing.

## Modes

Default mode is teaching (above). If the user's request matches the trigger below, switch modes instead.

### Summarize learning

Trigger: user asks to "summarize learning/progress", "save progress", or similar.

Do NOT teach anything in this mode — just capture state from the conversation so far.

1. Determine which script/topic is active (e.g. `learn-scripts/learn_waterfall_chart.py`).
2. Read `.claude/learning-matplot-progress.md` if it exists, to see prior progress (already done in Startup, above).
3. From the conversation, work out:
   - Concepts covered so far (with a one-line "why it matters" each, not just the term)
   - What's currently in progress / left mid-explanation
   - Concrete next step(s) to pick up with
4. Write (create or update) `.claude/learning-matplot-progress.md` using this structure. If multiple topics/scripts have been covered across sessions, keep one `## Topic: <name>` section per topic rather than overwriting other topics:

```markdown
# Learning Progress: Matplotlib

## Topic: <topic>

Last updated: <date>

### Covered
- <concept> — <why it matters, one line>

### In progress
- <what's mid-explanation or partially tried>

### Next
- <concrete next step(s)>
```

5. Keep it terse — this is a resumable checkpoint, not a transcript. Overwrite stale entries rather than appending duplicates.
6. Confirm to the user in 1-2 sentences what was saved and where.
