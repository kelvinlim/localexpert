"""Discover and load markdown skill files.

Each skill lives in ``skills/<dir>/SKILL.md`` and is composed of a YAML
frontmatter block delimited by ``---`` lines followed by a markdown body:

    ---
    name: eda-missingness
    description: Exploratory data analysis and missingness diagnostics.
    phase: 2
    when_to_use: Right after loading raw data, before any cleaning.
    ---
    ## Objective
    ...

The rigid frontmatter + structured body is what lets a skill later be
exported as an instruction/response pair for fine-tuning.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

# Repo-root/skills — this file is src/localexpert/skills.py, so go up three.
SKILLS_DIR = Path(__file__).resolve().parents[2] / "skills"

REQUIRED_FIELDS = ("name", "description", "phase", "when_to_use")


@dataclass(frozen=True)
class Skill:
    """A parsed skill: metadata from frontmatter plus the markdown body."""

    name: str
    description: str
    phase: int
    when_to_use: str
    body: str
    path: Path

    @property
    def prompt_block(self) -> str:
        """The text injected into the model's system prompt."""
        return (
            f"# Skill: {self.name} (Phase {self.phase})\n"
            f"{self.description}\n\n"
            f"{self.body.strip()}\n"
        )


def _split_frontmatter(text: str, path: Path) -> tuple[dict, str]:
    """Split ``---`` YAML frontmatter from the markdown body."""
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing '---' frontmatter block")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: malformed frontmatter (need opening and closing '---')")
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: frontmatter must be a YAML mapping")
    return meta, parts[2]


def load_skill(path: Path) -> Skill:
    """Parse a single ``SKILL.md`` file into a :class:`Skill`."""
    text = path.read_text(encoding="utf-8")
    meta, body = _split_frontmatter(text, path)
    missing = [f for f in REQUIRED_FIELDS if f not in meta]
    if missing:
        raise ValueError(f"{path}: frontmatter missing fields: {', '.join(missing)}")
    return Skill(
        name=str(meta["name"]),
        description=str(meta["description"]),
        phase=int(meta["phase"]),
        when_to_use=str(meta["when_to_use"]),
        body=body,
        path=path,
    )


def load_skills(skills_dir: Path = SKILLS_DIR) -> list[Skill]:
    """Discover and load every ``SKILL.md`` under ``skills_dir``, sorted by phase."""
    files = sorted(skills_dir.glob("*/SKILL.md"))
    if not files:
        raise FileNotFoundError(f"No SKILL.md files found under {skills_dir}")
    return sorted((load_skill(p) for p in files), key=lambda s: s.phase)


def select(phase: int, skills_dir: Path = SKILLS_DIR) -> Skill:
    """Return the single skill for the given pipeline ``phase``."""
    matches = [s for s in load_skills(skills_dir) if s.phase == phase]
    if not matches:
        raise ValueError(f"No skill found for phase {phase}")
    if len(matches) > 1:
        names = ", ".join(s.name for s in matches)
        raise ValueError(f"Multiple skills for phase {phase}: {names}")
    return matches[0]
