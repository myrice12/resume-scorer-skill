from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Optional, Union

from .models import DimensionScore, EvaluationResult

RESUME_SECTION_KEYWORDS = {
    "contact": [
        "email",
        "phone",
        "mobile",
        "linkedin",
        "github",
        "邮箱",
        "电话",
        "手机",
        "微信",
        "联系",
    ],
    "summary": [
        "summary",
        "profile",
        "objective",
        "个人简介",
        "自我评价",
        "个人总结",
        "about me",
    ],
    "experience": [
        "experience",
        "employment",
        "work history",
        "professional experience",
        "工作经历",
        "实习经历",
        "任职经历",
    ],
    "project": [
        "project",
        "projects",
        "project experience",
        "项目经历",
        "项目经验",
        "重点项目",
    ],
    "skills": [
        "skills",
        "tools",
        "tech stack",
        "技术栈",
        "专业技能",
        "技能",
    ],
    "education": [
        "education",
        "degree",
        "university",
        "school",
        "教育背景",
        "学历",
        "毕业",
    ],
    "awards": [
        "award",
        "certification",
        "patent",
        "publication",
        "获奖",
        "证书",
        "论文",
        "专利",
    ],
}

PROJECT_SECTION_KEYWORDS = {
    "background": ["背景", "目标", "挑战", "problem", "context", "goal", "business", "internal", "workflow", "approval", "user"],
    "role": ["负责", "主导", "ownership", "role", "led", "owned", "drove"],
    "stack": ["技术栈", "tech stack", "using", "built with", "python", "java", "react", "sql", "fastapi", "permission"],
    "result": ["结果", "收益", "效果", "impact", "result", "improved", "reduced", "上线", "supports", "supported", "支撑"],
}

JD_SECTION_KEYWORDS = {
    "responsibilities": [
        "responsibilities",
        "what you'll do",
        "what you will do",
        "岗位职责",
        "工作职责",
        "你将负责",
    ],
    "requirements": [
        "requirements",
        "qualifications",
        "you should have",
        "must have",
        "任职要求",
        "岗位要求",
        "我们希望你",
    ],
    "preferred": [
        "preferred",
        "plus",
        "nice to have",
        "bonus",
        "加分项",
        "优先",
    ],
    "benefits": [
        "benefits",
        "perks",
        "compensation",
        "salary",
        "福利",
        "薪资",
        "年包",
        "remote",
        "hybrid",
    ],
    "company": [
        "about us",
        "about the team",
        "company",
        "team",
        "关于我们",
        "团队介绍",
        "业务背景",
    ],
}

TECH_KEYWORDS = [
    "python",
    "sql",
    "java",
    "golang",
    "go",
    "c++",
    "javascript",
    "typescript",
    "react",
    "vue",
    "node.js",
    "node",
    "spring",
    "spring boot",
    "django",
    "fastapi",
    "flask",
    "mysql",
    "postgresql",
    "redis",
    "kafka",
    "spark",
    "hadoop",
    "airflow",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "linux",
    "git",
    "rest",
    "grpc",
    "microservices",
    "backend",
    "frontend",
    "full stack",
    "etl",
    "tableau",
    "power bi",
    "ab testing",
    "a/b testing",
    "analytics",
    "experimentation",
    "data analysis",
    "data engineering",
    "machine learning",
    "deep learning",
    "nlp",
    "llm",
    "pytorch",
    "tensorflow",
    "大模型",
    "机器学习",
    "深度学习",
    "自然语言处理",
    "数据分析",
    "数据工程",
    "数据科学",
    "后端",
    "前端",
    "全栈",
    "云原生",
    "微服务",
    "分布式",
    "高并发",
    "推荐",
    "搜索",
    "风控",
    "增长",
    "电商",
    "支付",
    "供应链",
    "saas",
    "crm",
    "erp",
]

