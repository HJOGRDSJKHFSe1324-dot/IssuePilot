# Design Notes

## Core principle

IssuePilot should be useful even without an AI API key.

The deterministic provider provides a predictable baseline that can be tested locally. AI providers are adapters layered above that baseline.

## Why duplicate detection is advisory

A similarity score is not proof that two issues are duplicates. The bot therefore reports candidates and can label them, but never automatically closes an issue.

## Why writes are opt-in

An issue-management bot has a larger blast radius than a local CLI. Dry-run is therefore the default, and labels/comments must be explicitly requested.

## Provider interface

Providers implement:

```python
analyze(issue: Issue) -> TriageResult
```

This makes it possible to add other model providers or a custom classifier without modifying GitHub integration code.
