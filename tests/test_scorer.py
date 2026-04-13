from __future__ import annotations

from resume_scorer.cli import _format_markdown
from resume_scorer.scorer import evaluate_text


CHINESE_RESUME = """
张三 | Senior Data Analyst
邮箱: zhangsan@example.com
电话: 13800001234

个人简介
5 年数据分析与增长经验，擅长 SQL、Python、A/B testing、Tableau 和自动化报表。

工作经历
2022.06 - 至今 某电商平台 数据分析师
- 主导搭建增长分析看板，使用 SQL、Python 与 Tableau，将周报制作时间从 4 小时缩短到 15 分钟。
- 与产品和运营团队合作设计 A/B testing 实验，使首购转化率提升 12%。

项目经历
用户增长归因平台
- 负责埋点治理和归因模型设计，覆盖 30+ 核心漏斗事件，支持 5 个业务团队复用。

技能
Python, SQL, Tableau, Airflow, Experimentation

教育背景
复旦大学 统计学硕士
"""

DATA_ANALYST_JD = """
Senior Data Analyst

Responsibilities
- Partner with product and growth teams to define success metrics.
- Build dashboards and automate reporting with SQL, Python, and Tableau.
- Design A/B testing programs and analyze experiment outcomes.

Requirements
- 3+ years of analytics experience in consumer internet or e-commerce.
- Strong SQL and Python skills.
- Experience with experimentation, dashboarding, and stakeholder communication.

Nice to have
- Airflow, attribution modeling, lifecycle marketing.
"""

ENGLISH_PROJECT = """
Led development of an internal workflow platform using React and FastAPI for cross-team approvals.
Designed the permission model, migrated legacy forms, and shipped the MVP in six weeks.
The platform now supports 12 business teams and reduced manual approval handling time by 35%.
"""

PLAIN_BACKEND_JD = """
Backend Engineer

Responsibilities
- Build internal APIs and data services.

Requirements
- 5+ years of Java and Spring Boot experience.
- Familiarity with MySQL and Kafka.
"""


def _dimension_score(result, name: str) -> int:
    for dimension in result.dimensions:
        if dimension.name == name:
            return dimension.score
    raise AssertionError(f"Dimension not found: {name}")


def test_resume_scoring_with_jd_returns_fit_gap_signals() -> None:
    result = evaluate_text(CHINESE_RESUME, kind="resume", jd_text=DATA_ANALYST_JD)

    assert result.input_kind == "resume"
    assert result.overall_score >= 70
    assert result.fit_score is not None and result.fit_score >= 60
    assert "sql" in [keyword.lower() for keyword in result.extracted["keyword_overlap"]]
    assert _dimension_score(result, "impact") >= 70


def test_auto_detect_project_and_flag_missing_depth_or_impact() -> None:
    result = evaluate_text(ENGLISH_PROJECT, kind="auto")

    assert result.input_kind == "project"
    assert result.overall_score >= 60
    assert _dimension_score(result, "impact") >= 60
    assert _dimension_score(result, "technical_depth") >= 60


def test_jd_scoring_surfaces_candidate_attractiveness_gap() -> None:
    result = evaluate_text(PLAIN_BACKEND_JD, kind="jd")

    assert result.input_kind == "jd"
    assert _dimension_score(result, "attractiveness") < 60
    assert any("salary" in suggestion.lower() or "remote" in suggestion.lower() for suggestion in result.suggestions)


def test_markdown_formatter_includes_key_sections() -> None:
    result = evaluate_text(CHINESE_RESUME, kind="resume", jd_text=DATA_ANALYST_JD)
    rendered = _format_markdown(result)

    assert "# Resume Scorer Report" in rendered
    assert "## Dimensions" in rendered
    assert "Fit score" in rendered
