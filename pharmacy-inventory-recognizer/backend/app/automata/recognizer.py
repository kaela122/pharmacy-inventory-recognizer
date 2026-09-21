"""
recognizer.py
=============
Domain layer on top of the generic DFA engine. Turns a raw ACCEPTED/REJECTED
verdict into something the inventory system can use: a reason, and (for valid
codes) the decoded meaning of the pharmacy product code.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import definitions as d
from .dfa import RunResult, run

CATEGORY_NAMES = {"M": "Medicine", "S": "Supplement", "C": "Consumable"}


@dataclass
class RecognitionResult:
    code: str
    accepted: bool
    final_state: str
    reason: str
    category: str | None = None          # Medicine / Supplement / Consumable
    item_number: str | None = None       # the 3-digit part if valid
    trace: list[str] = None              # human-readable transition list

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "verdict": "ACCEPTED" if self.accepted else "REJECTED",
            "accepted": self.accepted,
            "final_state": self.final_state,
            "reason": self.reason,
            "category": self.category,
            "item_number": self.item_number,
            "trace": self.trace or [],
        }


def _explain_rejection(result: RunResult) -> str:
    """Produce a friendly reason for why a code was rejected."""
    if result.invalid_symbols:
        bad = ", ".join(repr(s) for s in result.invalid_symbols)
        return f"contains symbol(s) not in the alphabet: {bad}"

    length = len(result.input_string)
    if length == 0:
        return "empty input - a code must be a letter followed by 3 digits"
    if length < 4:
        return f"too short ({length} symbols) - expected exactly 4"
    if length > 4:
        return f"too long ({length} symbols) - expected exactly 4"
    # Correct length, valid symbols, but still rejected -> wrong shape.
    first = result.input_string[0]
    if first not in d.LETTERS:
        return "first symbol must be a category letter (M, S or C)"
    return "digits are misplaced - format must be <letter><digit><digit><digit>"


def recognize(code: str) -> RecognitionResult:
    """
    Validate a pharmacy product code with the minimized DFA and decode it.
    """
    result = run(code)
    trace = [s.as_text() for s in result.steps]

    if result.accepted:
        letter = code[0]
        return RecognitionResult(
            code=code,
            accepted=True,
            final_state=result.final_state,
            reason=f"valid {CATEGORY_NAMES[letter]} code",
            category=CATEGORY_NAMES[letter],
            item_number=code[1:],
            trace=trace,
        )

    return RecognitionResult(
        code=code,
        accepted=False,
        final_state=result.final_state,
        reason=_explain_rejection(result),
        trace=trace,
    )