ACTION_VERBS = {
    "en": [
        "built",
        "designed",
        "implemented",
        "led",
        "launched",
        "shipped",
        "optimized",
        "improved",
        "reduced",
        "automated",
        "migrated",
        "developed",
        "created",
        "scaled",
        "analyzed",
        "partnered",
    ],
    "zh": [
        "负责",
        "主导",
        "设计",
        "实现",
        "优化",
        "搭建",
        "推动",
        "上线",
        "改造",
        "协调",
        "提升",
        "降低",
        "分析",
        "交付",
        "研发",
    ],
}

RESULT_TERMS = {
    "en": ["improved", "reduced", "increased", "saved", "grew", "boosted", "cut", "delivered"],
    "zh": ["提升", "降低", "减少", "增长", "节省", "缩短", "支撑", "覆盖", "落地"],
}

ARCHITECTURE_TERMS = [
    "architecture",
    "distributed",
    "latency",
    "throughput",
    "pipeline",
    "modeling",
    "permission",
    "observability",
    "cache",
    "queue",
    "schema",
    "permission",
    "workflow",
    "approval",
    "migration",
    "架构",
    "分布式",
    "高并发",
    "可观测",
    "链路",
    "权限",
    "缓存",
    "队列",
    "治理",
    "埋点",
]

TITLE_TERMS = [
    "engineer",
    "developer",
    "manager",
    "analyst",
    "scientist",
    "designer",
    "product",
    "运营",
    "工程师",
    "经理",
    "分析师",
    "科学家",
    "产品",
]

LEVEL_TERMS = ["senior", "staff", "lead", "principal", "junior", "mid", "高级", "资深", "专家", "主管"]
BENEFIT_TERMS = ["salary", "compensation", "benefits", "perks", "bonus", "equity", "remote", "hybrid", "薪资", "福利", "年包", "期权", "远程"]
MUST_HAVE_TERMS = ["must have", "required", "requirements", "任职要求", "必须", "至少", "3+", "5+"]
NICE_TO_HAVE_TERMS = ["nice to have", "preferred", "bonus", "plus", "加分项", "优先"]

METRIC_PATTERN = re.compile(
    r"(\b\d+(?:\.\d+)?\s?(?:%|x|k|m|b|ms|s|yrs?|years?|months?|people|users|teams?|services?|requests?|qps|tps)\b|\b\d+(?:\.\d+)?\s+(?:[a-z-]+\s+)?(?:teams?|users?|services?|requests?|events?|pipelines?|regions?)\b|\d+(?:\.\d+)?\s?(?:万|亿|人|次|个|天|月|年|小时|分钟|%)|[0-9]+\+)",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s-]{6,}\d)")
DATE_PATTERN = re.compile(r"(20\d{2}[./-]?\d{0,2}|20\d{2}\s*-\s*(?:present|now)|至今)")
BULLET_PATTERN = re.compile(r"^\s*(?:[-*•·]|\d+\.)\s+")
EN_TOKEN_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9+.#/-]{2,}\b")
ZH_CHAR_PATTERN = re.compile(r"[\u4e00-\u9fff]")
LONG_LINE_THRESHOLD = 150

EN_STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "this",
    "that",
    "from",
    "have",
    "has",
    "into",
    "about",
    "over",
    "role",
    "team",
    "work",
    "project",
    "projects",
    "experience",
    "responsibilities",
    "requirements",
    "using",
    "used",
    "build",
    "building",
    "developed",
    "description",
}


def evaluate_text(text: str, kind: str = "auto", jd_text: Optional[str] = None) -> EvaluationResult:
    clean_text = _normalize_text(text)
    clean_jd = _normalize_text(jd_text or "")
    input_kind = kind if kind != "auto" else _infer_kind(clean_text)
    language = _detect_language(clean_text)

    if input_kind == "resume":
        return _score_resume(clean_text, language, clean_jd or None)
    if input_kind == "project":
        return _score_project(clean_text, language, clean_jd or None)
    if input_kind == "jd":
        return _score_jd(clean_text, language)
    raise ValueError(f"Unsupported kind: {input_kind}")


