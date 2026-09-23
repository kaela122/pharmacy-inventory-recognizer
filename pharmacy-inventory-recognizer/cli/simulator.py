#!/usr/bin/env python3
"""
CCAUTOMA - Pharmacy Product-Code Recognizer :: Working Automata Simulator
======================================================================
A simple, dependency-free program that simulates the MINIMIZED DFA.

It satisfies every "Required Program Feature" from the CCAUTOMA brief:
  [x] Accept user input
  [x] Validate whether symbols belong to the alphabet
  [x] Process the input symbol by symbol
  [x] Display the state transitions
  [x] Identify the final state reached
  [x] Display ACCEPTED or REJECTED
  [x] Allow multiple test cases

Run it:
    python simulator.py            # interactive mode
    python simulator.py M001 S250  # batch mode (validate given codes)
    python simulator.py --demo     # run the built-in accepted/rejected sets
    python simulator.py --theory   # show NFA -> subset construction -> minimization

No third-party libraries are required (Python 3.9+).
"""

from __future__ import annotations

import os
import sys

# --- Make the shared automaton importable, so the simulator, the API, and
#     the documentation all run the exact same machine (single source of truth).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.join(_THIS_DIR, "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND_DIR))

from app.automata import definitions as d       # noqa: E402
from app.automata.dfa import run                 # noqa: E402
from app.automata.recognizer import recognize    # noqa: E402
from app.automata import construction as cons    # noqa: E402


# ---------------------------------------------------------------------------
# Pretty printing helpers
# ---------------------------------------------------------------------------
LINE = "=" * 64


def print_header() -> None:
    print(LINE)
    print(" PHARMACY PRODUCT-CODE RECOGNIZER  -  DFA SIMULATOR (CCAUTOMA)")
    print(LINE)
    print(f" Regular Expression : {d.REGEX}")
    print(f" Alphabet (Sigma)   : {{ {', '.join(sorted(d.ALPHABET))} }}")
    print(" Valid code shape   : <letter M|S|C><digit><digit><digit>   e.g. M001")
    print(LINE)


def print_transition_table() -> None:
    print("\nMinimized DFA transition table")
    print("-" * 56)
    print(f"{'state':<8}{'M':<8}{'S':<8}{'C':<8}{'0-9':<8}{'note'}")
    print("-" * 56)
    for state in d.STATES:
        note = d.STATE_MEANING[state].split(" - ")[0]
        print(
            f"{state:<8}{d.step(state, 'M'):<8}{d.step(state, 'S'):<8}"
            f"{d.step(state, 'C'):<8}{d.step(state, '0'):<8}{note}"
        )
    print("-" * 56)
    print(f"start state    : {d.START_STATE}")
    print(f"accepting state: {', '.join(sorted(d.ACCEPTING_STATES))}")


def simulate(code: str) -> bool:
    """Run one code through the DFA and print the full trace + verdict."""
    result = run(code)
    recog = recognize(code)

    print(f"\nInput: {code!r}   (length {len(code)})")

    if not code:
        print("  (no symbols to process)")
    else:
        print("  Step-by-step processing:")
        for step in result.steps:
            flag = "" if step.in_alphabet else "  <-- not in alphabet"
            print(
                f"    [{step.index}] read {step.symbol!r:>4} : "
                f"{step.from_state} -> {step.to_state}{flag}"
            )

    print(f"  Final state : {result.final_state}")
    print(f"  Reason      : {recog.reason}")
    print(f"  VERDICT     : {result.verdict}")
    if result.accepted:
        print(f"  Decoded     : category={recog.category}, item={recog.item_number}")
    return result.accepted


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------
ACCEPTED_SAMPLES = ["M001", "M123", "S001", "S002", "C001",
                    "C002", "M999", "S250", "C500", "M042"]
REJECTED_SAMPLES = ["M01", "C0012", "A123", "123", "MM123",
                    "C12A", "", "m123", "S12", "S1234"]


