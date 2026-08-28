from __future__ import annotations

import argparse
import os
import sys

from .config import Config
from .github import GitHubClient, GitHubError
from .reporting import print_report, write_json_report
from .triage import AnthropicProvider, RuleProvider, build_comment, triage_issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="issuepilot",
        description="Triage and maintain GitHub issues safely.",
    )
    parser.add_argument("repository", help="GitHub repository, e.g. owner/repo")
    parser.add_argument("--limit", type=int, default=None, help="Maximum issues to analyze")
    parser.add_argument(
        "--provider",
        choices=("rules", "anthropic"),
        default=None,
        help="Analysis provider",
    )
    parser.add_argument("--apply-labels", action="store_true", help="Apply recommended labels")
    parser.add_argument("--comment", action="store_true", help="Post triage comments")
    parser.add_argument("--report", help="Write JSON report to this path")
    parser.add_argument(
        "--no-duplicates",
        action="store_true",
        help="Skip duplicate candidate detection",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        config = Config.from_env()
        provider_name = args.provider or config.provider
        limit = args.limit or config.max_issues
        if limit < 1:
            raise ValueError("--limit must be at least 1.")

        github = GitHubClient(config.github_token)
        issues = github.list_open_issues(args.repository, limit=limit)

        if provider_name == "anthropic":
            if not config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is required for the anthropic provider.")
            provider = AnthropicProvider(config.anthropic_api_key)
        else:
            provider = RuleProvider()

        results = triage_issues(
            issues,
            provider,
            1.0 if args.no_duplicates else config.duplicate_threshold,
        )

        print_report(
            args.repository,
            results,
            dry_run=not (args.apply_labels or args.comment),
        )

        if args.report:
            write_json_report(args.report, args.repository, results)
            print(f"JSON report written to {args.report}")

        if args.apply_labels or args.comment:
            for issue, result in results:
                if args.apply_labels:
                    github.add_labels(args.repository, issue.number, result.labels)
                if args.comment:
                    github.comment(args.repository, issue.number, build_comment(result))
            print("Write operations completed.")

        return 0

    except (ValueError, GitHubError, RuntimeError) as exc:
        print(f"IssuePilot error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
