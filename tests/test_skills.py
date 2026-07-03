"""Tests for skill loading — no model or kernel required."""

from __future__ import annotations

import pytest

from localexpert.skills import REQUIRED_FIELDS, load_skills, select


def test_all_phases_discovered():
    skills = load_skills()
    phases = sorted(s.phase for s in skills)
    # 1-4 pipeline phases, plus 5 psychometrics, 6 survival, 7 power analysis.
    assert phases == [1, 2, 3, 4, 5, 6, 7]


def test_frontmatter_fields_present():
    for skill in load_skills():
        for field in REQUIRED_FIELDS:
            value = getattr(skill, field)
            assert value not in (None, ""), f"{skill.path}: empty {field}"


def test_bodies_are_nonempty():
    for skill in load_skills():
        assert skill.body.strip(), f"{skill.path}: empty body"


def test_prompt_block_includes_name_and_body():
    skill = select(2)
    block = skill.prompt_block
    assert skill.name in block
    assert "Objective" in block


@pytest.mark.parametrize("phase", [1, 2, 3, 4, 5, 6, 7])
def test_select_returns_single_skill_per_phase(phase):
    skill = select(phase)
    assert skill.phase == phase


def test_select_unknown_phase_raises():
    with pytest.raises(ValueError):
        select(9)