def _normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").strip().splitlines())


def _infer_kind(text: str) -> str:
    lowered = text.lower()
    resume_hits = _keyword_hit_count(lowered, RESUME_SECTION_KEYWORDS.values())
    project_hits = _keyword_hit_count(lowered, PROJECT_SECTION_KEYWORDS.values())
    jd_hits = _keyword_hit_count(lowered, JD_SECTION_KEYWORDS.values())

    if jd_hits >= 3 and jd_hits >= resume_hits + 1:
        return "jd"
    if resume_hits >= 2 or EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text):
        return "resume"
    if project_hits >= 2:
        return "project"
    if _count_bullets(_lines(text)) <= 2 and len(_extract_metrics(text)) <= 1:
        return "project"
    return "resume"


def _detect_language(text: str) -> str:
    zh_chars = len(ZH_CHAR_PATTERN.findall(text))
    en_tokens = len(re.findall(r"\b[A-Za-z]{2,}\b", text))
    if zh_chars and en_tokens:
        ratio = zh_chars / max(en_tokens, 1)
        if ratio >= 0.6:
            return "mixed"
    if zh_chars >= 20:
        return "zh"
    return "en"


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _keyword_hit_count(text: str, groups: Iterable[Iterable[str]]) -> int:
    return sum(1 for group in groups if any(keyword in text for keyword in group))


def _extract_metrics(text: str) -> list[str]:
    return _unique(METRIC_PATTERN.findall(text))


def _count_action_verbs(text: str) -> int:
    lowered = text.lower()
    count = 0
    for verb in ACTION_VERBS["en"]:
        count += len(re.findall(rf"\b{re.escape(verb)}\b", lowered))
    for verb in ACTION_VERBS["zh"]:
        count += lowered.count(verb)
    return count


def _count_result_terms(text: str) -> int:
    lowered = text.lower()
    count = 0
    for term in RESULT_TERMS["en"]:
        count += len(re.findall(rf"\b{re.escape(term)}\b", lowered))
    for term in RESULT_TERMS["zh"]:
        count += lowered.count(term)
    return count


def _count_bullets(lines: list[str]) -> int:
    return sum(1 for line in lines if BULLET_PATTERN.match(line))


def _section_presence(text: str, mapping: dict[str, list[str]]) -> dict[str, bool]:
    lowered = text.lower()
    return {section: any(keyword in lowered for keyword in keywords) for section, keywords in mapping.items()}


def _extract_keywords(text: str) -> list[str]:
    lowered = text.lower()
    keywords = [keyword for keyword in TECH_KEYWORDS if keyword in lowered]

    english_tokens = [
        token.lower()
        for token in EN_TOKEN_PATTERN.findall(text)
        if token.lower() not in EN_STOPWORDS and not token.lower().isdigit()
    ]
    counts = Counter(english_tokens)
    for token, frequency in counts.most_common(20):
        if frequency >= 2 or token in TITLE_TERMS:
            keywords.append(token)
    return _unique(keywords)


def _keyword_overlap(candidate_keywords: list[str], jd_keywords: list[str]) -> tuple[list[str], list[str], float]:
    if not jd_keywords:
        return [], [], 0.0
    candidate_set = {keyword.lower() for keyword in candidate_keywords}
    jd_set = {keyword.lower() for keyword in jd_keywords}
    overlap = _unique([keyword for keyword in jd_keywords if keyword.lower() in candidate_set])
    missing = _unique([keyword for keyword in jd_keywords if keyword.lower() not in candidate_set])
    ratio = len(overlap) / max(len(jd_set), 1)
    return overlap, missing, ratio


