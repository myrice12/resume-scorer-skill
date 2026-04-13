---
name: resume-scorer
description: "对中文或英文简历、项目经历和岗位 JD 做结构化评分，输出总分、维度分、JD 匹配度和修改建议。"
argument-hint: "[resume-or-jd-file-path]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

> **Language / 语言**：本 Skill 支持中文和英文。根据用户第一条消息的语言判断回复语言，并在整轮对话中保持一致。

# 简历评分 Skill（Claude Code 版）

## 触发条件

当用户说出以下任意内容时启动：

- `/resume-scorer`
- “帮我给这份简历打分”
- “帮我评估这段项目经历”
- “看看这个 JD 写得怎么样”
- “把简历和 JD 对标一下”
- “score this resume”
- “review this project blurb against the JD”

---

## 工具使用规则

| 任务 | 使用工具 |
|------|---------|
| 读取用户提供的简历、项目经历、JD | `Read` |
| 搜索本地 Markdown、TXT、PDF 文件 | `Glob` / `Grep` |
| 写入修改建议稿或改写稿 | `Write` / `Edit` |
| 创建输出目录 | `Bash` → `mkdir -p` |

---

## 主流程

### Step 1：接收输入

支持以下输入方式：

**方式 A：指定文件路径**  
用户直接给出简历、项目经历或 JD 文件路径，用 `Read` 读取。

**方式 B：粘贴文本**  
用户直接贴出内容，直接分析。

**方式 C：同时提供两个文本**  
当用户同时提供“简历/项目经历 + JD”时，将其视为对标分析任务。

**方式 D：要求帮忙搜索**  
如果用户只说“帮我找一下简历/JD”，就用 `Glob` 搜索 `**/*.md`、`**/*.txt`、`**/*.pdf` 中与 resume、cv、简历、jd、job description 等相关的文件。

读取后告知用户：

```text
已读取内容：{文件名或内容来源}
检测到类型：{resume / project / jd / resume+jd / project+jd}
语言：{中文 / English / mixed}
下一步开始结构化评分。
```

---

### Step 2：识别类型

参考 `${CLAUDE_SKILL_DIR}/prompts/classifier.md`：

1. 判断输入是 `resume`、`project` 还是 `jd`
2. 如果存在第二份文本，判断它是否是目标 JD
3. 提取目标岗位、核心关键词、量化结果、缺失信息
4. 决定后续应调用哪一套评分规则

---

### Step 3：执行评分

按输入类型分别参考：

- 简历：`${CLAUDE_SKILL_DIR}/prompts/scorer_resume.md`
- 项目经历：`${CLAUDE_SKILL_DIR}/prompts/scorer_project.md`
- 岗位 JD：`${CLAUDE_SKILL_DIR}/prompts/scorer_jd.md`

评分要求：

1. 所有维度都使用 0 到 100 分
2. 必须给出每个维度的打分理由
3. 必须从原文中抽取证据，不能凭空补充事实
4. 如果同时提供了 JD，则必须输出 `fit score`
5. 修改建议必须按优先级排序，而不是平铺罗列

---

### Step 4：输出结果

默认输出结构如下：

```text
一句话总评

总分：X/100
岗位匹配度：Y/100（如果有 JD）

分项评分：
- 维度 A：X/100
- 维度 B：Y/100

主要优势：
- ...

主要问题：
- ...

优先修改建议：
1. ...
2. ...
3. ...
```

额外要求：

- 如果用户输入的是简历或项目经历，要尽量指出“缺少量化结果”“缺少角色边界”“缺少目标岗位词汇”等具体问题
- 如果用户输入的是 JD，要明确指出是否“像职责列表”而不像“能吸引候选人的岗位说明”
- 如果用户明确要求改写，先保留原始事实，再给出优化后的 bullet 或段落

---

### Step 5：改写与导出

如果用户要求“直接帮我改”，则：

1. 基于最高优先级问题进行改写
2. 保留原始事实，不要编造指标
3. 对缺少事实支撑的内容用占位提示标注，例如：

```text
[待补充：请补一个具体指标，如提升百分比、覆盖用户数或节省时间]
```

如需写回文件，可生成：

- `{filename}.scored.md`：评分报告
- `{filename}.rewritten.md`：优化改写版本

---

## 质量要求

1. 所有结论都必须能追溯到原文
2. 修改建议必须可执行，不能只给空泛建议
3. 优先做“结构补齐”和“结果量化”，再做文案润色
4. 输出要专业、简洁、可直接用于求职优化场景
