"""Run a few canonical power-analysis questions locally on the 9B model.

Power analysis is a study-planning task with no dataset, so each example is driven
through the phase-7 skill with `data_path=None` (the CLI equivalent is
`python -m localexpert.demo --phase 7 --no-data --prompt "..."`). Every run writes
an audit notebook to notebooks/power_*.ipynb — nothing leaves the laptop.

    python scripts/run_power.py                 # all examples
    python scripts/run_power.py --only ttest    # a single example
"""

from __future__ import annotations

import argparse
from pathlib import Path

from localexpert.agent import Agent
from localexpert.runtime import DEFAULT_MODEL, OllamaRuntime

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = REPO_ROOT / "notebooks"

POWER_PHASE = 7

# name -> (notebook, prompt)
EXAMPLES = {
    "ttest": (
        NOTEBOOKS / "power_ttest.ipynb",
        "A-priori power for a two-group randomized trial with a continuous outcome, "
        "analyzed by an independent-samples t-test. Assume Cohen's d = 0.5, "
        "alpha = 0.05 (two-sided), and target power = 0.80, with equal allocation. "
        "How many participants are needed per group, and in total?",
    ),
    "anova": (
        NOTEBOOKS / "power_anova.ipynb",
        "A-priori power for a one-way ANOVA comparing k = 4 groups on a continuous "
        "outcome. Assume Cohen's f = 0.25 (a medium effect), alpha = 0.05, and target "
        "power = 0.80. What total sample size is required, and how many per group?",
    ),
    "mdes": (
        NOTEBOOKS / "power_mdes.ipynb",
        "Sensitivity analysis: we can recruit only 30 participants per group for a "
        "two-group independent t-test at alpha = 0.05 (two-sided) and 80% power. "
        "What is the minimum detectable effect size (Cohen's d), and is that a "
        "realistic effect to expect?",
    ),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local power-analysis examples.")
    parser.add_argument("--only", choices=list(EXAMPLES), default=None,
                        help="Run just one example (default: all).")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Ollama model id (default: {DEFAULT_MODEL}).")
    parser.add_argument("--max-iterations", type=int, default=20,
                        help="Max tool-calling iterations per example (default: 20).")
    args = parser.parse_args(argv)

    names = [args.only] if args.only else list(EXAMPLES)
    runtime = OllamaRuntime(model=args.model, max_iterations=args.max_iterations)
    agent = Agent(runtime=runtime)

    for name in names:
        notebook_path, prompt = EXAMPLES[name]
        print("\n" + "#" * 70)
        print(f"# Power example '{name}' | phase {POWER_PHASE} | model {args.model} | no data")
        print("#" * 70)
        result = agent.run_phase(
            phase=POWER_PHASE,
            data_path=None,
            notebook_path=notebook_path,
            extra_instructions=prompt,
        )
        flag = " (stopped on iteration limit)" if result.stopped_on_limit else ""
        print(f"\n[{name}] {result.tool_calls} tool calls{flag} -> {notebook_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
