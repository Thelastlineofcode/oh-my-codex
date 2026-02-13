"""Tests for skills module."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path

from orchestrator.skills import (
    Skill,
    SkillMatch,
    SkillManager,
)


@pytest.fixture
def temp_skills_dir():
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def skill_manager(temp_skills_dir):
    return SkillManager(skills_dir=temp_skills_dir)


def _install_skill(mgr, name, **kwargs):
    skill = Skill(name=name, **kwargs)
    mgr.install_skill(skill)
    return skill


class TestSkill:
    def test_create(self):
        s = Skill(name="test", description="A test skill")
        assert s.name == "test"
        assert s.version == "1.0.0"

    def test_to_dict(self):
        s = Skill(name="test", keywords=["kw1"])
        d = s.to_dict()
        assert d["name"] == "test"
        assert d["keywords"] == ["kw1"]

    def test_from_dict(self):
        s = Skill.from_dict({"name": "x", "description": "d", "keywords": ["k"]})
        assert s.name == "x"
        assert s.keywords == ["k"]


class TestSkillManager:
    def test_list_empty(self, skill_manager):
        assert skill_manager.list_skills() == []

    def test_install_and_list(self, skill_manager):
        _install_skill(skill_manager, "my-skill", description="test")
        skills = skill_manager.list_skills()
        assert len(skills) == 1
        assert skills[0].name == "my-skill"

    def test_get_skill(self, skill_manager):
        _install_skill(skill_manager, "get-test", description="hello")
        skill = skill_manager.get_skill("get-test")
        assert skill is not None
        assert skill.description == "hello"

    def test_get_nonexistent(self, skill_manager):
        assert skill_manager.get_skill("nope") is None

    def test_uninstall(self, skill_manager):
        _install_skill(skill_manager, "remove-me")
        assert skill_manager.uninstall_skill("remove-me") is True
        assert skill_manager.get_skill("remove-me") is None

    def test_uninstall_nonexistent(self, skill_manager):
        assert skill_manager.uninstall_skill("nope") is False

    def test_search_by_name(self, skill_manager):
        _install_skill(skill_manager, "autopilot-mode", description="auto")
        _install_skill(skill_manager, "eco-mode", description="efficient")
        results = skill_manager.search("auto")
        assert len(results) == 1
        assert results[0].name == "autopilot-mode"

    def test_search_by_keyword(self, skill_manager):
        _install_skill(skill_manager, "test-skill", keywords=["tdd", "testing"])
        results = skill_manager.search("tdd")
        assert len(results) == 1

    def test_search_by_description(self, skill_manager):
        _install_skill(skill_manager, "s1", description="parallel execution mode")
        results = skill_manager.search("parallel")
        assert len(results) == 1

    def test_search_no_match(self, skill_manager):
        _install_skill(skill_manager, "s1", description="hello")
        results = skill_manager.search("zzzzz")
        assert len(results) == 0

    def test_match_prompt(self, skill_manager):
        _install_skill(skill_manager, "auto", keywords=["autopilot:", "autopilot "])
        match = skill_manager.match_prompt("autopilot: build something")
        assert match is not None
        assert match.skill.name == "auto"

    def test_match_prompt_no_match(self, skill_manager):
        _install_skill(skill_manager, "s1", keywords=["xyz"])
        match = skill_manager.match_prompt("hello world")
        assert match is None

    def test_create_from_template(self, skill_manager):
        skill = skill_manager.create_from_template("new-skill", description="A new one", keywords=["new:"])
        assert skill.name == "new-skill"
        loaded = skill_manager.get_skill("new-skill")
        assert loaded is not None

    def test_export_skill(self, skill_manager):
        _install_skill(skill_manager, "export-me", description="for export", keywords=["e"])
        result = skill_manager.export_skill("export-me")
        assert result is not None
        data = json.loads(result)
        assert data["name"] == "export-me"

    def test_export_nonexistent(self, skill_manager):
        assert skill_manager.export_skill("nope") is None

    def test_import_skill(self, skill_manager):
        json_str = json.dumps({"name": "imported", "description": "from json", "keywords": ["imp"]})
        skill = skill_manager.import_skill(json_str)
        assert skill is not None
        assert skill.name == "imported"
        loaded = skill_manager.get_skill("imported")
        assert loaded is not None

    def test_import_invalid_json(self, skill_manager):
        assert skill_manager.import_skill("not json") is None

    def test_import_no_name(self, skill_manager):
        assert skill_manager.import_skill('{"description": "no name"}') is None

    def test_skill_md_legacy(self, temp_skills_dir):
        skill_dir = temp_skills_dir / "legacy-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Legacy Skill\n\nA legacy format skill.\n")
        mgr = SkillManager(skills_dir=temp_skills_dir)
        skill = mgr.get_skill("legacy-skill")
        assert skill is not None
        assert skill.name == "legacy-skill"

    def test_multiple_skills(self, skill_manager):
        for i in range(5):
            _install_skill(skill_manager, f"skill-{i}")
        assert len(skill_manager.list_skills()) == 5
