"""Tests for the references layer and intent-based skill selection — no model needed."""

from __future__ import annotations

import pytest

from localexpert.agent import Agent
from localexpert.references import load_references, references_prompt_block
from localexpert.runtime import OllamaRuntime
from localexpert.skills import select, select_by_intent


def test_references_load_with_description_and_body():
    refs = load_references()
    assert refs, "no references discovered"
    names = {r.name for r in refs}
    assert {"statistical-conventions", "data-handling", "notebook-conventions"} <= names
    for r in refs:
        assert r.description.strip(), f"{r.path}: empty description"
        assert r.body.strip(), f"{r.path}: empty body"


def test_references_prompt_block_nonempty():
    block = references_prompt_block()
    assert "Shared conventions" in block
    assert "effect size" in block.lower()


def test_system_prompt_includes_references_and_skill():
    agent = Agent(runtime=OllamaRuntime)  # not started; only the prompt is built
    sp = agent._system_prompt(select(2))
    assert "Shared conventions" in sp          # references injected
    assert "eda-missingness" in sp             # the selected skill
    assert "data never leaves the laptop" in sp  # BASE_PERSONA


@pytest.mark.parametrize(
    "query, expected",
    [
        ("check scale reliability", "psychometrics-reliability"),
        ("size a study before collecting data", "power-analysis"),
        ("time to event with censoring", "survival-analysis"),
        ("clean up missing values and outliers", "cleaning-preprocessing"),
        ("fit a mixed effects model over months", "statistical-testing"),
        ("explore distributions and missingness", "eda-missingness"),
        ("define my hypothesis and variables", "define-question"),
    ],
)
def test_select_by_intent_routes(query, expected):
    assert select_by_intent(query).name == expected


def test_select_by_intent_rejects_empty_and_unmatched():
    with pytest.raises(ValueError):
        select_by_intent("the of to")          # all stopwords
    with pytest.raises(ValueError):
        select_by_intent("xyzzy zzzptplk")     # matches nothing
