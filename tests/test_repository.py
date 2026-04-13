from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_repository_layout() -> None:
    expected_paths = [
        ROOT / "README.md",
        ROOT / "pyproject.toml",
        ROOT / "src" / "resume_scorer" / "scorer.py",
        ROOT / "skills" / "resume-scorer" / "SKILL.md",
        ROOT / "skills" / "resume-scorer" / "agents" / "openai.yaml",
        ROOT / "skills" / "resume-scorer" / "references" / "rubric.md",
        ROOT / "skills" / "resume-scorer" / "references" / "output-contract.md",
        ROOT / "skills" / "resume-scorer" / "scripts" / "score_resume.py",
        ROOT / "tests" / "test_scorer.py",
    ]

    for path in expected_paths:
        assert path.exists(), f"Missing expected path: {path}"


def test_skill_metadata_describes_scope() -> None:
    skill_text = (ROOT / "skills" / "resume-scorer" / "SKILL.md").read_text(encoding="utf-8")
    assert "中文或英文简历" in skill_text
    assert "岗位 JD" in skill_text
    assert "score_resume.py" in skill_text


def test_openai_yaml_default_prompt_mentions_skill_name() -> None:
    yaml_text = (ROOT / "skills" / "resume-scorer" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "$resume-scorer" in yaml_text
