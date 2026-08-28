from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Config:
    github_token: str
    provider: str = "rules"
    anthropic_api_key: str | None = None
    duplicate_threshold: float = 0.72
    max_issues: int = 50

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if not token:
            raise ValueError("GITHUB_TOKEN is required.")

        provider = os.getenv("ISSUEPILOT_PROVIDER", "rules").strip().lower()
        threshold = float(os.getenv("ISSUEPILOT_DUPLICATE_THRESHOLD", "0.72"))
        max_issues = int(os.getenv("ISSUEPILOT_MAX_ISSUES", "50"))

        if provider not in {"rules", "anthropic"}:
            raise ValueError("ISSUEPILOT_PROVIDER must be 'rules' or 'anthropic'.")
        if not 0.0 < threshold <= 1.0:
            raise ValueError("ISSUEPILOT_DUPLICATE_THRESHOLD must be between 0 and 1.")
        if max_issues < 1:
            raise ValueError("ISSUEPILOT_MAX_ISSUES must be at least 1.")

        return cls(
            github_token=token,
            provider=provider,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            duplicate_threshold=threshold,
            max_issues=max_issues,
        )
