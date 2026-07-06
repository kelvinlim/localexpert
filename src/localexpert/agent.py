"""Orchestrator: assemble a skill-driven prompt and run the agentic loop."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .kernel import KernelSession
from .references import references_prompt_block
from .runtime import OllamaRuntime, RunResult
from .skills import Skill, select
from .tools import run_python

BASE_PERSONA = """You are a careful statistical analysis assistant running fully \
on a local machine, so the data never leaves the laptop. You follow a documented \
skill for the current phase of a data-analysis pipeline.

You have one tool, run_python, that executes Python in a persistent Jupyter kernel \
(pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib, seaborn are available). \
State persists between calls.

Work incrementally: run small pieces of code, inspect the output, and decide the next \
step from what you observe — do not write one giant block. Follow the skill's Procedure \
in order and satisfy its Checks. When finished, write a concise markdown findings \
summary as your final message (no tool call). Do not go beyond the current phase."""


@dataclass
class Agent:
    """Runs a single pipeline phase against a dataset."""

    runtime: OllamaRuntime
    skills_dir: Path | None = None

    def _system_prompt(self, skill: Skill) -> str:
        refs = references_prompt_block()
        parts = [BASE_PERSONA]
        if refs:
            parts.append(refs)
        parts.append(skill.prompt_block)
        return "\n\n".join(parts)

    def _user_prompt(self, skill: Skill, data_path: Path | None, extra: str = "") -> str:
        if data_path is None:
            msg = (
                f"This is a study-planning task with no dataset. Carry out the "
                f"'{skill.name}' skill (Phase {skill.phase}) using the parameters "
                f"provided below."
            )
        else:
            msg = (
                f"Dataset for this analysis: {data_path}\n"
                f"Load it and carry out the '{skill.name}' skill (Phase {skill.phase})."
            )
        return f"{msg}\n\n{extra}".strip()

    def run_phase(
        self,
        phase: int,
        data_path: Path | None,
        notebook_path: Path,
        extra_instructions: str = "",
        on_event=None,
    ) -> RunResult:
        """Drive one phase; save the audit notebook regardless of outcome."""
        skill = (
            select(phase, self.skills_dir) if self.skills_dir else select(phase)
        )
        messages = [
            {"role": "system", "content": self._system_prompt(skill)},
            {"role": "user", "content": self._user_prompt(skill, data_path, extra_instructions)},
        ]

        with KernelSession() as session:
            dispatch = {"run_python": lambda code: run_python(session, code)}
            try:
                result = self.runtime.run(messages, dispatch, on_event=on_event)
            finally:
                session.save(notebook_path)
        return result
