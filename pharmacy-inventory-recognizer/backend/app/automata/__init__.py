"""Automata package: RE -> NFA -> DFA -> minimized DFA recognizer."""

from .dfa import RunResult, TransitionStep, run, transition_table
from .recognizer import RecognitionResult, recognize

__all__ = [
    "run",
    "transition_table",
    "recognize",
    "RunResult",
    "TransitionStep",
    "RecognitionResult",
]
