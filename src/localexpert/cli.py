"""Unified `localexpert` command with subcommands.

    localexpert init [folder]      # scaffold a VS Code + local-LLM workspace
    localexpert demo  --phase 2    # run one skill headlessly (batch/reproducible)

`localexpert-init` and `localexpert-demo` remain as direct console scripts too.
"""

from __future__ import annotations

import argparse
import sys

from . import demo as demo_mod
from . import init_cmd
from .skills import load_skills


def _list_skills(_args: argparse.Namespace) -> int:
    """Print the skill map (phase, name, description, when_to_use)."""
    for s in load_skills():
        print(f"[{s.phase}] {s.name}\n    {s.description}\n    when to use: {s.when_to_use}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="localexpert",
        description="Local LLM statistical-analysis assistant.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Scaffold a VS Code + local-LLM workspace.")
    init_cmd.add_arguments(p_init)
    p_init.set_defaults(_run=init_cmd.run)

    p_skills = sub.add_parser("skills", help="List the available skills and when to use each.")
    p_skills.set_defaults(_run=_list_skills)

    sub.add_parser(
        "demo",
        help="Run one skill headlessly on a dataset (see 'localexpert demo -h').",
        add_help=False,
    )

    # Parse only the top-level command so 'demo' can own its own flags.
    args, rest = parser.parse_known_args(argv)

    if args.command == "demo":
        return demo_mod.main(rest)
    return args._run(args)


if __name__ == "__main__":
    sys.exit(main())
