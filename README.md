# IssuePilot

**IssuePilot is an open-source GitHub issue triage and maintenance bot designed to keep repositories organized without requiring a human to manually inspect every new issue.**

IssuePilot can analyze incoming GitHub issues, recommend or apply labels, detect likely duplicates, generate concise summaries, and leave a transparent triage comment. AI analysis is optional: the project can run with a deterministic rule-based classifier when no model provider is configured.

## Why IssuePilot?

Issue queues become difficult to maintain as projects grow. IssuePilot turns the first-pass maintenance work into an explicit, reviewable workflow:

1. Fetch open issues.
2. Ignore pull requests.
3. Build a compact issue representation.
4. Classify the issue into a configurable category.
5. Suggest labels, priority, and duplicate candidates.
6. Optionally post a triage comment and apply labels.
7. Produce a machine-readable report for CI or scheduled runs.

The design goal is **automation with accountability**. Dry-run mode is the default, and every write operation can be disabled independently.

## Features

- GitHub Issues API integration
- Rule-based triage that works without an AI provider
- Optional Anthropic Claude analysis
- Label recommendations for:
  - `bug`
  - `feature`
  - `question`
  - `documentation`
  - `duplicate`
  - `security`
  - `invalid`
- Priority estimation (`low`, `medium`, `high`, `critical`)
- Duplicate-candidate detection using normalized text similarity
- Human-readable triage comments
- Dry-run mode for safe testing
- JSON reports for CI pipelines
- Configurable label names
- GitHub Actions workflow for scheduled/manual runs
- Tests for the core classification and similarity logic

## Quick start

### 1. Install

```bash
git clone https://github.com/HJOGRDSJKHFSe1324-dot/IssuePilot.git
cd IssuePilot

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Configure GitHub access

Create a GitHub token with the minimum repository permissions required for your repository's issue operations.

```bash
set GITHUB_TOKEN=ghp_your_token
```

Linux/macOS:

```bash
export GITHUB_TOKEN=ghp_your_token
```

### 3. Run a dry-run triage

```bash
issuepilot owner/repository --limit 25
```

Example output:

```text
IssuePilot
Repository: owner/repository
Mode: DRY RUN

#42  [bug]  high  Login fails after password reset
#41  [question]  low  How do I configure the worker?
#39  [feature]  medium  Add CSV export

3 issue(s) analyzed.
```

### 4. Enable writes

```bash
issuepilot owner/repository --apply-labels --comment
```

Writes are opt-in.

## Optional Claude integration

IssuePilot can use Anthropic Claude for issue classification.

Install the optional dependency:

```bash
pip install -e ".[anthropic]"
```

Then provide:

```bash
export ANTHROPIC_API_KEY=your_key
```

Run:

```bash
issuepilot owner/repository --provider anthropic
```

IssuePilot does not require Claude to operate.

## Configuration

Example environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | — | GitHub authentication |
| `ANTHROPIC_API_KEY` | — | Optional Claude authentication |
| `ISSUEPILOT_PROVIDER` | `rules` | `rules` or `anthropic` |
| `ISSUEPILOT_DUPLICATE_THRESHOLD` | `0.72` | Similarity threshold |
| `ISSUEPILOT_MAX_ISSUES` | `50` | Maximum issues per run |

CLI flags override environment defaults.

## GitHub Action

A workflow is included at `.github/workflows/issuepilot.yml`.

It can be triggered manually or on a schedule. The included workflow starts in dry-run mode so that enabling automation does not immediately modify repository issues.

For a repository where you want IssuePilot to write labels/comments, set the workflow permissions and explicitly add the write flags:

```yaml
permissions:
  issues: write
```

Then:

```yaml
args: "--apply-labels --comment"
```

## Architecture

```text
issuepilot/
├── cli.py              # command-line interface
├── config.py           # configuration loading
├── github.py           # GitHub REST API client
├── models.py           # typed data models
├── similarity.py       # duplicate detection
├── triage.py           # rule-based and provider orchestration
├── providers/
│   ├── base.py         # provider protocol
│   ├── rules.py        # deterministic classifier
│   └── anthropic.py    # optional Claude provider
└── reporting.py        # console/JSON reporting
```

The provider interface intentionally keeps the core independent from any single AI vendor.

## Safety model

IssuePilot is built around conservative automation:

- **Dry-run by default**
- **Writes are opt-in**
- Credentials are read from environment variables
- AI output is parsed into a constrained schema
- Labels are allow-listed through configuration
- Duplicate detection produces candidates rather than silently closing issues
- API failures are reported instead of being silently ignored

IssuePilot does not automatically close issues, delete comments, or merge pull requests.

## Development

Run the test suite:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Build the package:

```bash
python -m build
```

## Contributing

Contributions are welcome. Start with an issue describing the proposed change, then open a focused pull request with tests where practical.

See:

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`

## License

MIT. See `LICENSE`.
