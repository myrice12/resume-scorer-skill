from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional

from .models import EvaluationResult
from .scorer import evaluate_text


def _read_optional_text(file_path: Optional[str], inline_text: Optional[str]) -> Optional[str]:
    if file_path and inline_text:
        raise ValueError("Use either a file path or inline text, not both.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    return inline_text


def _format_markdown(result: EvaluationResult) -> str:
    lines = [
        "# Resume Scorer Report",
        f"- Input kind: `{result.input_kind}`",
        f"- Language: `{result.language}`",
        f"- Overall score: `{result.overall_score}/100`",
    ]
    if result.fit_score is not None:
        lines.append(f"- Fit score: `{result.fit_score}/100`")

    lines.extend(
        [
            "",
            "## Summary",
            result.summary,
            "",
            "## Dimensions",
        ]
    )

    for dimension in result.dimensions:
        lines.append(f"- `{dimension.name}`: `{dimension.score}/100` - {dimension.reason}")

    if result.strengths:
        lines.extend(["", "## Strengths"])
        lines.extend(f"- {item}" for item in result.strengths)

    if result.risks:
        lines.extend(["", "## Risks"])
        lines.extend(f"- {item}" for item in result.risks)

    if result.suggestions:
        lines.extend(["", "## Suggested Revisions"])
        lines.extend(f"1. {item}" for item in result.suggestions)

    extracted = result.extracted
    interesting_keys = ["keywords", "jd_keywords", "keyword_overlap", "missing_keywords", "metrics_found"]
    interesting_pairs = [(key, extracted.get(key)) for key in interesting_keys if extracted.get(key)]
    if interesting_pairs:
        lines.extend(["", "## Extracted Signals"])
        for key, value in interesting_pairs:
            if isinstance(value, list):
                rendered = ", ".join(str(item) for item in value[:12])
            else:
                rendered = str(value)
            lines.append(f"- `{key}`: {rendered}")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score resumes, project blurbs, and job descriptions.",
    )
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument("--input-file", help="Path to the primary text file.")
    target_group.add_argument("--text", help="Primary text content provided inline.")
    parser.add_argument(
        "--kind",
        choices=["auto", "resume", "project", "jd"],
        default="auto",
        help="Force the scorer to treat the input as a resume, project, or JD.",
    )
    jd_group = parser.add_mutually_exclusive_group()
    jd_group.add_argument("--jd-file", help="Optional JD file for fit scoring.")
    jd_group.add_argument("--jd-text", help="Optional JD content provided inline.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        primary_text = _read_optional_text(args.input_file, args.text)
        jd_text = _read_optional_text(args.jd_file, args.jd_text)
    except ValueError as error:
        parser.error(str(error))

    result = evaluate_text(primary_text or "", kind=args.kind, jd_text=jd_text)
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(_format_markdown(result))
    return 0
