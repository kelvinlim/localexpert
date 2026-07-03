"""Scaffold a novice-ready VS Code workspace: `localexpert init`.

Turns the single-source markdown skills (``src/localexpert/skills/``) into VS Code
Copilot artifacts and drops a ready-to-open workspace so a non-programmer can chat
with a local Ollama model that writes and runs the analysis in a Jupyter notebook.

Writes into the target folder (default: current directory):
- ``.github/copilot-instructions.md``     — shared persona/guardrails (auto-applied)
- ``.github/prompts/<phase>-<name>.prompt.md`` — one invocable `/skill` per phase
- ``.vscode/extensions.json`` / ``settings.json`` — recommended extensions + kernel
- ``notebooks/analysis_starter.ipynb``     — the first-session starter notebook
- ``data/sample_biobehavioral.csv``        — sample dataset (stress ↓ HRV signal)

Then (unless ``--no-pull``) pulls the Ollama model so the picker has it.

Everything is generated from code and is idempotent; re-running refreshes the files.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import nbformat

from .runtime import PORTABLE_MODEL
from .sample_data import make as make_sample_data
from .skills import Skill, load_skills

# --------------------------------------------------------------------------- #
# Static content (generated from code — no packaged template files needed).
# --------------------------------------------------------------------------- #

COPILOT_INSTRUCTIONS = """\
# localexpert — analysis assistant instructions

You help a researcher analyse data **in this Jupyter notebook**, running fully on a
local model so the data never leaves the laptop. Follow these rules for every chat:

- **Work incrementally.** Add and run **one cell at a time**; read its output before
  writing the next cell. Do not dump one giant cell.
- **Keep it transparent.** The notebook is the record — put the code, the output, and a
  short markdown interpretation for each step so it reads top to bottom.
- **Verify, don't assert.** State assumptions and check them (distributions, missingness,
  model diagnostics) before trusting a result; report effect sizes, not just p-values.
- **Stay local / no cloud.** Never suggest uploading the data to a web service. This
  workflow exists precisely so sensitive data stays on the machine.
- **Use the skill prompts.** For a standard task, the user may invoke a `/skill` (e.g.
  `/eda-missingness`); follow that skill's Procedure and satisfy its Checks.
- **Ask when the design is ambiguous** rather than guessing the statistical approach.

When unsure which analysis applies, do exploratory data analysis first and describe the
data's structure before choosing a test.
"""

EXTENSIONS_JSON = {
    "recommendations": [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "GitHub.copilot-chat",
        "ollama.ollama",
    ]
}

SETTINGS_JSON = {
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv",
    "notebook.output.textLineLimit": 30,
    # Legacy enable flag — harmless on current VS Code (prompt files are on by
    # default) but helps older versions pick up .github/prompts/.
    "chat.promptFiles": True,
}

STARTER_INTRO_MD = """\
# Analysis starter — chat with a local LLM

This notebook is your workspace. A **local** model does the analysis live in these
cells; nothing leaves your laptop.

**How to use it (4 steps):**

1. **Select the kernel** (top-right): pick the `.venv` interpreter for this folder.
2. **Open Copilot Chat** (the chat icon in the sidebar) and switch it to **Agent** mode.
3. **Pick the local model** in the chat model dropdown (e.g. `qwen3.5:9b`). If you don't
   see it, open *Manage Models* and add your Ollama models.
4. **Ask a question** in plain language — e.g.
   *"Does stress predict HRV in this data? Do proper EDA first."* — or invoke a skill
   with a slash command like `/eda-missingness`. Approve each step and watch the agent
   add and run cells below.

The cell beneath loads the bundled sample dataset so you have something to try.
See `TUTORIAL.md` for a full walkthrough.
"""

STARTER_LOAD_CODE = """\
import pandas as pd

