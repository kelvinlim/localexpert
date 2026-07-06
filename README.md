# localexpert

**A local LLM statistical-analysis assistant. Nothing leaves the laptop.**

There are often situations where help from an LLM is wanted but the data are
sensitive — protected health information, unpublished research — and sending them
to a cloud model is not appropriate. This project explores running a *local* model
on a laptop (an Apple Silicon MacBook Pro with 16 or 32 GB) and making it genuinely
useful for real statistical work despite its smaller size.

The bet: a small model doesn't need to *know* every method if it is handed a
**skill** — a short, structured markdown procedure — for the task at hand. `localexpert`
pairs a local tool-calling model (~7–9 GB) with a library of such skills, lets it
**write and run Python in a live Jupyter kernel**, and records every cell and output
to an auditable notebook. The result is transparent and reproducible by construction
— you can read top-to-bottom exactly how each number was produced.

The default model is auto-selected by platform: `qwen3.5:9b-mlx` on Apple Silicon
(faster and cleaner via Metal) and `qwen3.5:9b` (GGUF) everywhere else. If only the
GGUF build is present on Apple Silicon, the runtime detects the missing MLX tag and
falls back automatically. `LOCALEXPERT_MODEL=<id>` overrides the pick.

Design preferences: Python ≥ 3.12, standard packages, Jupyter notebooks for
transparency.

## Two ways to use it

The same **skills** drive two front-ends:

- **Interactive (VS Code) — for exploration, novice-friendly.** Chat with the local model
  in VS Code's Copilot Agent mode; it writes and runs the analysis in a Jupyter notebook
  right in front of you. One command scaffolds a ready workspace:

  ```bash
  uvx --from git+https://github.com/kelvinlim/localexpert localexpert init
  ```

  Full step-by-step install in **[SETUP.md](SETUP.md)**; a narrated first analysis in
  **[TUTORIAL.md](TUTORIAL.md)**.

- **Batch / reproducible (CLI) — for scripted runs.** The `localexpert` engine drives a
  skill end-to-end and writes an audit notebook (used for the RetreatExercise and power
  analyses). See the quickstart below and **[USAGE.md](USAGE.md)**.

## What works today

Project 1 — the **statistical analysis assistant** — is a working skeleton:

- **Seven skills** (`src/localexpert/skills/*/SKILL.md`), each a fine-tune-ready procedure:
  1–4 the analysis pipeline (define question → EDA/missingness → cleaning →
  statistical testing), **5** psychometrics (reliability + factor analysis),
  **6** survival analysis, **7** power analysis (study planning). Pick one by phase
  number, by `/name` in VS Code, or by free-text intent (`localexpert demo --task "…"`;
  `localexpert skills` lists the map).
- **Shared references** (`src/localexpert/references/*.md`) — cross-cutting conventions
  (stats reporting, local-only/PHI data handling, notebook practice) as one source,
  injected into the CLI system prompt and exported to VS Code as auto-applied
  `.github/instructions/`.
- A local **Ollama tool-calling loop** driving a single `run_python` tool against a
  persistent IPython kernel, with an **nbformat audit trail** per run.
- **Reproduces a real teaching exercise locally** — the three analyses in
  [RetreatExercise.md](RetreatExercise.md) (mixed model, psychometrics, survival)
  that were designed for Colab's cloud Gemini agent now run entirely on-device, as
  the PHI-safe replacement. Verified against the exercise's published answer keys.
- **Power analysis without a dataset** — a-priori sample size, sensitivity/MDES,
  post-hoc power, and power curves for the standard test families.

See **[USAGE.md](USAGE.md)** for setup, the demo, the RetreatExercise reproduction,
and power analysis. See [DataAnalysisPipeline.md](DataAnalysisPipeline.md) for the
four-phase pipeline the core skills are derived from.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ollama pull qwen3.5:9b-mlx      # Apple Silicon; use `qwen3.5:9b` on x86 / Intel Mac
python scripts/make_sample_data.py
python -m localexpert.demo --phase 2       # EDA on the sample data -> notebooks/phase2.ipynb
```

## Roadmap

- **Fine-tuning** — the rigid skill + transcript format is meant to be exported as
  instruction/response pairs to LoRA-tune an open-weights model on these tasks
  (an alternative to prompting with skills at inference time).
- **Autonomous chaining** of the pipeline phases end to end.
- **Project 2 — a UMN finance assistant** familiar with UMN analytics that can help
  locate and obtain the data a question needs. Not yet started.
