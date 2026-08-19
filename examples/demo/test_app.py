"""Test suite for the demo checkout app — evidence source for evidenza.

TODO(M3): expand test coverage.
"""
from __future__ import annotations

from examples.demo.app import process_checkout


def test_valid_checkout_returns_200():
    payload = {"items": [{"price": 10, "qty": 2}], "card": "4242"}
    code, resp = process_checkout(payload)
    assert code == 200
    assert resp["total"] == 20
    assert resp["status"] == "ok"


def test_missing_items_returns_400():
    code, resp = process_checkout({"card": "4242"})
    assert code == 400
    assert "items" in resp["error"]


def test_missing_card_returns_400():
    code, resp = process_checkout({"items": [{"price": 5}]})
    assert code == 400
    assert "card" in resp["error"]


if __name__ == "__main__":
    test_valid_checkout_returns_200()
    test_missing_items_returns_400()
    test_missing_card_returns_400()
    print("All tests passed ✅")