def _score_resume(text: str, language: str, jd_text: Optional[str]) -> EvaluationResult:
    lines = _lines(text)
    sections = _section_presence(text, RESUME_SECTION_KEYWORDS)
    metrics = _extract_metrics(text)
    action_count = _count_action_verbs(text)
    result_count = _count_result_terms(text)
    bullets = _count_bullets(lines)
    dates = DATE_PATTERN.findall(text)
    keywords = _extract_keywords(text)

    completeness_weights = {
        "contact": 5,
        "summary": 10,
        "experience": 30,
        "project": 20,
        "skills": 15,
        "education": 15,
        "awards": 5,
    }
    completeness = sum(weight for section, weight in completeness_weights.items() if sections.get(section))
    if not sections["experience"] and not sections["project"]:
        completeness = max(completeness - 20, 0)

    quantified_lines = sum(1 for line in lines if METRIC_PATTERN.search(line))
    impact = 18 + min(len(metrics), 5) * 10 + min(quantified_lines, 4) * 8 + min(action_count, 10) * 3 + min(result_count, 4) * 6
    if len(metrics) == 0:
        impact -= 12
    if action_count < 3:
        impact -= 8
    impact = _clamp(impact)

    long_lines = sum(1 for line in lines if len(line) > LONG_LINE_THRESHOLD)
    clarity = 35 + sum(1 for present in sections.values() if present) * 7 + min(bullets, 8) * 3 + min(len(dates), 4) * 4 - long_lines * 8
    if bullets == 0 and len(lines) > 4:
        clarity -= 12
    clarity = _clamp(clarity)

    if jd_text:
        jd_keywords = _extract_keywords(jd_text)
        overlap, missing, ratio = _keyword_overlap(keywords, jd_keywords)
        targeting = 35 + int(ratio * 50) + min(len(overlap), 5) * 3
        if jd_keywords and not overlap:
            targeting -= 12
        targeting = _clamp(targeting)
        fit_score = targeting
    else:
        jd_keywords = []
        overlap = []
        missing = []
        targeting = _clamp(42 + min(len(keywords), 10) * 4 + (10 if sections["summary"] else 0))
        fit_score = None

    credibility = 24 + min(len(dates), 4) * 10 + min(len(keywords), 8) * 4 + min(len(metrics), 4) * 5
    if not dates:
        credibility -= 10
    if len(keywords) < 3:
        credibility -= 8
    credibility = _clamp(credibility)

    dimensions = [
        DimensionScore(
            name="completeness",
            score=completeness,
            reason="Section coverage shows whether the resume is easy to screen quickly.",
            evidence=_resume_section_evidence(sections),
            suggestions=_resume_section_suggestions(sections),
        ),
        DimensionScore(
            name="impact",
            score=impact,
            reason="The strongest resumes show actions, scale, and measurable outcomes.",
            evidence=[f"metrics: {len(metrics)}", f"action verbs: {action_count}", f"result markers: {result_count}"],
            suggestions=_impact_suggestions(impact, kind="resume"),
        ),
        DimensionScore(
            name="clarity",
            score=clarity,
            reason="Readable structure and concise bullets make recruiter scanning easier.",
            evidence=[f"bullet lines: {bullets}", f"dated entries: {len(dates)}", f"long lines: {long_lines}"],
            suggestions=_clarity_suggestions(clarity, kind="resume"),
        ),
        DimensionScore(
            name="targeting",
            score=targeting,
            reason="Targeting measures how explicitly the text matches the intended role or JD.",
            evidence=_targeting_evidence(overlap, missing, jd_keywords),
            suggestions=_targeting_suggestions(targeting, missing, jd_text is not None),
        ),
        DimensionScore(
            name="credibility",
            score=credibility,
            reason="Specific tools, dates, and scope boundaries make claims feel more believable.",
            evidence=[f"keywords: {len(keywords)}", f"metrics: {len(metrics)}", f"date markers: {len(dates)}"],
            suggestions=_credibility_suggestions(credibility),
        ),
    ]

    overall = _weighted_average(
        {
            "completeness": (completeness, 0.24),
            "impact": (impact, 0.24),
            "clarity": (clarity, 0.18),
            "targeting": (targeting, 0.20),
            "credibility": (credibility, 0.14),
        }
    )

    strengths = _dimension_observations(dimensions, threshold=78, positive=True)
    risks = _dimension_observations(dimensions, threshold=68, positive=False)
    suggestions = _merge_suggestions(dimensions)
    summary = _build_summary("resume", overall, dimensions)

    return EvaluationResult(
        input_kind="resume",
        language=language,
        overall_score=overall,
        fit_score=fit_score,
        summary=summary,
        dimensions=dimensions,
        strengths=strengths,
        risks=risks,
        suggestions=suggestions,
        extracted={
            "sections_present": [name for name, present in sections.items() if present],
            "metrics_found": metrics,
            "keywords": keywords[:15],
            "jd_keywords": jd_keywords[:15],
            "keyword_overlap": overlap[:12],
            "missing_keywords": missing[:12],
        },
    )


