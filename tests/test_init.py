"""Tests for the workspace scaffolder (`localexpert init`) — no model required."""

from __future__ import annotations

import json

import nbformat
import yaml

from localexpert import init_cmd
from localexpert.skills import load_skills


def test_prompt_file_per_skill_with_valid_frontmatter():
    for skill in load_skills():
        name = init_cmd.prompt_file_name(skill)
        assert name == f"{skill.phase:02d}-{skill.name}.prompt.md"
        text = init_cmd.render_prompt_file(skill)
        assert text.startswith("---")
        fm = yaml.safe_load(text.split("---")[1])
        assert fm["agent"] == "agent"
        assert fm["description"] == skill.description
        # The skill's procedure carries through into the prompt body.
        assert "Procedure" in text


def test_build_workspace_scaffolds_all_artifacts(tmp_path):
    init_cmd.build_workspace(tmp_path, pull=False)

    # One prompt per phase, plus the shared instructions.
    phases = sorted(s.phase for s in load_skills())
    prompts = sorted((tmp_path / ".github" / "prompts").glob("*.prompt.md"))
    assert len(prompts) == len(phases)
    assert (tmp_path / ".github" / "copilot-instructions.md").is_file()

    # VS Code config is valid JSON with the expected keys.
    ext = json.loads((tmp_path / ".vscode" / "extensions.json").read_text())
    assert "ollama.ollama" in ext["recommendations"]
    settings = json.loads((tmp_path / ".vscode" / "settings.json").read_text())
    assert "python.defaultInterpreterPath" in settings

    # Starter notebook is valid and sample data was written.
    nb = nbformat.read(str(tmp_path / "notebooks" / "analysis_starter.ipynb"), as_version=4)
    nbformat.validate(nb)
    assert (tmp_path / "data" / "sample_biobehavioral.csv").is_file()