def run_demo() -> None:
    print_header()
    print_transition_table()

    print("\n\n### EXPECTED-ACCEPTED SET " + "#" * 37)
    ok = sum(simulate(c) for c in ACCEPTED_SAMPLES)
    print(f"\n  --> {ok}/{len(ACCEPTED_SAMPLES)} accepted (expected all).")

    print("\n\n### EXPECTED-REJECTED SET " + "#" * 37)
    bad = sum(1 for c in REJECTED_SAMPLES if not simulate(c))
    print(f"\n  --> {bad}/{len(REJECTED_SAMPLES)} rejected (expected all).")

    print(f"\n{LINE}")
    passed = ok == len(ACCEPTED_SAMPLES) and bad == len(REJECTED_SAMPLES)
    print(" DEMO RESULT:", "ALL CORRECT" if passed else "MISMATCH - CHECK DFA")
    print(LINE)


def run_theory() -> None:
    """Rebuild the minimized DFA from the NFA and show every step."""
    print_header()
    print("\n[1] epsilon-NFA  M = (Q, Sigma, delta, p0, F)")
    print(f"    Q = {{{', '.join(cons.NFA_STATES)}}}   start = {cons.NFA_START}"
          f"   F = {{{', '.join(sorted(cons.NFA_ACCEPT))}}}")
    print(f"    {'state':<7}{'M':<8}{'S':<8}{'C':<8}{'D':<8}{'eps':<8}meaning")
    for q in cons.NFA_STATES:
        row = cons.NFA_DELTA[q]
        cell = lambda sym: cons.fmt(frozenset(row.get(sym, set())))  # noqa: E731
        print(f"    {q:<7}{cell('M'):<8}{cell('S'):<8}{cell('C'):<8}"
              f"{cell('0'):<8}{cell(cons.EPS):<8}{cons.NFA_MEANING[q]}")

    dfa = cons.subset_construction()
    print("\n[2] Subset construction (NFA -> DFA)")
    for line in dfa.log:
        print("    " + line)
    print(f"\n    Reachable DFA states: {len(dfa.delta)}  "
          f"(out of 2^{len(cons.NFA_STATES)} = {2 ** len(cons.NFA_STATES)} possible subsets)")
    print(f"    Accepting: {', '.join(sorted(dfa.accepting))} (subsets containing p7)")

    m = cons.minimize(dfa)
    print("\n[3] Minimization (partition refinement)")
    print(f"    Unreachable states removed: {m.unreachable or 'none'}")
    for i, part in enumerate(m.rounds):
        blocks = "  ".join("{" + ", ".join(sorted(b)) + "}" for b in part)
        print(f"    P{i}: {blocks}")
    merged = [sorted(b) for b in m.blocks if len(b) > 1]
    print(f"    Merged (equivalent) states: {merged}")
    print(f"    Renaming: {', '.join(f'{k}->{v}' for k, v in m.rename.items())}")
    print(f"\n    States: NFA {len(cons.NFA_STATES)}  |  DFA {len(dfa.delta)}"
          f"  |  minimized DFA {len(m.delta)}")
    ok = cons.matches_hand_written_dfa(m)
    print("    Computed minimized DFA == DFA used by the simulator:",
          "YES" if ok else "NO - CHECK definitions.py")


def run_batch(codes: list[str]) -> None:
    print_header()
    for c in codes:
        simulate(c)


def run_interactive() -> None:
    print_header()
    print_transition_table()
    print("\nType a code to validate. Commands: 'table', 'demo', 'theory', 'quit'.\n")
    while True:
        try:
            raw = input("code> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        cmd = raw.lower()
        if cmd in {"quit", "exit", "q"}:
            print("Goodbye.")
            break
        if cmd == "table":
            print_transition_table()
            continue
        if cmd == "demo":
            run_demo()
            continue
        if cmd == "theory":
            run_theory()
            continue
        # Treat the raw text (case preserved) as a code to validate.
        simulate(raw)


def main(argv: list[str]) -> None:
    args = argv[1:]
    if not args:
        run_interactive()
    elif args[0] in {"--demo", "-d", "demo"}:
        run_demo()
    elif args[0] in {"--theory", "-t", "theory"}:
        run_theory()
    elif args[0] in {"--help", "-h", "help"}:
        print(__doc__)
    else:
        run_batch(args)


if __name__ == "__main__":
    # The theory output uses ε, δ and ∅; make sure Windows consoles print them.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    main(sys.argv)