def _score_project(text: str, language: str, jd_text: Optional[str]) -> EvaluationResult:
    lines = _lines(text)
    sections = _section_presence(text, PROJECT_SECTION_KEYWORDS)
    metrics = _extract_metrics(text)
    keywords = _extract_keywords(text)
    action_count = _count_action_verbs(text)
    result_count = _count_result_terms(text)
    bullets = _count_bullets(lines)
    long_lines = sum(1 for line in lines if len(line) > LONG_LINE_THRESHOLD)
    architecture_hits = sum(1 for term in ARCHITECTURE_TERMS if term in text.lower())

    context_terms = sum(1 for marker in ("workflow", "approval", "business", "user", "internal", "平台", "系统") if marker in text.lower() or marker in text)
    context = 28 + (20 if sections["background"] else 0) + min(len(DATE_PATTERN.findall(text)), 3) * 5 + min(len(lines), 6) * 3 + min(context_terms, 3) * 4
    if not sections["background"] and "problem" not in text.lower() and "背景" not in text:
        context -= 10
    context = _clamp(context)

    ownership = 28 + (22 if sections["role"] else 0) + min(action_count, 8) * 4
    if action_count < 2:
        ownership -= 14
    ownership = _clamp(ownership)

    technical_depth = 28 + min(len(keywords), 8) * 6 + min(architecture_hits, 5) * 7
    if not sections["stack"] and len(keywords) < 3:
        technical_depth -= 10
    technical_depth = _clamp(technical_depth)

    impact = 30 + min(len(metrics), 4) * 12 + min(result_count, 4) * 8
    if len(metrics) == 0:
        impact -= 16
    impact = _clamp(impact)

    clarity = 32 + sum(1 for present in sections.values() if present) * 9 + min(bullets, 6) * 4 - long_lines * 8
    if bullets == 0 and len(lines) > 3:
        clarity -= 10
    clarity = _clamp(clarity)

    if jd_text:
        jd_keywords = _extract_keywords(jd_text)
        overlap, missing, ratio = _keyword_overlap(keywords, jd_keywords)
        fit_score = _clamp(34 + int(ratio * 52) + min(len(overlap), 5) * 3)
    else:
        jd_keywords = []
        overlap = []
        missing = []
        fit_score = None

    dimensions = [
        DimensionScore(
            name="context",
            score=context,
            reason="Strong project blurbs explain what business or technical problem mattered.",
            evidence=[f"context markers: {int(sections['background'])}", f"lines: {len(lines)}"],
            suggestions=_project_context_suggestions(context),
        ),
        DimensionScore(
            name="ownership",
            score=ownership,
            reason="Hiring teams want to see what you personally drove rather than what the team did.",
            evidence=[f"action verbs: {action_count}", f"role markers: {int(sections['role'])}"],
            suggestions=_project_ownership_suggestions(ownership),
        ),
        DimensionScore(
            name="technical_depth",
            score=technical_depth,
            reason="The blurb should reveal architecture choices, tools, and non-trivial engineering work.",
            evidence=[f"keywords: {len(keywords)}", f"architecture markers: {architecture_hits}"],
            suggestions=_project_depth_suggestions(technical_depth),
        ),
        DimensionScore(
            name="impact",
            score=impact,
            reason="Without outcomes or scope, a project can sound like a task list instead of a contribution.",
            evidence=[f"metrics: {len(metrics)}", f"result markers: {result_count}"],
            suggestions=_impact_suggestions(impact, kind="project"),
        ),
        DimensionScore(
            name="clarity",
            score=clarity,
            reason="Project descriptions land better when they follow a compact situation-action-result flow.",
            evidence=[f"bullet lines: {bullets}", f"long lines: {long_lines}"],
            suggestions=_clarity_suggestions(clarity, kind="project"),
        ),
    ]

    overall = _weighted_average(
        {
            "context": (context, 0.20),
            "ownership": (ownership, 0.22),
            "technical_depth": (technical_depth, 0.24),
            "impact": (impact, 0.20),
            "clarity": (clarity, 0.14),
        }
    )

    strengths = _dimension_observations(dimensions, threshold=78, positive=True)
    risks = _dimension_observations(dimensions, threshold=68, positive=False)
    suggestions = _merge_suggestions(dimensions)
    if fit_score is not None and missing:
        suggestions.append(f"Map the project explicitly to the JD by naming missing terms such as: {', '.join(missing[:5])}.")
    summary = _build_summary("project", overall, dimensions)

    return EvaluationResult(
        input_kind="project",
        language=language,
        overall_score=overall,
        fit_score=fit_score,
        summary=summary,
        dimensions=dimensions,
        strengths=strengths,
        risks=risks,
        suggestions=_unique(suggestions),
        extracted={
            "sections_present": [name for name, present in sections.items() if present],
            "metrics_found": metrics,
            "keywords": keywords[:15],
            "jd_keywords": jd_keywords[:15],
            "keyword_overlap": overlap[:12],
            "missing_keywords": missing[:12],
        },
    )


