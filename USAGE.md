# localexpert — usage (skeleton milestone)

A local statistical-analysis assistant: a local Ollama model, extended with
markdown **skills** (one per pipeline phase), that writes and *runs* Python in a
live Jupyter kernel and records every step to an auditable notebook. Nothing
leaves the laptop.

See [DataAnalysisPipeline.md](DataAnalysisPipeline.md) for the four-phase pipeline
the skills are derived from.

> **Just want to chat with the model in VS Code?** That's the *interactive* path —
> see [SETUP.md](SETUP.md) (install) and [TUTORIAL.md](TUTORIAL.md) (first analysis).
> This page covers the *batch / reproducible* CLI path.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# A tool-calling model must be pulled in Ollama. The default is auto-selected by
# platform: qwen3.5:9b-mlx on Apple Silicon (faster/cleaner via Metal),
# qwen3.5:9b (GGUF) everywhere else (Windows/Linux x86, Intel Macs). Both ~7-9 GB,
# fit 16 GB. Pull the one for your machine:
ollama pull qwen3.5:9b-mlx    # Apple Silicon (M-series)
ollama pull qwen3.5:9b        # Windows/Linux x86, Intel Mac  (portable fallback)
# More headroom on 32 GB: `ollama pull qwen3.6:27b` and set LOCALEXPERT_MODEL.
```

If, on Apple Silicon, only the GGUF build is pulled, the runtime detects the
missing MLX tag and falls back to `qwen3.5:9b` automatically (with a printed
notice) — so either pull works. `LOCALEXPERT_MODEL=<id>` overrides the auto-pick.

## Run the demo

```bash
python scripts/make_sample_data.py            # -> data/sample_biobehavioral.csv
python -m localexpert.demo --phase 2          # EDA + missingness on the sample data
```

The agent loads the Phase-2 skill, executes analysis code step by step, prints a
findings summary, and writes an audit notebook to `notebooks/phase2.ipynb`. Open
that notebook to see every cell it ran and the outputs (including plots).

Flags: `--phase {1,2,3,4,5,6,7}`, `--task "<free-text intent>"` (heuristic skill
routing — alternative to `--phase`), `--model <ollama-id>`, `--data <csv>`,
`--no-data`, `--prompt "<directed instructions>"`, `--max-iterations <n>`,
`--notebook <path>`. Phases 1–4 are the pipeline stages; **5** is psychometrics
(reliability + factor analysis), **6** is survival analysis, and **7** is power
analysis. Override the model without a flag via `LOCALEXPERT_MODEL=<id>`.

## Power analysis (study planning)

Phase 7 sizes a study — or asks what a fixed sample can detect — for the standard
test families (t-tests, ANOVA, two proportions, correlation, χ², regression), using
`statsmodels.stats.power`. It supports a-priori sample size, sensitivity / minimum
detectable effect, post-hoc power, and power curves. A-priori planning has **no
dataset**, so pass `--no-data` and put the parameters in `--prompt`:

```bash
python -m localexpert.demo --phase 7 --no-data \
  --prompt "A-priori power: two-group independent t-test, Cohen's d=0.5, \
alpha=0.05, target power=0.80 — required n per group?"     # -> ~64 per group

python scripts/run_power.py        # a few worked examples -> notebooks/power_*.ipynb
```

## Reproduce the RetreatExercise locally (PHI-safe)

[RetreatExercise.md](RetreatExercise.md) is a faculty session that runs three
analyses through Colab's *cloud* Gemini agent — which is **not** BAA-covered, so
real patient data can't go through it. This project is the local replacement: the
same three analyses on a local 9B model, with nothing leaving the laptop.

```bash
# One-time prep (needs network to fetch the two R datasets; Rossi ships offline).
python scripts/make_btheb_data.py    # -> data/btheb_long.csv  (mixed model)
python scripts/make_bfi_data.py      # -> data/bfi.csv         (psychometrics)
python scripts/make_rossi_data.py    # -> data/rossi.csv       (survival)

ollama pull qwen3.5:9b               # tool-calling 9B, fits 16 GB
python scripts/run_retreat.py        # all three -> notebooks/retreat_*.ipynb
```

`run_retreat.py` feeds each segment its **directed** prompt (the design is named,
forcing the correct method). Add `--blind` to withhold it and see whether the model
recognizes the structure on its own — the side-by-side contrast the exercise is
built around. Run one segment with `--only {btheb,bfi,rossi}`.

Equivalent single call via the demo CLI (directed prompt passed with `--prompt`):

```bash
python -m localexpert.demo --phase 6 --data data/rossi.csv \
  --prompt "Treat this as time-to-event: KM curves by fin, log-rank, and a Cox model."
```

Open `notebooks/retreat_*.ipynb` and check the numbers against the answer keys in
`RetreatExercise.md` (e.g. Rossi Cox `fin` HR ≈ 0.68). **To run on real PHI data,**
point a segment's CSV at your own file with the same column names — the whole run
stays local.

## Layout

| Path | Role |
|------|------|
| `src/localexpert/skills/*/SKILL.md` | One skill per phase (frontmatter + procedure). Fine-tune-ready; shipped as package data. |
| `src/localexpert/references/*.md` | Shared cross-cutting conventions (single source), injected into the CLI prompt + exported to VS Code. |
| `src/localexpert/init_cmd.py` · `cli.py` | `localexpert init` — scaffold a VS Code workspace; `localexpert skills` — list the skill map. |
| `src/localexpert/skills.py` | Discover/parse skills. |
| `src/localexpert/kernel.py` | IPython kernel + nbformat audit trail. |
| `src/localexpert/tools.py` | The single `run_python` tool. |
| `src/localexpert/runtime.py` | Ollama tool-calling loop. |
| `src/localexpert/agent.py` | Assembles the skill prompt and drives one phase. |
| `src/localexpert/demo.py` | CLI entrypoint. |
| `scripts/make_sample_data.py` | Synthetic dataset with injected missingness/outliers. |
| `scripts/make_{btheb,bfi,rossi}_data.py` | Prep the three RetreatExercise datasets. |
| `scripts/run_retreat.py` | Reproduce the RetreatExercise's three analyses locally. |
| `scripts/run_power.py` | Worked power-analysis examples (phase 7, no dataset). |

## Tests

```bash
pytest        # skill loading + live-kernel execution/audit smoke tests
```

## Not yet built (follow-ups)

- Fine-tuning (export skills + transcripts as training pairs; LoRA via MLX/unsloth).
- Autonomous chaining of all four phases in sequence.
- The UMN finance assistant (second project in the README).
