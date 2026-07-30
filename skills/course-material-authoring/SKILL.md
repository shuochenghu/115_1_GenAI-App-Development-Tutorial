---
name: course-material-authoring
description: Create, revise, compare, and validate Traditional Chinese course materials for the「生成式 AI 應用開發」project, including Jupyter notebooks, Markdown handouts or slides, and Streamlit starter/demo projects. Use when preparing weekly teaching materials, maintaining student/teacher editions, integrating useful parts of alternate AI-generated versions, checking notebook quality, or synchronizing project memory after教材 changes.
---

# Course Material Authoring

Follow the project’s established teaching sequence, file conventions, student/teacher separation, validation rules, and memory-update workflow.

## Start with project context

1. Read `PROJECT_MEMORY.md` completely and treat it as the current source of truth.
2. Read `PROJECT_MEMORY_claude.md` only when comparing Claude-produced variants or tracing older decisions.
3. Inspect the target week, related preceding-week materials, and the course outline before editing.
4. Prefer the formal Codex track unless the user explicitly names another variant.
5. Read [references/conventions.md](references/conventions.md) before creating or substantially revising materials.

## Choose the deliverable

- For weekly notebooks, preserve separate student and teacher editions.
- For application weeks, use a teaching document plus a runnable local project when that matches the existing week.
- For slides or handouts, align terminology and examples with the formal notebook/project track.
- For comparison work, preserve alternate variants and selectively integrate strengths into the formal track.

Do not create new `_claude` or `Claude生成` names for formal outputs. Keep existing alternate files intact unless the user explicitly requests changes.

## Design for teaching

1. Confirm the week’s prerequisites, learning outcomes, three-hour flow, and next-week bridge.
2. Progress from a minimal working example to guided practice and then integrated exercises.
3. Explain non-obvious concepts before the code that uses them.
4. Add teaching-oriented comments for block purpose, API flow, state, errors, validation, cost, and secrets.
5. Avoid comments that merely restate obvious syntax.
6. Default paid API execution to off or clearly guarded.
7. Never write API keys, passwords, student data, or other secrets into materials.

For student editions, retain useful scaffolding and TODOs without exposing full answers. For teacher editions, provide complete reference implementations and expected observations.

## Edit safely

- Preserve unrelated user changes.
- Use UTF-8 and Traditional Chinese.
- Modify notebooks through structured JSON processing rather than textual search-and-replace.
- Preserve stable cell ordering and unique cell IDs.
- Keep notebook outputs cleared unless saved output is explicitly required.
- Keep formal Streamlit projects runnable from their own directories.
- Use current official API syntax only after checking authoritative documentation when the syntax or model availability may have changed.

## Validate before handoff

Run the applicable checks from [references/conventions.md](references/conventions.md):

- Parse notebook JSON.
- Compile every ordinary Python code cell after excluding notebook magics or non-Python file bodies.
- Check unique cell IDs and cleared outputs.
- Scan for mojibake, suspicious runs of `?`, secrets, and accidental answer leakage.
- Confirm student TODOs and teacher completeness.
- Compile `.py` files and perform proportionate local smoke tests.
- Do not claim paid API or deployment verification unless it actually ran.

After changing course materials, update `PROJECT_MEMORY.md` with the artifact, decisions, validation performed, and remaining live-test gaps. Do not put secrets in memory.

## Report the result

Lead with what was created or changed. Link the principal files, summarize validation, and explicitly distinguish static validation from real API, Streamlit, Colab, or deployment testing.
