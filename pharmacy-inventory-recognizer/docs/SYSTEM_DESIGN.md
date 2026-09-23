# System Design

## 1. Overview

PharmaHub has two connected parts:

1. **The automata core** (the graded part): a minimized DFA that decides whether a pharmacy product code is ACCEPTED or REJECTED.
2. **The inventory system**: a web app for medicines, categories, suppliers, orders and stock. It uses the automata core as a gatekeeper, so no product can be saved with an invalid code.

The DFA is defined once, in `backend/app/automata/definitions.py`. The command-line simulator, the REST API and the inventory service all import that same definition, so they cannot disagree. The web front end has a small TypeScript copy (`frontend/src/lib/dfa.ts`) so the recognizer screen can animate instantly without a server round trip. It uses the same states and transitions.

## 2. Architecture

```
            ┌────────────────────────────┐
 User ───▶  │  CLI simulator             │  cli/simulator.py
            │  (interactive / demo /     │
            │   theory modes)            │
            └──────────────┬─────────────┘
                           │ imports
            ┌──────────────▼─────────────┐
            │  Automata core             │  backend/app/automata/
            │  definitions.py  (Σ, δ, F) │  ← single source of truth
            │  dfa.py          (runner)  │
            │  recognizer.py   (reasons) │
            │  construction.py (NFA →    │
            │    DFA → minimized DFA)    │
            └──────▲───────────────▲─────┘
                   │               │
     ┌─────────────┴───┐   ┌───────┴──────────────┐
     │ /api/recognizer │   │ ProductService        │
     │  /validate      │   │ checks every SKU with │
     │  /info, /theory │   │ the DFA before saving │
     └────────▲────────┘   └───────▲──────────────┘
              │ HTTP (FastAPI)     │
     ┌────────┴────────────────────┴───────────────┐
     │  React front end (Vite)                     │
     │  Code Recognizer · Automata Theory ·        │
     │  Medicines · Dashboard · Orders · ...       │
     └─────────────────────────────────────────────┘
                           │
                   SQLite / PostgreSQL
```

## 3. Processing an input string

1. The user types a code, for example `M001`.
2. The runner starts in `q0`.
3. For each symbol, it checks whether the symbol is in Σ. A symbol outside Σ sends the machine to `qDead`.
4. Otherwise it applies δ(state, symbol) and records the step (`q0 --M--> q1`).
5. After the last symbol, it reports the final state.
6. If the final state is `q4`, the verdict is **ACCEPTED**. Otherwise it is **REJECTED**, with a reason pointing at the first place the input broke the pattern.

## 4. Where the DFA is used

| Place | File | What happens |
|---|---|---|
| CLI simulator | `cli/simulator.py` | Interactive, batch, `--demo` (20 cases) and `--theory` (NFA → DFA → minimized DFA) modes |
| REST API | `backend/app/api/routes/recognizer.py` | `POST /api/recognizer/validate` returns verdict, final state and trace. `GET /api/recognizer/info` returns the RE, Σ and transition table |
| Inventory rules | `backend/app/services/product_service.py` | Adding or editing a medicine runs the DFA. Invalid codes are refused |
| Automata Theory screen | `frontend/src/pages/TheoryPage.tsx` + `GET /api/recognizer/theory` | Shows the ε-NFA, steps through subset construction and minimization, and confirms the result matches the recognizer's DFA. The data is computed live by `construction.py` |
| Recognizer screen | `frontend/src/pages/RecognizerPage.tsx` | Animates the state chain and shows each transition. Input is checked exactly as typed |
| Medicines form | `frontend/src/pages/MedicinesPage.tsx` | Live check while typing |

**Note on the Medicines form:** before validating, the inventory form trims spaces and converts the code to uppercase, so a user typing `m001` saves `M001`. This is input preprocessing done by the application before the automaton runs. It does not change the language L. The Code Recognizer screen and the CLI simulator do no preprocessing, so they show the pure automaton behaviour (`m001` is rejected).

## 5. Technology

| Layer | Technology |
|---|---|
| Automata core and simulator | Python 3.11 (standard library only) |
| API | FastAPI, Pydantic |
| Database | SQLAlchemy, SQLite by default, PostgreSQL optional |
| Front end | React + TypeScript, built with Vite |
| Tests | pytest |
| Diagrams | Graphviz, generated from code by `docs/diagrams/make_diagrams.py` |

## 6. Scope and limitations

- The recognizer validates the **format** of a code only. It does not check whether the code already exists; the inventory service does that separately with a database lookup.
- The language allows exactly 3 digits, so each category holds at most 1,000 codes (000–999). Supporting more would mean changing the language, for example to 4 digits.
- Only three categories are supported (M, S, C). Adding one means adding a letter to Σ and one transition from `q0`.
- Lowercase letters are not in Σ. The inventory form uppercases input for convenience, but the automaton itself treats them as invalid.