def _score_jd(text: str, language: str) -> EvaluationResult:
    lines = _lines(text)
    sections = _section_presence(text, JD_SECTION_KEYWORDS)
    keywords = _extract_keywords(text)
    bullets = _count_bullets(lines)
    title_hits = sum(1 for term in TITLE_TERMS if term in text.lower())
    level_hits = sum(1 for term in LEVEL_TERMS if term in text.lower())
    benefit_hits = sum(1 for term in BENEFIT_TERMS if term in text.lower())
    must_have_hits = sum(1 for term in MUST_HAVE_TERMS if term in text.lower())
    nice_to_have_hits = sum(1 for term in NICE_TO_HAVE_TERMS if term in text.lower())
    year_requirements = len(re.findall(r"\b\d+\+?\s*(?:years?|yrs?)\b|\d+\+?\s*年", text.lower()))

    role_clarity = 22 + min(title_hits, 2) * 18 + min(level_hits, 2) * 10 + (20 if sections["company"] else 0) + (10 if "remote" in text.lower() or "地点" in text else 0)
    role_clarity = _clamp(role_clarity)

    specificity = 18 + min(len(keywords), 10) * 4 + min(year_requirements, 2) * 12 + min(must_have_hits, 3) * 10
    if not sections["requirements"]:
        specificity -= 12
    specificity = _clamp(specificity)

    structure = 24 + sum(1 for present in sections.values() if present) * 12 + (10 if 4 <= bullets <= 14 else 0)
    structure = _clamp(structure)

    attractiveness = 18 + min(benefit_hits, 4) * 12 + (12 if "salary" in text.lower() or "薪资" in text else 0) + (10 if "remote" in text.lower() or "hybrid" in text.lower() or "远程" in text else 0)
    attractiveness = _clamp(attractiveness)

    screening_efficiency = 26 + min(must_have_hits, 3) * 12 + min(nice_to_have_hits, 2) * 10 + (12 if sections["responsibilities"] and sections["requirements"] else 0)
    if bullets > 16:
        screening_efficiency -= 18
    screening_efficiency = _clamp(screening_efficiency)

    dimensions = [
        DimensionScore(
            name="role_clarity",
            score=role_clarity,
            reason="Candidates need to understand the role, level, and business context quickly.",
            evidence=[f"title markers: {title_hits}", f"level markers: {level_hits}", f"company context: {int(sections['company'])}"],
            suggestions=_jd_role_suggestions(role_clarity),
        ),
        DimensionScore(
            name="specificity",
            score=specificity,
            reason="Specific requirements improve signal quality and make screening faster.",
            evidence=[f"keywords: {len(keywords)}", f"year requirements: {year_requirements}", f"must-have markers: {must_have_hits}"],
            suggestions=_jd_specificity_suggestions(specificity),
        ),
        DimensionScore(
            name="structure",
            score=structure,
            reason="A strong JD separates responsibilities, must-haves, and nice-to-haves cleanly.",
            evidence=[f"sections: {sum(1 for present in sections.values() if present)}", f"bullets: {bullets}"],
            suggestions=_jd_structure_suggestions(structure),
        ),
        DimensionScore(
            name="attractiveness",
            score=attractiveness,
            reason="Good candidates respond better when the role includes concrete reasons to engage.",
            evidence=[f"benefit markers: {benefit_hits}", f"salary markers: {int('salary' in text.lower() or '薪资' in text)}"],
            suggestions=_jd_attractiveness_suggestions(attractiveness),
        ),
        DimensionScore(
            name="screening_efficiency",
            score=screening_efficiency,
            reason="The best JDs distinguish non-negotiables from optional strengths without becoming a laundry list.",
            evidence=[f"must-have markers: {must_have_hits}", f"nice-to-have markers: {nice_to_have_hits}", f"bullets: {bullets}"],
            suggestions=_jd_screening_suggestions(screening_efficiency),
        ),
    ]

    overall = _weighted_average(
        {
            "role_clarity": (role_clarity, 0.22),
            "specificity": (specificity, 0.24),
            "structure": (structure, 0.18),
            "attractiveness": (attractiveness, 0.18),
            "screening_efficiency": (screening_efficiency, 0.18),
        }
    )

    strengths = _dimension_observations(dimensions, threshold=78, positive=True)
    risks = _dimension_observations(dimensions, threshold=68, positive=False)
    suggestions = _merge_suggestions(dimensions)
    summary = _build_summary("jd", overall, dimensions)

    return EvaluationResult(
        input_kind="jd",
        language=language,
        overall_score=overall,
        fit_score=None,
        summary=summary,
        dimensions=dimensions,
        strengths=strengths,
        risks=risks,
        suggestions=suggestions,
        extracted={
            "sections_present": [name for name, present in sections.items() if present],
            "keywords": keywords[:15],
            "metrics_found": _extract_metrics(text),
        },
    )


