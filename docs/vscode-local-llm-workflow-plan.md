# Plan: Interactive VS Code + local-LLM + Jupyter workflow for novices

> Status: **approved; implementation in progress.** Companion planning copy:
> `~/.claude/plans/how-to-use-local-golden-finch.md`.

## Context

Today `localexpert` is a one-shot **CLI**: `python -m localexpert.demo --phase N` drives a
local model through a skill and writes an audit notebook. The desired working strategy is
different and interactive: a **novice researcher sits in VS Code and chats with a local
LLM that does the analysis live in a Jupyter notebook** — on Apple Silicon Mac and
Windows 11 x86, fully local (PHI never leaves the laptop), with an install a non-programmer
can complete.

Research (2025–2026) settled the approach:
- **VS Code's built-in Copilot Chat Agent mode** already creates, edits, and **runs**
  Jupyter cells, and via **"Manage Models" → Ollama** it uses a **local model with no
  GitHub account, fully offline** ([BYOK](https://code.visualstudio.com/blogs/2026/06/18/byok-vscode),
  [notebooks-with-ai](https://code.visualstudio.com/docs/agents/guides/notebooks-with-ai)).
  This is exactly the target experience — no custom chat UI needed.
- **Ollama** ships one-click GUI installers on both OSes (background service auto-starts);
  **`uv`** gives a one-command cross-platform env; shipping a **`.vscode/` workspace** makes
  extensions auto-suggest and pre-wires the kernel.

**Decisions (confirmed with user):** (1) adopt VS Code's native notebook agent and package
the **skills** as VS Code instruction/prompt files; (2) **keep the existing CLI engine** for
reproducible/batch runs (RetreatExercise, power) — skills stay single-source and feed both;
(3) deliver install as an **installable Python package with a `localexpert init` command**
(run via `uv`, from the Git repo — no PyPI publish needed) that scaffolds a shipped
**`.vscode/` workspace**.

The insight: the model's notebook *is* the audit trail, so VS Code's agent satisfies the
transparency goal natively. Our real IP — the **skills** — is authored once in
`skills/*/SKILL.md` and exported to VS Code artifacts.

## Alternatives considered (and rejected)
- **localexpert as a local MCP server** the VS Code agent calls — rejected: code would run in
  localexpert's own kernel, not the visible notebook, so outputs wouldn't land in the user's
  cells; more moving parts for a novice.
- **Custom chat UI on the engine** (in-notebook widget, streaming, multi-turn) — rejected:
  most to build/maintain and reinvents what VS Code's agent already does well.
- **OS-specific bootstrap scripts (`install.sh` + `install.ps1`)** — reconsidered and dropped
  in favor of a packaged, cross-platform **`localexpert init`** console command: one Python
  command behaves identically on Mac and Windows, so there's no second script to maintain and
  no untestable-on-Mac Windows `.ps1`. (The package also delivers the pinned scientific stack
  the notebook kernel needs, in one install.)

## Changes

### 1. Skills → VS Code artifacts (single-source exporter)
Exporter logic that reuses the existing loader `localexpert.skills.load_skills()`
(`src/localexpert/skills.py:83`) and writes, from each `SKILL.md`:
- **`.github/copilot-instructions.md`** — the shared persona/guardrails (adapted from
  `agent.py`'s `BASE_PERSONA`, `src/localexpert/agent.py:13`): work incrementally, run one
  cell at a time and inspect output, verify results, keep everything local / no cloud, prefer
  the notebook as the record. Auto-applies to all Copilot chats in the workspace.
- **`.github/prompts/<phase>-<name>.prompt.md`** — one invocable prompt per skill (used as
  `/<name>` in Copilot Chat), with **verified 2026 frontmatter**: `agent: agent` (the field is
  `agent:` now, values `ask|agent|plan`; the old `mode:` key is legacy-compatible only),
  `description:` from the skill. Body carries the skill's **Objective / Procedure / Checks /
  Output**, reworded from "write and run Python via a tool" to "add and run cells in this notebook."
  Directory `.github/prompts/` and the `/name` invocation are confirmed current
  ([prompt-files docs](https://code.visualstudio.com/docs/agent-customization/prompt-files)).

The exporter lives in the package (callable from `localexpert init`) and is idempotent; the
generated files are also committed so a fresh clone works without running it. Add a test that
every phase produces a prompt file with valid frontmatter.

### 2. Shipped `.vscode/` workspace
- **`.vscode/extensions.json`** → recommend these exact IDs (verified): `ms-python.python`
  (auto-adds Pylance + Jupyter as optional deps — also list `ms-toolsai.jupyter` explicitly to
  be safe), `GitHub.copilot-chat`, and **`ollama.ollama`** — the official Ollama extension that
  surfaces local models in Copilot's picker (the old built-in Ollama provider is deprecated).
  First open shows the "install recommended extensions" banner.
- **`.vscode/settings.json`** → pre-wire `python.defaultInterpreterPath` to the `.venv`
  (portable `${workspaceFolder}/.venv` form VS Code resolves per-OS) and sensible notebook
  defaults. **Note:** prompt files and `.github/copilot-instructions.md` are **on by default** in
  current VS Code — no enabling setting needed (`chat.promptFiles` /
  `github.copilot.chat.codeGeneration.useInstructionFiles` are legacy; include only if targeting
  older VS Code). No `mcp.json` (not needed for this strategy).

### 3. Novice install: packaged tool + `localexpert init`
- **Ship as an installable package**, so `uv` installs the tool *and* its full pinned
  scientific stack (pandas/statsmodels/lifelines/factor_analyzer/scikit-learn) in one command —
  **from the Git repo, no PyPI publish required initially**:
  `uv tool install git+https://github.com/kelvinlim/localexpert` or, zero-install,
  `uvx --from git+https://github.com/kelvinlim/localexpert localexpert init`.
  (Publish to PyPI later only if bare `uvx localexpert` is wanted.)
- **New `localexpert init` console entry point** (`src/localexpert/init_cmd.py`, registered in
  `[project.scripts]`) that scaffolds a ready workspace in the target folder: runs the exporter
  (§1) to write `.github/`, drops `.vscode/` (§2), pulls the Ollama model, and writes the starter
  notebook + sample data. Idempotent and cross-platform — this **replaces** `install.sh`/`install.ps1`.
- **Packaging delta (the real work — confirmed structural gap):** today `skills/` sits at the
  **repo root**, a sibling of `src/`, while `pyproject.toml` builds only `where=["src"]` — so a
  wheel would **not** include the skills, and `importlib.resources` can only read data *inside*
  the package. Therefore:
  - **Move `skills/` → `src/localexpert/skills/`** and change `SKILLS_DIR`
    (`src/localexpert/skills.py:27`) to resolve via `importlib.resources.files("localexpert") / "skills"`.
    `load_skills()`/`select()` callers using the default dir are unaffected; keep `pip install -e`
    working for devs.
  - **Make sample-data generation importable:** move `scripts/make_sample_data.py` logic into the
    package (`localexpert.sample_data:make`) so `init` can call it; keep a thin script wrapper.
  - **Generate `.vscode/` and `.github/` from code** (inline constants + the exporter), not
    packaged template files.
  - Generate `uv.lock` via `uv sync`.
- **Only OS-specific steps left, both one-time and documented:** install Ollama (GUI installer)
  and install `uv` (one-liner). Everything after is the single `localexpert init` command.
- **`notebooks/analysis_starter.ipynb`** — a first markdown cell with the 4-step novice flow
  (open Copilot Chat → Agent mode → pick the local model → type `/eda` or describe the task),
  then a data-loading cell pointed at `data/sample_biobehavioral.csv`.

### 4. Model guidance
Recommend the **tool-calling-capable** `qwen3.5:9b` (portable GGUF tag) for the VS Code path
so agent mode works on both platforms; note `qwen3.5:9b-mlx` as the faster Mac option and
`qwen2.5-coder` as an alternative. (Agent mode hides models lacking tool support.) The existing
CLI keeps its platform auto-select in `runtime.py` unchanged.

### 5. Docs
Two separate novice documents — **install** vs **worked example** — kept distinct on purpose:
- New **`SETUP.md`** (get it running) — the step-by-step install for Mac and Windows: install
  Ollama (GUI), install `uv`, run `uvx --from git+… localexpert init`, open the folder in VS Code,
  accept recommended extensions, select the local model in "Manage Models", switch Copilot Chat to
  Agent mode. Include the **PHI checklist** and the honest wrong-cell-edit caveat.
- New **`TUTORIAL.md`** (a first real session, for a non-programmer) — a **narrated, click-by-click
  worked example** on the shipped `data/sample_biobehavioral.csv`: open the starter notebook →
  confirm Agent mode + local model → ask "Does stress predict HRV? Do proper EDA first" (or `/eda`)
  → what to expect as the agent adds/runs cells → how to read each step and when to redirect →
  interpret and save the notebook as the audit record. Each step names the exact button/menu, the
  expected on-screen result, and an "if it goes wrong" note. Numbers cross-checked against the
  sample data's known signal (stress ↓ HRV).
- Update **README.md / USAGE.md**: document the **two paths** — *Interactive* (VS Code agent) and
  *Batch/reproducible* (the `localexpert` CLI) — and link `SETUP.md` + `TUTORIAL.md`.

## Verification

1. **Exporter:** run it (or `localexpert init` in a temp dir); confirm `.github/copilot-instructions.md`
   plus one `.github/prompts/*.prompt.md` per phase (1–7), each with valid frontmatter. `pytest`
   (new test) asserts the mapping.
2. **Packaged install (Mac):** from a clean checkout, `uv tool install .` (and `uvx --from . localexpert init`)
   → package installs with the full stack, `python -c "import localexpert"` works, skills load via
   `importlib.resources` (test the wheel-vs-editable trap), `localexpert init` scaffolds `.vscode/` +
   `.github/` + starter notebook and pulls the model. Validate generated JSON. `pytest` green.
3. **Windows:** the same single `localexpert init` command runs there — still do one manual smoke
   test on a Win11 box.
4. **Interactive smoke test (documented manual):** open the folder in VS Code, accept extensions,
   pick the local `qwen3.5:9b` model, Agent mode, run `/eda` on the sample CSV, confirm the agent
   adds/executes cells. Record in `SETUP.md`.

## Files
- Add: `src/localexpert/init_cmd.py`, `src/localexpert/sample_data.py`,
  `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md` (generated),
  `.vscode/extensions.json`, `.vscode/settings.json`, `uv.lock`,
  `notebooks/analysis_starter.ipynb`, `SETUP.md`, `TUTORIAL.md`, a test in `tests/`.
- Move: `skills/` → `src/localexpert/skills/`.
- Modify: `pyproject.toml` (package data for `localexpert/skills/**`; `[project.scripts]`
  `localexpert-init`; `[tool.uv]`), `src/localexpert/skills.py` (`SKILLS_DIR` via
  `importlib.resources`), `scripts/make_sample_data.py` (thin wrapper), `scripts/run_*.py` +
  `tests/` if they reference the old skills path, `README.md`, `USAGE.md`.
- Not doing: `install.sh` / `install.ps1`.
- Unchanged: the `src/localexpert/` engine loop (runtime/agent/kernel/tools) and CLI/batch behavior.

## Build readiness

**Verdict: ready.** VS Code formats verified; the one structural unknown (skills inside the
package) is a concrete refactor. Accepted empirical risk: whether `qwen3.5:9b` drives VS Code's
notebook agent reliably — resolved only by the manual smoke test; fallback is `qwen2.5-coder` or a
larger model. Build order: (1) packaging refactor → pytest green; (2) exporter + `localexpert init`;
(3) `.vscode`/`.github`/starter notebook; (4) `uv.lock` + docs; (5) smoke tests.

## Key references
- VS Code BYOK / local models: https://code.visualstudio.com/blogs/2026/06/18/byok-vscode
- VS Code notebook agent: https://code.visualstudio.com/docs/agents/guides/notebooks-with-ai
- VS Code prompt files: https://code.visualstudio.com/docs/agent-customization/prompt-files
- uv install / tools: https://docs.astral.sh/uv/getting-started/installation/ · https://docs.astral.sh/uv/guides/tools/
- Ollama macOS / Windows: https://docs.ollama.com/macos · https://docs.ollama.com/windows
