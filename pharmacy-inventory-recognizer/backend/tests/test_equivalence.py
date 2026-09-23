"""
CCAUTOMA Tester / QA - equivalence of representations
====================================================
Objective 4 of the brief: show that the Regular Expression, the NFA, the
DFA from subset construction, and the minimized DFA all describe the SAME
language. We check this exhaustively: every string over Sigma (plus a few
symbols outside Sigma) up to length 5 is run through all four and they must
agree on every single one.

Run from the `backend/` folder:  pytest -v   (or: python -m tests.test_equivalence)
"""
from __future__ import annotations

import itertools
import re

from app.automata import construction as cons
from app.automata import definitions as d
from app.automata.dfa import run

# Letters plus two representative digits keeps the search fast; all digits
# behave identically, so this covers every path through the machines.
SYMBOLS = ["M", "S", "C", "0", "7", "m", "X", " "]
MAX_LEN = 5
REGEX = re.compile(d.REGEX_PRACTICAL)


def _subset_dfa_accepts(dfa: cons.SubsetDFA, text: str) -> bool:
    state = dfa.start
    for ch in text:
        if ch not in d.ALPHABET:
            return False
        col = "D" if ch in d.DIGITS else ch
        state = dfa.delta[state][col]
    return state in dfa.accepting


def _all_strings():
    for n in range(MAX_LEN + 1):
        for tup in itertools.product(SYMBOLS, repeat=n):
            yield "".join(tup)


def test_minimized_dfa_is_rebuilt_from_nfa():
    m = cons.minimize(cons.subset_construction())
    assert cons.matches_hand_written_dfa(m)


def test_state_counts():
    dfa = cons.subset_construction()
    m = cons.minimize(dfa)
    assert len(cons.NFA_STATES) == 8
    assert len(dfa.delta) == 8          # T0..T6 + dead
    assert len(m.delta) == 6            # q0..q4 + qDead
    assert m.unreachable == []


def test_re_nfa_dfa_mindfa_agree_on_every_string():
    dfa = cons.subset_construction()
    checked = 0
    for s in _all_strings():
        by_re = REGEX.fullmatch(s) is not None
        by_nfa = cons.nfa_accepts(s)
        by_dfa = _subset_dfa_accepts(dfa, s)
        by_min = run(s).accepted
        assert by_re == by_nfa == by_dfa == by_min, f"disagreement on {s!r}"
        checked += 1
    assert checked > 30_000


def test_theory_report_for_web_page():
    # The data behind the web app's Automata Theory page.
    r = cons.theory_report()
    assert r["counts"] == {"nfa": 8, "dfa": 8, "min": 6}
    assert r["matches_simulator"] is True
    assert len(r["subset"]["steps"]) == 8 * 4          # 8 DFA states x 4 columns
    assert r["minimization"]["merged"] == [["T1", "T2", "T3"]]


def test_language_size_is_3000():
    # |L| = 3 letters x 10 x 10 x 10 digits
    count = sum(
        run(a + "".join(ds)).accepted
        for a in d.LETTERS
        for ds in itertools.product(d.DIGITS, repeat=3)
    )
    assert count == 3000


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
