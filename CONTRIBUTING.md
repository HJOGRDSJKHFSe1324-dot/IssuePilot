# Contributing to IssuePilot

Thanks for contributing.

## Development setup

```bash
python -m venv .venv
pip install -e ".[dev]"
pytest
ruff check .
```

## Pull requests

Keep pull requests focused and explain:

- what changed
- why it changed
- how it was tested

New behavior should have tests when practical.

## Design principles

IssuePilot favors:

1. Safe defaults.
2. Small, testable components.
3. Vendor-neutral core interfaces.
4. Transparent automation.
5. Backward-compatible configuration where possible.
