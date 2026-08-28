from issuepilot.models import Issue
from issuepilot.triage import RuleProvider, build_comment, triage_issues


def test_rule_provider_detects_security():
    issue = Issue(10, "Possible vulnerability in auth", "There may be a credential leak.")
    result = RuleProvider().analyze(issue)
    assert result.category == "security"
    assert result.priority == "critical"
    assert "security" in result.labels


def test_rule_provider_detects_feature():
    issue = Issue(11, "Add dark mode", "It would be nice to support a dark UI.")
    result = RuleProvider().analyze(issue)
    assert result.category == "feature"
    assert result.priority == "medium"


def test_comment_contains_core_fields():
    issue = Issue(12, "How do I install?", "Question about installation.")
    result = RuleProvider().analyze(issue)
    comment = build_comment(result)
    assert "IssuePilot triage" in comment
    assert "Category" in comment
    assert "Priority" in comment


def test_trio_adds_duplicate_label():
    issues = [
        Issue(20, "Crash on startup", "Application crashes on startup."),
        Issue(21, "Startup crash", "Application crashes on startup."),
    ]
    output = triage_issues(issues, RuleProvider(), threshold=0.4)
    assert "duplicate" in output[0][1].labels
