---
name: resume-scorer
description: 使用结构化规则对中文或英文简历、单段项目经历和岗位 JD 打分。适用于评审、对标、优化、定制或改写简历与 JD 的场景，输出维度分、优势项、风险项、JD 匹配缺口和明确修改建议。
---

# resume-scorer

当用户希望对以下内容做结构化评估时，使用这个 skill：

- 一份完整简历
- 一段项目经历
- 一份岗位 JD
- 一段简历内容或项目经历与目标 JD 的对标结果

## 工作流

1. 先判断主输入属于 `resume`、`project` 还是 `jd`。如果用户额外提供了 JD，就把它作为岗位匹配度的对标上下文。
2. 如果文本已经在当前工作区中，优先直接运行本地评分脚本：

```bash
python3 skills/resume-scorer/scripts/score_resume.py --input-file /path/to/input.txt --kind resume
python3 skills/resume-scorer/scripts/score_resume.py --input-file /path/to/input.txt --jd-file /path/to/jd.txt --kind project --format json
```

3. 优先以脚本输出作为基础判断；如果不能运行脚本，再按照同一套 rubric 手动评估。
4. 最终结论必须严格基于用户提供的原文，不要凭空补充不存在的成绩、技术栈、指标或职责。

## 输出要求

始终返回：

- 总分
- 分维度得分
- 主要优势
- 主要风险或缺口
- 3 到 5 条按优先级排序的修改建议

当 `resume` 或 `project` 提供了 JD 对标信息时，还要返回：

- `fit score`
- 已匹配关键词
- 值得从 JD 中自然补齐的缺失关键词

如果用户需要改写帮助，可以针对最高优先级缺口生成优化后的 bullet，但必须保留原始事实；凡是需要用户补充确认的信息，都要明确标成占位内容。

## 参考文档

- `references/rubric.md`：查看各维度的评分逻辑。
- `references/output-contract.md`：查看建议的输出结构和改写边界。
