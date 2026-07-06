"""Discover and load shared reference documents.

References are cross-cutting guidance the assistant should follow regardless of the
specific skill (statistical conventions, data handling, notebook conventions). They
are the single source of these rules — consumed by both front-ends: injected into the
CLI system prompt (`agent.py`) and exported to `.github/instructions/` for VS Code
(`init_cmd.py`).

Each reference is `references/<name>.md`: a YAML frontmatter block (`description`)
delimited by `---` lines, followed by a markdown body — the same shape as skills.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import yaml

# References ship inside the package so they resolve from an editable checkout and
# an installed wheel alike (same pattern as skills.SKILLS_DIR).
REFERENCES_DIR = Path(resources.files("localexpert") / "references")


@dataclass(frozen=True)
class Reference:
    """A parsed reference: its description plus the markdown body."""

    name: str
    description: str
    body: str
    path: Path

    @property
    def block(self) -> str:
        """The text injected into a system prompt."""
        return f"## {self.name}\n{self.body.strip()}\n"


def _split_frontmatter(text: str, path: Path) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing '---' frontmatter block")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: malformed frontmatter (need opening and closing '---')")
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: frontmatter must be a YAML mapping")
    return meta, parts[2]


def load_reference(path: Path) -> Reference:
    """Parse a single reference markdown file."""
    meta, body = _split_frontmatter(path.read_text(encoding="utf-8"), path)
    if "description" not in meta:
        raise ValueError(f"{path}: frontmatter missing 'description'")
    return Reference(
        name=path.stem,
        description=str(meta["description"]),
        body=body,
        path=path,
    )


def load_references(references_dir: Path = REFERENCES_DIR) -> list[Reference]:
    """Discover and load every reference under ``references_dir``, sorted by name."""
    files = sorted(references_dir.glob("*.md"))
    return [load_reference(p) for p in files]


def references_prompt_block(references_dir: Path = REFERENCES_DIR) -> str:
    """A single markdown block of all references, for injection into a system prompt."""
    refs = load_references(references_dir)
    if not refs:
        return ""
    body = "\n".join(r.block for r in refs)
    return f"# Shared conventions (always apply)\n\n{body}"
