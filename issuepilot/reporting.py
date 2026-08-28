from __future__ import annotations

import json

from .models import Issue, TriageResult


def print_report(repository: str, results: list[tuple[Issue, TriageResult]], dry_run: bool) -> None:
    print("IssuePilot")
    print(f"Repository: {repository}")
    print(f"Mode: {'DRY RUN' if dry_run else 'WRITE'}")
    print()
    for issue, result in results:
        duplicates = (
            f" duplicates={','.join('#' + str(x) for x in result.duplicate_candidates)}"
            if result.duplicate_candidates
            else ""
        )
        print(
            f"#{issue.number:<5} [{result.category:<13}] "
            f"{result.priority:<8} {issue.title}{duplicates}"
        )
    print(f"\n{len(results)} issue(s) analyzed.")


def write_json_report(
    path: str,
    repository: str,
    results: list[tuple[Issue, TriageResult]],
) -> None:
    payload = {
        "repository": repository,
        "issues": [
            {
                "number": issue.number,
                "title": issue.title,
                "url": issue.url,
                "triage": result.to_dict(),
            }
            for issue, result in results
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
