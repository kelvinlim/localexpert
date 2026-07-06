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
from importlib import resources
from pathlib import Path

import yaml

# Skills ship *inside* the package (src/localexpert/skills/) so they resolve both
# from an editable checkout and from an installed wheel. `resources.files` returns
# a path into the installed package data either way.
SKILLS_DIR = Path(resources.files("localexpert") / "skills")

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


# Words too generic (in a data-analysis tool) to distinguish one skill from another.
_STOPWORDS = frozenset(
    "a an the of to for and or in on with without is are do does this that i want "
    "we my me it its some any how what which over into out want need please help "
    "analysis analyse analyze data dataset".split()
)


def _tokens(text: str) -> set[str]:
    cleaned = "".join(c.lower() if c.isalnum() else " " for c in text)
    return {w for w in cleaned.split() if len(w) > 2 and w not in _STOPWORDS}


def _overlap(query_tokens: set[str], corpus_tokens: set[str]) -> int:
    """Count query tokens that match a corpus token exactly or by 4+ char prefix.

    Prefix matching gives light stemming (clean~cleaning, missing~missingness,
    outlier~outliers) without a stemming dependency.
    """
    count = 0
    for q in query_tokens:
        if q in corpus_tokens or any(
            len(q) >= 4 and len(t) >= 4 and (t.startswith(q) or q.startswith(t))
            for t in corpus_tokens
        ):
            count += 1
    return count


def select_by_intent(query: str, skills_dir: Path = SKILLS_DIR) -> Skill:
    """Pick the skill whose text best matches a free-text ``query``.

    A lightweight, dependency-free keyword-overlap scorer over each skill's
    ``when_to_use`` + ``description`` + ``name`` + ``body`` — a heuristic for routing a
    task to a skill, **not** an LLM router. Ties break to the lowest phase. Raises
    ``ValueError`` if the query has no usable words or nothing matches.
    """
    q = _tokens(query)
    if not q:
        raise ValueError(f"No usable words in task query: {query!r}")
    corpora = [
        (s, _tokens(f"{s.when_to_use} {s.description} {s.name} {s.body}"))
        for s in load_skills(skills_dir)
    ]
    # Weight each query token by how discriminative it is: a token matching many
    # skills (e.g. "before") is worth less than one matching a single skill.
    hits = {t: [c for _, c in corpora if _overlap({t}, c)] for t in q}
    weight = {t: (1.0 / len(cs) if cs else 0.0) for t, cs in hits.items()}

    def score(corpus: set[str]) -> float:
        return sum(weight[t] for t in q if _overlap({t}, corpus))

    scored = sorted(
        ((score(c), -s.phase, s) for s, c in corpora),
        key=lambda t: (t[0], t[1]),
        reverse=True,
    )
    best_score, _, best = scored[0]
    if best_score == 0:
        raise ValueError(
            f"No skill matched task {query!r}. Try `--phase` or `localexpert skills`."
        )
    return best
