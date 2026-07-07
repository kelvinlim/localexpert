# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **local, private** statistical-analysis assistant. A small local LLM (served by
Ollama) is extended with markdown **skills** + shared **references**, then driven to
write and *run* Python in a live Jupyter kernel, recording every step to an auditable
`.ipynb`. Sensitive/PHI data never leaves the laptop — the offline replacement for
cloud tools like Colab+Gemini (see `RetreatExercise.md`). Python ≥3.12; Apple Silicon
16–32 GB is the target machine.

The same skills/references drive **two front-ends**:
- **Batch/reproducible CLI** — `localexpert`'s own agentic loop (`agent.py` + `runtime.py`),
  used by `demo.py` and `scripts/run_*.py`. This is the engine the Architecture section traces.
- **Interactive VS Code** — `localexpert init` (`init_cmd.py`/`cli.py`) scaffolds a workspace
  that exports the skills/references to `.github/` so VS Code's Copilot agent (with a local
  Ollama model) writes+runs cells. See `SETUP.md` / `TUTORIAL.md` / `docs/vscode-local-llm-workflow-plan.md`.

## Commands

```bash
# Environment (all commands assume this venv; scripts import the installed package)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Model — auto-selected by platform; pull the one for your machine:
ollama pull qwen3.5:9b-mlx     # Apple Silicon
ollama pull qwen3.5:9b         # Windows/Linux x86, Intel Mac (portable fallback)

# Data + demo (batch CLI)
python scripts/make_sample_data.py                 # -> data/sample_biobehavioral.csv
python -m localexpert.demo --phase 2               # run one skill by phase number
python -m localexpert.demo --task "check scale reliability"      # pick skill by intent
python -m localexpert.demo --phase 7 --no-data --prompt "..."   # a-priori planning
localexpert skills                                 # list the skill map (phase/name/when_to_use)

# Interactive VS Code workspace (scaffold + export skills/references to .github/)
localexpert init [folder]                          # also builds .venv + pulls the model

# Reproduce the RetreatExercise (three analyses, one notebook each)
python scripts/make_btheb_data.py && python scripts/make_bfi_data.py && python scripts/make_rossi_data.py
python scripts/run_retreat.py                      # add --only rossi / --blind

# Tests
pytest                                             # full suite
pytest tests/test_kernel.py::test_error_is_captured_not_raised   # a single test
```

`pytest` requires no model (skill-loading + live-kernel smoke tests), but the demo
and `scripts/run_*.py` require a running Ollama with the model pulled.

## Architecture

The **batch CLI** is one agentic loop assembled from five core modules in
`src/localexpert/` (the interactive path reuses only the skills/references, not this loop
— it's exported to VS Code by `init_cmd.py`/`cli.py`, with `sample_data.py` providing the
demo dataset). Trace a CLI run to understand the engine:

1. **Entry** (`demo.py` or `scripts/run_*.py`) builds an `OllamaRuntime` and an
   `Agent`, then calls `Agent.run_phase(phase, data_path, notebook_path, extra_instructions)`.
2. **`agent.py`** selects the skill for that phase (`skills.select`), composes the
   system prompt (`BASE_PERSONA` + shared `references_prompt_block()` + `skill.prompt_block`)
   and the user prompt, opens a `KernelSession`, and hands control to the runtime with a
   one-entry tool dispatch table mapping `run_python` → the kernel. The audit notebook is
   saved in a `finally` block, so it persists even if the run errors or hits the limit.
3. **`runtime.py`** loops calling `ollama.chat` with a single tool (`RUN_PYTHON_TOOL`).
   Each `tool_calls` entry is dispatched to the kernel and the text result appended
   as a `role: tool` message; the loop ends when the model returns plain text (its
   findings summary) or `max_iterations` is hit.
4. **`kernel.py`** (`KernelSession`) runs code in a persistent `jupyter_client`
   IPython kernel — state persists across `run_python` calls. Every execution is
   also appended as a code cell + captured outputs to an in-memory `nbformat`
   notebook; that notebook is the transparency artifact.
5. **`tools.py`** defines the single `run_python` tool and its kernel-backed handler.

### Load-bearing design decisions

- **One tool, on purpose.** Small models handle a minimal tool surface far better,
  so the agent gets only `run_python`. Don't add tools casually.
- **Low temperature (0.2) is required, not cosmetic.** At Ollama's default (~0.8)
  the 9B model emits malformed Python and spirals into an error loop. `temperature`
  lives on `OllamaRuntime`.
- **Model auto-selection** (`runtime.default_model` / `is_apple_silicon`): picks
  `qwen3.5:9b-mlx` on Apple Silicon (Metal), `qwen3.5:9b` GGUF elsewhere, since MLX
  is Apple-only. `OllamaRuntime` falls back MLX→GGUF if the MLX tag isn't pulled.
  `LOCALEXPERT_MODEL` overrides everything; `LOCALEXPERT_OLLAMA_HOST` sets the host.
- **Two run modes.** `data_path` set → dataset-backed analysis; `data_path=None`
  (`--no-data`) → a-priori study planning with no data (e.g. power analysis, phase 7).

### Skills & references

Skills and references live **inside the package** (`src/localexpert/skills/`,
`src/localexpert/references/`) and are shipped as package data — `skills.py`/`references.py`
resolve them via `importlib.resources` (`SKILLS_DIR`/`REFERENCES_DIR`), so they work from an
editable checkout *and* an installed wheel. Both are declared in `pyproject.toml`
`[tool.setuptools.package-data]`.

**Skills** — each `skills/<dir>/SKILL.md`: YAML frontmatter (`name`, `description`, `phase`,
`when_to_use`) + a fixed **Objective / Procedure / Checks / Output** body. Selection three ways:
- `select(phase)` — the integer `phase` is the deterministic key; exactly one skill per phase.
- `select_by_intent(query)` — heuristic keyword router (inverse-skill-frequency weighted over
  when_to_use/description/name/body); exposed as `demo.py --task "..."`. Not an LLM router.
- VS Code `/name` — the exported prompt files (`.github/prompts/`) carry a "When to use this"
  line so Copilot can pick by intent.
Current phases: 1–4 the `DataAnalysisPipeline.md` stages; 5 psychometrics, 6 survival, 7 power.
The rigid body format is deliberate so skills can double as fine-tuning data.

**References** — each `references/<name>.md`: frontmatter (`description`) + a short body of
cross-cutting conventions (stats reporting, data handling/PHI, notebook practice). They are the
single source, injected into the CLI system prompt (`agent.py`) and exported to VS Code as
auto-applied `.github/instructions/*.instructions.md` (`init_cmd.py`).

**To add a skill:** create `src/localexpert/skills/NN-name/SKILL.md` with a new unique `phase`
and all four frontmatter fields. `tests/test_skills.py` asserts the exact set of discovered
phases; `tests/test_init.py`/`test_references.py` assert the export + intent routing — update
those when the skill/reference set changes. **To add a reference:** drop a
`src/localexpert/references/<name>.md` with a `description` frontmatter; both front-ends pick
it up automatically.
