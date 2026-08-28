from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Issue


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    """Small dependency-free client for the GitHub Issues REST API."""

    def __init__(self, token: str):
        self.token = token

    def _request(self, method: str, path: str, payload: dict | None = None):
        url = f"https://api.github.com/{path.lstrip('/')}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "IssuePilot/0.1",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubError(f"GitHub API returned {exc.code}: {detail[:500]}") from exc
        except URLError as exc:
            raise GitHubError(f"Could not reach GitHub: {exc.reason}") from exc

    def list_open_issues(self, repository: str, limit: int = 50) -> list[Issue]:
        params = urlencode({"state": "open", "per_page": min(limit, 100)})
        data = self._request("GET", f"repos/{repository}/issues?{params}")
        issues: list[Issue] = []
        for item in data:
            # Pull requests are returned by the Issues endpoint too.
            if "pull_request" in item:
                continue
            issues.append(
                Issue(
                    number=int(item["number"]),
                    title=item.get("title", ""),
                    body=item.get("body") or "",
                    labels=[x["name"] for x in item.get("labels", []) if x.get("name")],
                    url=item.get("html_url", ""),
                )
            )
        return issues[:limit]

    def add_labels(self, repository: str, issue_number: int, labels: list[str]) -> None:
        if not labels:
            return
        self._request(
            "POST",
            f"repos/{repository}/issues/{issue_number}/labels",
            {"labels": labels},
        )

    def comment(self, repository: str, issue_number: int, body: str) -> None:
        self._request(
            "POST",
            f"repos/{repository}/issues/{issue_number}/comments",
            {"body": body},
        )