def _resume_section_evidence(sections: dict[str, bool]) -> list[str]:
    return [f"{section}: {'yes' if present else 'no'}" for section, present in sections.items()]


def _resume_section_suggestions(sections: dict[str, bool]) -> list[str]:
    missing = [section for section, present in sections.items() if not present]
    if not missing:
        return []
    display_names = {
        "contact": "contact information",
        "summary": "a short summary",
        "experience": "work experience",
        "project": "project highlights",
        "skills": "skills or tech stack",
        "education": "education",
        "awards": "awards or certifications",
    }
    shortlist = [display_names[name] for name in missing[:3]]
    return [f"Add or label {', '.join(shortlist)} so reviewers can scan the resume without guessing."]


def _impact_suggestions(score: int, kind: str) -> list[str]:
    if score >= 70:
        return []
    if kind == "resume":
        return ["Rewrite bullets as action + scope + tool + quantified result instead of duty-only statements."]
    return ["Add a concrete outcome such as latency, users, revenue, efficiency gain, or rollout scope."]


def _clarity_suggestions(score: int, kind: str) -> list[str]:
    if score >= 70:
        return []
    if kind == "resume":
        return ["Use short bullet points and reverse-chronological sections instead of dense paragraphs."]
    return ["Restructure the blurb into a compact context -> action -> result flow with 2-4 bullets."]


