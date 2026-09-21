"""
Formal-language definitions for the pharmacy product-code recognizer (COM244).
Single source of truth: the CLI simulator, the API, and the docs all use this.

Language: one category letter then exactly three digits.
    M = Medicine, S = Supplement, C = Consumable
    e.g. M001, S002, C001

Regular expression:  (M|S|C)(0-9)(0-9)(0-9)
Alphabet (Sigma):    { M, S, C, 0..9 }
"""
from __future__ import annotations

LETTERS = ("M", "S", "C")
DIGITS = tuple("0123456789")
ALPHABET = frozenset(LETTERS + DIGITS)

REGEX = "(M|S|C)(0-9)(0-9)(0-9)"
TABLE_COLUMNS = ("M", "S", "C", "0-9")

# Minimized DFA: q0 -letter-> q1 -digit-> q2 -digit-> q3 -digit-> q4 (accept)
START_STATE = "q0"
DEAD_STATE = "qDead"
ACCEPTING_STATES = frozenset({"q4"})
STATES = ("q0", "q1", "q2", "q3", "q4", DEAD_STATE)

STATE_MEANING = {
    "q0": "start - waiting for a category letter (M, S or C)",
    "q1": "letter read - waiting for digit 1 of 3",
    "q2": "1 digit read - waiting for digit 2 of 3",
    "q3": "2 digits read - waiting for digit 3 of 3",
    "q4": "3 digits read - VALID CODE (accepting)",
    DEAD_STATE: "trap - input can never be accepted from here",
}


def _digits_to(target):
    return {d: target for d in DIGITS}


DELTA = {
    "q0": {"M": "q1", "S": "q1", "C": "q1", **_digits_to(DEAD_STATE)},
    "q1": {"M": DEAD_STATE, "S": DEAD_STATE, "C": DEAD_STATE, **_digits_to("q2")},
    "q2": {"M": DEAD_STATE, "S": DEAD_STATE, "C": DEAD_STATE, **_digits_to("q3")},
    "q3": {"M": DEAD_STATE, "S": DEAD_STATE, "C": DEAD_STATE, **_digits_to("q4")},
    "q4": {"M": DEAD_STATE, "S": DEAD_STATE, "C": DEAD_STATE, **_digits_to(DEAD_STATE)},
    DEAD_STATE: {"M": DEAD_STATE, "S": DEAD_STATE, "C": DEAD_STATE, **_digits_to(DEAD_STATE)},
}


def symbol_class(symbol):
    return "0-9" if symbol in DIGITS else symbol


def step(state, symbol):
    if symbol not in ALPHABET:
        return DEAD_STATE
    return DELTA.get(state, {}).get(symbol, DEAD_STATE)


def is_accepting(state):
    return state in ACCEPTING_STATES
