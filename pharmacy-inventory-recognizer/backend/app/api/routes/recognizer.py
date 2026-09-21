"""COM244 recognizer endpoints -- the automata core exposed over HTTP.
These endpoints need no database, so they run out of the box."""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.recognizer import (AutomatonInfo, RecognizeRequest,
                                     RecognizeResponse)
from app.services import recognizer_service

router = APIRouter(prefix="/recognizer", tags=["recognizer"])


@router.get("/info", response_model=AutomatonInfo)
def get_automaton_info():
    """Return the RE, alphabet, states and DFA transition table."""
    return recognizer_service.automaton_info()


@router.post("/validate", response_model=RecognizeResponse)
def validate_code(payload: RecognizeRequest):
    """Validate one code and return the verdict + full transition trace."""
    return recognizer_service.recognize_code(payload.code)
