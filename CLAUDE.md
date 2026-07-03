# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **local, private** statistical-analysis assistant. A small local LLM (served by
Ollama) is extended with markdown **skills**, then driven through an agentic loop
where it writes and *runs* Python in a live Jupyter kernel, recording every step
to an auditable `.ipynb`. The point is that sensitive/PHI data never leaves the
laptop — this is the offline replacement for cloud tools like Colab+Gemini (see
`RetreatExercise.md`). Python ≥3.12; Apple Silicon 16–32 GB is the target machine.

## Commands

```bash
# Environment (all commands assume this venv; scripts import the installed package)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Model — auto-selected by platform; pull the one for your machine:
ollama pull qwen3.5:9b-mlx     # Apple Silicon
ollama pull qwen3.5:9b         # Windows/Linux x86, Intel Mac (portable fallback)

# Data + demo
python scripts/make_sample_data.py                 # -> data/sample_biobehavioral.csv
python -m localexpert.demo --phase 2               # run one skill on a dataset
python -m localexpert.demo --phase 7 --no-data --prompt "..."   # a-priori planning

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

The whole system is one agentic loop assembled from five modules in
`src/localexpert/`. Trace a run to understand it:

1. **Entry** (`demo.py` or `scripts/run_*.py`) builds an `OllamaRuntime` and an
   `Agent`, then calls `Agent.run_phase(phase, data_path, notebook_path, extra_instructions)`.
2. **`agent.py`** selects the skill for that phase (`skills.select`), composes the
   system prompt (`BASE_PERSONA` + `skill.prompt_block`) and the user prompt, opens
   a `KernelSession`, and hands control to the runtime with a one-entry tool
   dispatch table mapping `run_python` → the kernel. The audit notebook is saved in
   a `finally` block, so it persists even if the run errors or hits the limit.
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

### Skills

Each skill is `skills/<dir>/SKILL.md`: YAML frontmatter (`name`, `description`,
`phase`, `when_to_use`) + a body with a fixed **Objective / Procedure / Checks /
Output** structure (parsed in `skills.py`). The integer **`phase` is the selection
key** — `select(phase)` requires exactly one skill per phase. Current phases: 1–4
are the `DataAnalysisPipeline.md` stages (define question, EDA/missingness,
cleaning, testing); 5 psychometrics, 6 survival, 7 power. The rigid body format is
deliberate so skills can later double as fine-tuning data.

**To add a skill:** create `skills/NN-name/SKILL.md` with a new unique `phase`
number and all four frontmatter fields. `tests/test_skills.py` asserts the exact
set of discovered phases and that every skill has non-empty frontmatter/body —
update those assertions when the phase set changes.
