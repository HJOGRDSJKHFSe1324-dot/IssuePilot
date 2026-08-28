from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Issue:
    number: int
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
    url: str = ""


@dataclass(slots=True)
class TriageResult:
    category: str
    priority: str
    confidence: float
    summary: str
    labels: list[str] = field(default_factory=list)
    duplicate_candidates: list[int] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "priority": self.priority,
            "confidence": round(self.confidence, 3),
            "summary": self.summary,
            "labels": self.labels,
            "duplicate_candidates": self.duplicate_candidates,
            "reason": self.reason,
        }
