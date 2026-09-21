"""
dfa.py
======
A tiny, generic DFA engine. It knows nothing about pharmacy codes; it just
runs whatever transition function it is given, symbol by symbol, and records
the trace of state transitions.

This directly satisfies the COM244 "Required Program Features":
  * process the input symbol by symbol
  * display the state transitions
  * identify the final state reached
  * decide ACCEPTED / REJECTED
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import definitions as d


@dataclass
class TransitionStep:
    """One symbol consumed: from_state --symbol--> to_state."""

    index: int          # position of the symbol in the input (0-based)
    symbol: str         # the actual character read
    from_state: str
    to_state: str
    in_alphabet: bool   # was the symbol part of Sigma?

    def as_text(self) -> str:
        arrow = f"{self.from_state} --{self.symbol}--> {self.to_state}"
        if not self.in_alphabet:
            arrow += "   (symbol NOT in alphabet)"
        return arrow


@dataclass
class RunResult:
    """The full outcome of running one input string through the DFA."""

    input_string: str
    accepted: bool
    final_state: str
    steps: list[TransitionStep] = field(default_factory=list)
    invalid_symbols: list[str] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "ACCEPTED" if self.accepted else "REJECTED"


def run(input_string: str) -> RunResult:
    """
    Feed `input_string` to the minimized DFA one symbol at a time.

    Returns a RunResult holding the verdict, the final state, and the
    complete transition trace.
    """
    state = d.START_STATE
    steps: list[TransitionStep] = []
    invalid: list[str] = []

    for i, ch in enumerate(input_string):
        in_alphabet = ch in d.ALPHABET
        if not in_alphabet and ch not in invalid:
            invalid.append(ch)
        next_state = d.step(state, ch)
        steps.append(
            TransitionStep(
                index=i,
                symbol=ch,
                from_state=state,
                to_state=next_state,
                in_alphabet=in_alphabet,
            )
        )
        state = next_state

    return RunResult(
        input_string=input_string,
        accepted=d.is_accepting(state),
        final_state=state,
        steps=steps,
        invalid_symbols=invalid,
    )


def transition_table() -> list[dict[str, str]]:
    """
    Return the DFA transition table as a list of row dicts, ready to print
    or serialize to JSON. Columns are M, S, 0-9 (the digit class).
    """
    rows = []
    for state in d.STATES:
        row = {"state": state}
        row["M"] = d.step(state, "M")
        row["S"] = d.step(state, "S")
        row["0-9"] = d.step(state, "0")  # any digit represents the class
        row["type"] = (
            "start+accept"
            if state == d.START_STATE and d.is_accepting(state)
            else "start"
            if state == d.START_STATE
            else "accept"
            if d.is_accepting(state)
            else "dead"
            if state == d.DEAD_STATE
            else "normal"
        )
        rows.append(row)
    return rows