def _targeting_evidence(overlap: list[str], missing: list[str], jd_keywords: list[str]) -> list[str]:
    if not jd_keywords:
        return ["No JD provided; used generic role targeting signals instead."]
    return [
        f"overlap: {', '.join(overlap[:5]) or 'none'}",
        f"missing: {', '.join(missing[:5]) or 'none'}",
    ]


def _targeting_suggestions(score: int, missing: list[str], has_jd: bool) -> list[str]:
    if score >= 70:
        return []
    if has_jd and missing:
        return [f"Mirror the JD's exact wording for missing capabilities such as: {', '.join(missing[:5])}."]
    return ["State the target role more explicitly in the summary and order the strongest matching experience first."]


def _credibility_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Add dates, team scope, usage volume, or ownership boundaries so the claims feel more concrete."]


def _project_context_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Open with one sentence on the problem, user, or business goal before describing implementation details."]


def _project_ownership_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Separate what you personally designed or implemented from what the team delivered together."]


def _project_depth_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Name the core architecture choice, technical constraint, and why your solution was non-trivial."]


def _jd_role_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Clarify the job title, level, reporting line, and team or business context near the top."]


def _jd_specificity_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Replace vague asks with screenable requirements such as years, scope, systems, or must-use tools."]


def _jd_structure_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Split the JD into responsibilities, must-haves, and nice-to-haves so candidates can self-qualify faster."]


def _jd_attractiveness_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Add salary, location or remote policy, team stage, or growth reasons to make the role more compelling."]


def _jd_screening_suggestions(score: int) -> list[str]:
    if score >= 70:
        return []
    return ["Keep non-negotiables short and explicit; move bonus items into a separate preferred section."]


def _dimension_observations(dimensions: list[DimensionScore], threshold: int, positive: bool) -> list[str]:
    ordered = sorted(dimensions, key=lambda item: item.score, reverse=positive)
    selected = []
    for dimension in ordered:
        if positive and dimension.score >= threshold:
            selected.append(f"{dimension.name} is strong at {dimension.score}/100.")
        if not positive and dimension.score <= threshold:
            selected.append(f"{dimension.name} needs work at {dimension.score}/100.")
    return selected[:3]


def _merge_suggestions(dimensions: list[DimensionScore]) -> list[str]:
    suggestions: list[str] = []
    for dimension in dimensions:
        suggestions.extend(dimension.suggestions)
    return _unique(suggestions)[:5]


def _build_summary(kind: str, overall: int, dimensions: list[DimensionScore]) -> str:
    ranked = sorted(dimensions, key=lambda item: item.score, reverse=True)
    strongest = ranked[0]
    weakest = ranked[-1]
    if overall >= 80:
        tone = "already reads as a strong draft"
    elif overall >= 65:
        tone = "has a solid base but still leaves signal on the table"
    else:
        tone = "needs a sharper structure and evidence layer"
    return (
        f"This {kind} {tone}. The current strength is {strongest.name} ({strongest.score}/100), "
        f"while the main gap is {weakest.name} ({weakest.score}/100)."
    )


def _weighted_average(weighted_scores: dict[str, tuple[int, float]]) -> int:
    total = sum(score * weight for score, weight in weighted_scores.values())
    return int(round(total))


def _clamp(value: Union[int, float], lower: int = 0, upper: int = 100) -> int:
    return max(lower, min(int(round(value)), upper))


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        if not item:
            continue
        key = item.lower() if isinstance(item, str) else str(item)
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)
    return unique_items
