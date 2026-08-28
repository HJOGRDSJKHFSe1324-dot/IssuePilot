from __future__ import annotations

import re
from collections import Counter
from math import sqrt


def normalize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    stopwords = {
        "the", "and", "for", "with", "this", "that", "from", "have", "has",
        "issue", "please", "when", "into", "after", "before", "what", "how",
    }
    return [w for w in words if w not in stopwords and len(w) > 2]


def cosine_similarity(a: str, b: str) -> float:
    left = Counter(normalize(a))
    right = Counter(normalize(b))
    if not left or not right:
        return 0.0
    keys = set(left) | set(right)
    dot = sum(left[k] * right[k] for k in keys)
    left_norm = sqrt(sum(v * v for v in left.values()))
    right_norm = sqrt(sum(v * v for v in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return min(1.0, dot / (left_norm * right_norm))


def duplicate_candidates(
    title: str,
    body: str,
    issues: list,
    threshold: float,
    current_number: int,
    max_candidates: int = 3,
) -> list[int]:
    text = f"{title}\n{body}"
    scored: list[tuple[float, int]] = []
    for issue in issues:
        if issue.number == current_number:
            continue
        score = cosine_similarity(text, f"{issue.title}\n{issue.body}")
        if score >= threshold:
            scored.append((score, issue.number))
    scored.sort(reverse=True)
    return [number for _, number in scored[:max_candidates]]
