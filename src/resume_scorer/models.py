from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class DimensionScore:
    name: str
    score: int
    reason: str
    evidence: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationResult:
    input_kind: str
    language: str
    overall_score: int
    summary: str
    dimensions: list[DimensionScore]
    strengths: list[str]
    risks: list[str]
    suggestions: list[str]
    extracted: dict[str, Any]
    fit_score: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_kind": self.input_kind,
            "language": self.language,
            "overall_score": self.overall_score,
            "fit_score": self.fit_score,
            "summary": self.summary,
            "dimensions": [dimension.to_dict() for dimension in self.dimensions],
            "strengths": self.strengths,
            "risks": self.risks,
            "suggestions": self.suggestions,
            "extracted": self.extracted,
        }
