from issuepilot.models import Issue
from issuepilot.similarity import cosine_similarity, duplicate_candidates


def test_identical_text_scores_one():
    assert cosine_similarity("login crashes after reset", "login crashes after reset") == 1.0


def test_unrelated_text_has_low_similarity():
    assert cosine_similarity("database migration", "custom logo request") < 0.3


def test_duplicate_candidates():
    issues = [
        Issue(1, "Login crashes after password reset", "Users get a crash after resetting passwords."),
        Issue(2, "Add CSV export", "Please export users as CSV."),
        Issue(3, "Password reset crash", "Crash happens immediately after a password reset."),
    ]
    result = duplicate_candidates(
        issues[0].title,
        issues[0].body,
        issues,
        threshold=0.35,
        current_number=1,
    )
    assert 3 in result
