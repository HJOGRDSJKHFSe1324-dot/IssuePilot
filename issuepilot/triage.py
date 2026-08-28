from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Protocol

from .models import Issue, TriageResult
from .similarity import duplicate_candidates


class Provider(Protocol):
    def analyze(self, issue: Issue) -> TriageResult: ...


@dataclass(slots=True)
class RuleProvider:
    """Deterministic classifier used by default."""

    def analyze(self, issue: Issue) -> TriageResult:
        text = f"{issue.title}\n{issue.body}".lower()

        security_terms = ("vulnerability", "exploit", "credential", "secret leak", "security")
        bug_terms = ("error", "bug", "crash", "broken", "fails", "failure", "exception", "regression")
        feature_terms = ("feature", "support", "add ", "request", "enhancement", "would be nice")
        docs_terms = ("documentation", "docs", "readme", "typo", "example", "guide")
        question_terms = ("how do i", "how can i", "question", "is it possible", "where do i")

        if any(term in text for term in security_terms):
            category = "security"
            priority = "critical"
            reason = "Security-related language was detected."
        elif any(term in text for term in bug_terms):
            category = "bug"
            priority = "high" if any(x in text for x in ("crash", "data loss", "regression")) else "medium"
            reason = "Bug or failure language was detected."
        elif any(term in text for term in feature_terms):
            category = "feature"
            priority = "medium"
            reason = "Feature-request language was detected."
        elif any(term in text for term in docs_terms):
            category = "documentation"
            priority = "low"
            reason = "Documentation-related language was detected."
        elif any(term in text for term in question_terms):
            category = "question"
            priority = "low"
            reason = "Question/help language was detected."
        else:
            category = "question"
            priority = "low"
            reason = "No strong category signal was detected."

        summary = re.sub(r"\s+", " ", issue.body.strip())[:280]
        if not summary:
            summary = issue.title.strip()[:280]

        labels = [category, f"priority:{priority}"]
        confidence = 0.62 if category == "question" and reason.startswith("No strong") else 0.82

        return TriageResult(
            category=category,
            priority=priority,
            confidence=confidence,
            summary=summary,
            labels=labels,
            reason=reason,
        )


class AnthropicProvider:
    """Optional Claude-backed provider.

    The import is delayed so the main package remains dependency-free.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Anthropic support requires `pip install -e '.[anthropic]'`."
            ) from exc
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze(self, issue: Issue) -> TriageResult:
        prompt = f"""
Analyze this GitHub issue.

TITLE:
{issue.title}

BODY:
{issue.body[:8000]}

Return ONLY valid JSON matching this schema:
{{
  "category": "bug|feature|question|documentation|security|invalid",
  "priority": "low|medium|high|critical",
  "confidence": 0.0,
  "summary": "one concise sentence",
  "labels": ["label", "..."],
  "reason": "brief explanation"
}}
"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(block, "text", "") for block in response.content).strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\\s*|\\s*```$", "", text, flags=re.IGNORECASE)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Claude returned invalid JSON.") from exc

        category = data.get("category", "question")
        priority = data.get("priority", "low")
        allowed_categories = {"bug", "feature", "question", "documentation", "security", "invalid"}
        allowed_priorities = {"low", "medium", "high", "critical"}

        if category not in allowed_categories:
            category = "question"
        if priority not in allowed_priorities:
            priority = "low"

        labels = [str(x) for x in data.get("labels", []) if x]
        if category not in labels:
            labels.insert(0, category)
        priority_label = f"priority:{priority}"
        if priority_label not in labels:
            labels.append(priority_label)

        return TriageResult(
            category=category,
            priority=priority,
            confidence=max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
            summary=str(data.get("summary", issue.title))[:500],
            labels=labels[:8],
            reason=str(data.get("reason", "Claude classification."))[:500],
        )


def triage_issues(
    issues: list[Issue],
    provider: Provider,
    threshold: float,
) -> list[tuple[Issue, TriageResult]]:
    results = []
    for issue in issues:
        result = provider.analyze(issue)
        result.duplicate_candidates = duplicate_candidates(
            issue.title,
            issue.body,
            issues,
            threshold,
            issue.number,
        )
        if result.duplicate_candidates and "duplicate" not in result.labels:
            result.labels.append("duplicate")
        results.append((issue, result))
    return results


def build_comment(result: TriageResult) -> str:
    labels = ", ".join(f"`{x}`" for x in result.labels) or "none"
    duplicates = (
        ", ".join(f"#{x}" for x in result.duplicate_candidates)
        if result.duplicate_candidates
        else "none detected"
    )
    return (
        "### IssuePilot triage\n\n"
        f"**Category:** `{result.category}`  \n"
        f"**Priority:** `{result.priority}`  \n"
        f"**Confidence:** `{result.confidence:.0%}`  \n"
        f"**Summary:** {result.summary}  \n"
        f"**Suggested labels:** {labels}  \n"
        f"**Possible duplicates:** {duplicates}\n\n"
        f"_Reason: {result.reason}_"
    )
