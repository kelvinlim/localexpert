"""End-to-end demo: drive one skill on the sample dataset with a local model.

Usage:
    python -m localexpert.demo --phase 2
    python -m localexpert.demo --phase 2 --data data/sample_biobehavioral.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .agent import Agent
from .runtime import DEFAULT_MODEL, OllamaRuntime
from .skills import select_by_intent

REPO_ROOT = Path(__file__).resolve().parents[2]


def _print_event(kind: str, text: str) -> None:
    label = {
        "assistant": "ASSISTANT",
        "tool_call": "TOOL CALL ",
        "tool_result": "TOOL OUT  ",
    }.get(kind, kind.upper())
    snippet = text if len(text) < 1500 else text[:1500] + " ...[truncated]"
    print(f"\n=== {label} ===\n{snippet}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local statistical analysis assistant demo.")
    parser.add_argument("--phase", type=int, default=2, choices=[1, 2, 3, 4, 5, 6, 7],
                        help="Skill to run: 1-4 pipeline phases, 5 psychometrics, "
                             "6 survival, 7 power analysis (default: 2, EDA).")
    parser.add_argument("--task", default=None,
                        help="Pick the skill by free-text intent instead of --phase "
                             "(heuristic keyword match on when_to_use/description, not an "
                             "LLM router). E.g. --task \"check scale reliability\".")
    parser.add_argument("--data", type=Path,
                        default=REPO_ROOT / "data" / "sample_biobehavioral.csv",
                        help="Path to the dataset CSV.")
    parser.add_argument("--no-data", action="store_true",
                        help="Run without a dataset — a-priori study planning "
                             "(e.g. power analysis). Parameters come from --prompt.")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Ollama model id (default: {DEFAULT_MODEL}).")
    parser.add_argument("--max-iterations", type=int, default=20,
                        help="Max tool-calling iterations before stopping.")
    parser.add_argument("--notebook", type=Path, default=None,
                        help="Where to write the audit notebook (default: notebooks/phase<N>.ipynb).")
    parser.add_argument("--prompt", "--instructions", dest="prompt", default="",
                        help="Extra task instructions appended to the skill prompt — "
                             "e.g. a directed prompt naming the design. Omit for the "
                             "skill-only (blind) behavior.")
    args = parser.parse_args(argv)

    phase = args.phase
    if args.task:
        skill = select_by_intent(args.task)
        phase = skill.phase
        print(f"Task {args.task!r} -> skill '{skill.name}' (phase {phase})")

    data_path = None if args.no_data else args.data
    if data_path is not None and not data_path.exists():
        parser.error(
            f"Dataset not found: {data_path}\n"
            "Generate it first with: python scripts/make_sample_data.py\n"
            "(or pass --no-data for an a-priori planning task like power analysis)"
        )

    notebook_path = args.notebook or (REPO_ROOT / "notebooks" / f"phase{phase}.ipynb")

    runtime = OllamaRuntime(model=args.model, max_iterations=args.max_iterations)
    agent = Agent(runtime=runtime)

    data_label = "(a priori / no data)" if data_path is None else data_path
    print(f"Model: {args.model} | Phase: {phase} | Data: {data_label}")
    result = agent.run_phase(
        phase=phase,
        data_path=data_path,
        notebook_path=notebook_path,
        extra_instructions=args.prompt,
        on_event=_print_event,
    )

    print("\n" + "=" * 60)
    print(f"Tool calls: {result.tool_calls} | Stopped on limit: {result.stopped_on_limit}")
    print(f"Audit notebook: {notebook_path}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
