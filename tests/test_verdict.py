"""Tests for verdict logic."""
from evidenza.proof.verdict import compute_verdict


def test_all_passed_returns_ship():
    criteria = [
        {"status": "passed"},
        {"status": "passed"},
        {"status": "passed"},
    ]
    assert compute_verdict(criteria) == "SHIP"


def test_any_failed_returns_blocked():
    criteria = [
        {"status": "passed"},
        {"status": "failed"},
    ]
    assert compute_verdict(criteria) == "BLOCKED"


def test_any_blocked_returns_blocked():
    criteria = [
        {"status": "passed"},
        {"status": "blocked"},
    ]
    assert compute_verdict(criteria) == "BLOCKED"


def test_manual_review_returns_needs_human():
    criteria = [
        {"status": "passed"},
        {"status": "manual_review"},
    ]
    assert compute_verdict(criteria) == "NEEDS_HUMAN_REVIEW"


def test_pending_returns_needs_human():
    criteria = [
        {"status": "passed"},
        {"status": "pending"},
    ]
    assert compute_verdict(criteria) == "NEEDS_HUMAN_REVIEW"


def test_empty_returns_needs_human():
    assert compute_verdict([]) == "NEEDS_HUMAN_REVIEW"


def test_failed_takes_priority_over_manual_review():
    criteria = [
        {"status": "failed"},
        {"status": "manual_review"},
    ]
    assert compute_verdict(criteria) == "BLOCKED"
