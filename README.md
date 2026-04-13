# resume-scorer-skill

`resume-scorer` 是一个中英双语的 skill 项目，用于对中文或英文简历、单段项目经历和岗位 JD 做结构化打分，并输出优先级明确的修改建议。

仓库结构参考了 `YifeiCAO/shandong-xiangfu` 这种轻量级的 skill 优先布局，但在此基础上补充了可执行的 Python 评分器和测试用例，方便复现、验证和继续扩展。

## 项目能力

- 对 `resume`、`project`、`jd` 三类输入分别使用独立评分维度。
- 支持中文、英文以及中英混合文本。
- 当简历或项目经历与 JD 配套输入时，会额外计算岗位匹配度。
- 输出优势项、风险项、缺失关键词和明确的修改建议。
- 既可以作为 Codex skill 使用，也可以通过本地 CLI 运行。

## 快速开始

```bash
cd resume-scorer-skill
python3 -m pip install -e .
resume-scorer --text "Built a data platform with Python and SQL..." --kind project
python3 skills/resume-scorer/scripts/score_resume.py --input-file sample_resume.txt --jd-file sample_jd.txt --kind resume --format json
python3 -m pytest
```

## 仓库结构

```text
resume-scorer-skill/
├── README.md
├── pyproject.toml
├── src/resume_scorer/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── models.py
│   └── scorer.py
├── skills/resume-scorer/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── output-contract.md
│   │   └── rubric.md
│   └── scripts/score_resume.py
└── tests/
    ├── conftest.py
    ├── test_repository.py
    └── test_scorer.py
```

## 评分维度

- `resume`：完整度、影响力、清晰度、针对性、可信度
- `project`：背景上下文、个人主导度、技术深度、影响力、清晰度
- `jd`：岗位清晰度、要求具体度、结构完整度、吸引力、筛选效率

当 `resume` 或 `project` 同时提供目标 JD 时，评分器还会返回 `fit_score`，并标记匹配关键词与缺失关键词。
# resume-scorer-skill