df = pd.read_csv("data/sample_biobehavioral.csv")
print(df.shape)
df.head()
"""


# --------------------------------------------------------------------------- #
# Exporters
# --------------------------------------------------------------------------- #

def prompt_file_name(skill: Skill) -> str:
    """`.github/prompts/` filename for a skill, e.g. ``02-eda-missingness.prompt.md``."""
    return f"{skill.phase:02d}-{skill.name}.prompt.md"


def render_prompt_file(skill: Skill) -> str:
    """Render a VS Code prompt file (2026 frontmatter: `agent:`) from a skill."""
    front = (
        "---\n"
        f"description: {skill.description}\n"
        "agent: agent\n"
        "---\n"
    )
    intro = (
        f"You are performing a **{skill.name}** analysis (Phase {skill.phase}) in the "
        f"open Jupyter notebook. Work incrementally: add and run one cell at a time and "
        f"inspect each output before continuing. Load the dataset the user names (ask "
        f"which file if unclear). Follow the procedure below and satisfy every check, "
        f"then write a short markdown summary as the final cell.\n"
    )
    return f"{front}\n{intro}\n{skill.body.strip()}\n"


def write_github(target: Path) -> list[Path]:
    """Write .github/copilot-instructions.md and one prompt file per skill."""
    written: list[Path] = []
    gh = target / ".github"
    (gh / "prompts").mkdir(parents=True, exist_ok=True)

    instr = gh / "copilot-instructions.md"
    instr.write_text(COPILOT_INSTRUCTIONS, encoding="utf-8")
    written.append(instr)

    for skill in load_skills():
        p = gh / "prompts" / prompt_file_name(skill)
        p.write_text(render_prompt_file(skill), encoding="utf-8")
        written.append(p)
    return written


def write_vscode(target: Path) -> list[Path]:
    """Write .vscode/extensions.json and settings.json."""
    vs = target / ".vscode"
    vs.mkdir(parents=True, exist_ok=True)
    ext = vs / "extensions.json"
    ext.write_text(json.dumps(EXTENSIONS_JSON, indent=2) + "\n", encoding="utf-8")
    sets = vs / "settings.json"
    sets.write_text(json.dumps(SETTINGS_JSON, indent=2) + "\n", encoding="utf-8")
    return [ext, sets]


def write_starter_notebook(target: Path) -> Path:
    """Write notebooks/analysis_starter.ipynb."""
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell(STARTER_INTRO_MD),
        nbformat.v4.new_code_cell(STARTER_LOAD_CODE),
    ]
    nb.metadata["language_info"] = {"name": "python"}
    path = target / "notebooks" / "analysis_starter.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, str(path))
    return path


def pull_model(model: str) -> bool:
    """Best-effort `ollama pull`. Returns True on success, False (with a note) otherwise."""
    if shutil.which("ollama") is None:
        print(f"  ! Ollama not found on PATH — skipping model pull. Install it, then run: "
              f"ollama pull {model}")
        return False
    print(f"  · pulling Ollama model '{model}' (first time downloads several GB)…")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  ! 'ollama pull {model}' failed ({exc}); pull it manually later.")
        return False


# --------------------------------------------------------------------------- #
# Orchestration + CLI
# --------------------------------------------------------------------------- #

def build_workspace(target: Path, model: str = PORTABLE_MODEL,
                    pull: bool = True) -> None:
    """Scaffold the whole workspace under ``target``."""
    target = target.resolve()
    print(f"Scaffolding a localexpert workspace in {target}")

    written = write_github(target)
    written += write_vscode(target)
    written.append(write_starter_notebook(target))
    data_csv = make_sample_data(target / "data" / "sample_biobehavioral.csv")
    written.append(data_csv)

    for p in written:
        print(f"  + {p.relative_to(target)}")

    if pull:
        pull_model(model)

    print(
        "\nDone. Next:\n"
        f"  1. Open this folder in VS Code and accept the recommended extensions.\n"
        f"  2. Open notebooks/analysis_starter.ipynb and select the .venv kernel.\n"
        f"  3. In Copilot Chat: Agent mode + the local '{model}' model, then ask a question.\n"
        "  See SETUP.md and TUTORIAL.md for the full guide."
    )


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("target", nargs="?", default=".", type=Path,
                        help="Folder to scaffold (default: current directory).")
    parser.add_argument("--model", default=PORTABLE_MODEL,
                        help=f"Ollama model to pull / recommend (default: {PORTABLE_MODEL}).")
    parser.add_argument("--no-pull", action="store_true",
                        help="Do not run 'ollama pull' (just write the workspace files).")


def run(args: argparse.Namespace) -> int:
    build_workspace(Path(args.target), model=args.model, pull=not args.no_pull)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the `localexpert-init` console script."""
    parser = argparse.ArgumentParser(
        prog="localexpert-init",
        description="Scaffold a VS Code + local-LLM workspace for notebook analysis.",
    )
    add_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
