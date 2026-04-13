# 简历评分 Skill（resume-scorer）

> 对中文或英文简历、单段项目经历、岗位 JD 做结构化打分，并给出明确的修改建议。

## 这是什么

`resume-scorer` 是一个面向简历优化场景的 Skill 仓库，严格采用 `my-anti-distill` 的扁平项目结构：

- 根目录直接放 `SKILL.md`
- 评分规则拆到 `prompts/`
- 使用示例放到 `examples/`
- 补充 `README.md` 和 `INSTALL.md`

这个 Skill 不依赖额外代码或 Python 包，核心能力全部通过 Skill 主流程和 prompt 文件来约束。

## 它做什么

1. 识别输入是 `resume`、`project`、`jd`，还是“简历/项目 + JD 对标”
2. 对简历进行五维评分：完整度、影响力、清晰度、针对性、可信度
3. 对项目经历进行五维评分：背景上下文、个人主导度、技术深度、影响力、清晰度
4. 对 JD 进行五维评分：岗位清晰度、要求具体度、结构完整度、吸引力、筛选效率
5. 当提供目标 JD 时，额外输出匹配度、匹配关键词和缺失关键词
6. 给出 3 到 5 条按优先级排序的修改建议，并在需要时生成改写版本

## 安装

见 [INSTALL.md](./INSTALL.md)。

## 使用

在 Claude Code 或兼容的 Skill 环境里触发：

```text
/resume-scorer
```

或直接说：

- “帮我给这份简历打分”
- “看看这段项目经历适不适合这个 JD”
- “这个岗位 JD 写得怎么样”
- “帮我把这份英文简历按目标岗位优化一下”

## 项目结构

```text
resume-scorer-skill/
├── SKILL.md
├── prompts/
│   ├── classifier.md
│   ├── scorer_resume.md
│   ├── scorer_project.md
│   └── scorer_jd.md
├── README.md
├── INSTALL.md
└── examples/
    └── lihua_before_after.md
```

## 输出风格

输出默认包含：

- 一句话总评
- 总分，必要时附 `fit score`
- 分维度打分
- 主要优势
- 主要问题
- 明确修改建议

如果用户要求改写，还应输出优化后的 bullet 或段落，但不能编造原文不存在的事实。
