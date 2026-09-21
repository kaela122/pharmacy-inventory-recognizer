"""
COM244 Tester / QA
==================
Test cases that verify the minimized DFA behaves exactly as the language
specification requires.

Run from the `backend/` folder:
    pytest -v
or without pytest installed:
    python -m tests.test_recognizer      # falls back to a plain runner
"""

from __future__ import annotations

from app.automata import definitions as d
from app.automata.dfa import run
from app.automata.recognizer import recognize

# The 10 accepted + 10 rejected strings required by the brief.
ACCEPTED = ["M001", "M123", "S001", "S002", "C001",
            "C002", "M999", "S250", "C500", "M042"]

REJECTED = ["M01", "M0012", "A123", "123", "MM123",
            "M12A", "", "m123", "S12", "S1234"]


def test_all_accepted_strings_are_accepted():
    for code in ACCEPTED:
        result = run(code)
        assert result.accepted, f"{code!r} should be ACCEPTED"
        assert result.final_state in d.ACCEPTING_STATES


def test_all_rejected_strings_are_rejected():
    for code in REJECTED:
        result = run(code)
        assert not result.accepted, f"{code!r} should be REJECTED"


def test_symbols_outside_alphabet_are_flagged():
    result = run("m123")            # lowercase m is not in Sigma
    assert not result.accepted
    assert "m" in result.invalid_symbols


def test_wrong_length_is_rejected():
    assert not run("M01").accepted      # too short
    assert not run("M0012").accepted    # too long


def test_trace_length_matches_input_length():
    result = run("M001")
    assert len(result.steps) == len("M001")


def test_recognizer_decodes_valid_codes():
    r = recognize("M042")
    assert r.accepted
    assert r.category == "Medicine"
    assert r.item_number == "042"
    assert recognize("S002").category == "Supplement"

    r = recognize("C001")
    assert r.category == "Consumable"


def test_recognizer_gives_a_reason_when_rejecting():
    r = recognize("A123")
    assert not r.accepted
    assert r.reason  # non-empty explanation


# ---------------------------------------------------------------------------
# Plain runner so this file also works without pytest installed.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {t.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} tests passed.")
    raise SystemExit(1 if failures else 0)
