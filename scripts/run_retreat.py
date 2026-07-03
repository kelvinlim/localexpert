"""Reproduce the RetreatExercise's three analyses locally on the 9B model.

Runs all three RetreatExercise.md segments back-to-back through localexpert, each
with its *directed* prompt (the design is named, so the local model is forced onto
the correct method), writing one audit notebook per segment. Nothing leaves the
laptop — this is the PHI-safe replacement for the Colab/Gemini exercise.

    # one-time setup (needs network for prep + `ollama pull qwen3.5:9b`)
    python scripts/make_btheb_data.py
    python scripts/make_bfi_data.py
    python scripts/make_rossi_data.py

    python scripts/run_retreat.py                 # all three segments
    python scripts/run_retreat.py --only rossi    # a single segment
    python scripts/run_retreat.py --blind         # withhold the directed prompt

To swap in real (PHI) data, point a segment's CSV at your own file with the same
column names — the analysis runs entirely locally.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from localexpert.agent import Agent
from localexpert.runtime import DEFAULT_MODEL, OllamaRuntime

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data"
NOTEBOOKS = REPO_ROOT / "notebooks"

# Directed prompts lifted from RetreatExercise.md (one per segment).
BTHEB_PROMPT = (
    "This is the Beat the Blues dataset in long format: a randomized trial of "
    "computer-delivered CBT (treatment = BtheB) versus treatment as usual (TAU) "
    "for depression. Each patient's Beck Depression Inventory (bdi) is measured "
    "repeatedly across months (month = 2, 4, 6, 8), with baseline severity in "
    "bdi_pre. I want to know whether depression improves over time and whether the "
    "BtheB treatment helps, while accounting for the repeated measurements within "
    "each patient. Please: (1) explain which statistical approach is appropriate and "
    "why OLS would be inadequate; (2) fit a linear mixed-effects model with month, "
    "treatment, and bdi_pre as fixed effects and a random intercept for patient, "
    "using statsmodels; (3) report the fixed-effect estimates and the between-patient "
    "variance; (4) check assumptions with residual diagnostics; and (5) plot "
    "individual patient BDI trajectories with the group-average fits overlaid."
)

BFI_PROMPT = (
    "This is the bfi dataset: 25 personality items forming five 5-item scales — "
    "Agreeableness (A1-A5), Conscientiousness (C1-C5), Extraversion (E1-E5), "
    "Neuroticism (N1-N5), Openness (O1-O5). Some items are reverse-keyed. Please: "
    "(1) compute Cronbach's alpha for each scale; (2) identify and correctly recode "
    "any reverse-keyed items, then recompute alpha and explain what changed; (3) test "
    "factor adequacy with the KMO measure and Bartlett's test; and (4) run an "
    "exploratory factor analysis and report whether the items recover five "
    "interpretable factors."
)

ROSSI_PROMPT = (
    "This is the Rossi recidivism dataset: 432 released prisoners followed for one "
    "year. 'week' is time to re-arrest and 'arrest' indicates whether re-arrest "
    "occurred (1) or the person was censored (0). 'fin' indicates whether they "
    "received financial aid. Treat this as a time-to-relapse problem. Please: "
    "(1) explain why survival analysis is needed and what censoring means here; "
    "(2) plot Kaplan-Meier survival curves comparing the financial-aid groups; "
    "(3) run a log-rank test between those groups; and (4) fit a Cox "
    "proportional-hazards model with the available covariates and interpret the "
    "hazard ratios, noting which predictors are significant."
)

# name -> (phase, dataset csv, notebook, directed prompt)
SEGMENTS = {
    "btheb": (4, DATA / "btheb_long.csv", NOTEBOOKS / "retreat_btheb.ipynb", BTHEB_PROMPT),
    "bfi": (5, DATA / "bfi.csv", NOTEBOOKS / "retreat_bfi.ipynb", BFI_PROMPT),
    "rossi": (6, DATA / "rossi.csv", NOTEBOOKS / "retreat_rossi.ipynb", ROSSI_PROMPT),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reproduce the RetreatExercise locally.")
    parser.add_argument("--only", choices=list(SEGMENTS), default=None,
                        help="Run just one segment (default: all three).")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Ollama model id (default: {DEFAULT_MODEL}).")
    parser.add_argument("--max-iterations", type=int, default=30,
                        help="Max tool-calling iterations per segment (default: 30).")
    parser.add_argument("--blind", action="store_true",
                        help="Withhold the directed prompt to demonstrate the blind contrast.")
    args = parser.parse_args(argv)

    names = [args.only] if args.only else list(SEGMENTS)
    runtime = OllamaRuntime(model=args.model, max_iterations=args.max_iterations)
    agent = Agent(runtime=runtime)

    for name in names:
        phase, data_path, notebook_path, prompt = SEGMENTS[name]
        if not data_path.exists():
            parser.error(
                f"Dataset not found: {data_path}\n"
                f"Prepare it first with: python scripts/make_{name}_data.py"
            )
        print("\n" + "#" * 70)
        print(f"# Segment '{name}' | phase {phase} | model {args.model} | "
              f"{'BLIND' if args.blind else 'directed'} prompt")
        print("#" * 70)
        result = agent.run_phase(
            phase=phase,
            data_path=data_path,
            notebook_path=notebook_path,
            extra_instructions="" if args.blind else prompt,
        )
        flag = " (stopped on iteration limit)" if result.stopped_on_limit else ""
        print(f"\n[{name}] {result.tool_calls} tool calls{flag} -> {notebook_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
