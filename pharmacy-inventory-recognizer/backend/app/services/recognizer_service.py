"""Service layer for the automata recognizer. Wraps the automata package so
the API and the rest of the app never touch the DFA internals directly."""
from __future__ import annotations

from app.automata import definitions as d
from app.automata import recognize, transition_table


def recognize_code(code: str) -> dict:
    return recognize(code).to_dict()


def automaton_info() -> dict:
    return {
        "regex": d.REGEX,
        "alphabet": sorted(d.ALPHABET),
        "states": list(d.STATES),
        "start_state": d.START_STATE,
        "accepting_states": sorted(d.ACCEPTING_STATES),
        "transition_table": transition_table(),
    }
