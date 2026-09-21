"""Pydantic schemas for the code-recognizer endpoint."""
from __future__ import annotations
from pydantic import BaseModel


class RecognizeRequest(BaseModel):
    code: str


class RecognizeResponse(BaseModel):
    code: str
    verdict: str            # "ACCEPTED" | "REJECTED"
    accepted: bool
    final_state: str
    reason: str
    category: str | None = None
    item_number: str | None = None
    trace: list[str] = []


class AutomatonInfo(BaseModel):
    regex: str
    alphabet: list[str]
    states: list[str]
    start_state: str
    accepting_states: list[str]
    transition_table: list[dict]
