"""
construction.py
===============
The THEORY side of the project, as runnable code:

    Regular Expression  ->  epsilon-NFA  ->  DFA (subset construction)
                        ->  minimized DFA (partition refinement)

It builds everything from the NFA below and checks that the result is the
same machine as the hand-written minimized DFA in `definitions.py`. That is
how the project demonstrates that the RE, NFA, DFA and minimized DFA are
equivalent representations of one regular language.

The ten digits always behave identically, so tables group them into one
column "D" (D = 0|1|...|9). Internally every digit is still a separate symbol.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import definitions as d

EPS = "ε"

# ---------------------------------------------------------------------------
# 1. The epsilon-NFA, built from   RE = (M|S|C) D D D
#
#    p0 --M--> p1 --ε--+
#    p0 --S--> p2 --ε--+--> p4 --D--> p5 --D--> p6 --D--> p7 (accept)
#    p0 --C--> p3 --ε--+
#
#    p1, p2, p3 are one branch per alternative of (M|S|C); the ε-moves join
#    the branches before the three digits.
# ---------------------------------------------------------------------------
NFA_STATES = ("p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7")
NFA_START = "p0"
NFA_ACCEPT = frozenset({"p7"})

NFA_DELTA: dict[str, dict[str, set[str]]] = {
    "p0": {"M": {"p1"}, "S": {"p2"}, "C": {"p3"}},
    "p1": {EPS: {"p4"}},
    "p2": {EPS: {"p4"}},
    "p3": {EPS: {"p4"}},
    "p4": {dig: {"p5"} for dig in d.DIGITS},
    "p5": {dig: {"p6"} for dig in d.DIGITS},
    "p6": {dig: {"p7"} for dig in d.DIGITS},
    "p7": {},
}

NFA_MEANING = {
    "p0": "start",
    "p1": "read M (Medicine branch)",
    "p2": "read S (Supplement branch)",
    "p3": "read C (Consumable branch)",
    "p4": "category done, expecting digit 1",
    "p5": "1 digit read",
    "p6": "2 digits read",
    "p7": "3 digits read (accept)",
}

# Column order used in every printed table: letters, then the digit class.
COLUMNS = ("M", "S", "C", "D")
_REP = {"M": "M", "S": "S", "C": "C", "D": "0"}   # representative symbol


def eps_closure(states: frozenset[str]) -> frozenset[str]:
    stack, seen = list(states), set(states)
    while stack:
        s = stack.pop()
        for t in NFA_DELTA[s].get(EPS, ()):
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return frozenset(seen)


def move(states: frozenset[str], symbol: str) -> frozenset[str]:
    out: set[str] = set()
    for s in states:
        out |= NFA_DELTA[s].get(symbol, set())
    return frozenset(out)


def nfa_accepts(text: str) -> bool:
    cur = eps_closure(frozenset({NFA_START}))
    for ch in text:
        if ch not in d.ALPHABET:
            return False
        cur = eps_closure(move(cur, ch))
    return bool(cur & NFA_ACCEPT)


def fmt(subset: frozenset[str]) -> str:
    return "{" + ", ".join(sorted(subset)) + "}" if subset else "∅"


# ---------------------------------------------------------------------------
# 2. Subset construction  (NFA -> DFA)
# ---------------------------------------------------------------------------
@dataclass
class SubsetDFA:
    names: dict[frozenset[str], str]            # subset -> DFA state name
    order: list[frozenset[str]]                 # discovery order
    delta: dict[str, dict[str, str]]            # name -> symbol -> name
    start: str
    accepting: set[str]
    log: list[str] = field(default_factory=list)
    steps: list[dict] = field(default_factory=list)


def subset_construction() -> SubsetDFA:
    # DFA states are named T0, T1, ... (not A, B, C ... because C and D are
    # already symbols in this project: C = Consumable, D = digit class).
    counter = iter(range(100))
    letters = (f"T{i}" for i in counter)
    start = eps_closure(frozenset({NFA_START}))
    names = {start: next(letters)}
    order, queue = [start], [start]
    delta: dict[str, dict[str, str]] = {}
    log = [f"Start: ε-closure({{{NFA_START}}}) = {fmt(start)}  = {names[start]}"]
    steps: list[dict] = []

    while queue:
        cur = queue.pop(0)
        cname = names[cur]
        delta[cname] = {}
        for col in COLUMNS:
            target = eps_closure(move(cur, _REP[col]))
            if target not in names:
                names[target] = "∅" if not target else next(letters)
                order.append(target)
                queue.append(target)
                tag = "  (new)"
            else:
                tag = ""
            delta[cname][col] = names[target]
            steps.append({
                "from": cname, "subset": sorted(cur), "symbol": col,
                "move": sorted(move(cur, _REP[col])), "closure": sorted(target),
                "result": names[target], "new": bool(tag),
            })
            log.append(
                f"δ'({cname}, {col}) = ε-closure(move({fmt(cur)}, {col})) "
                f"= {fmt(target)} = {names[target]}{tag}"
            )

    accepting = {names[s] for s in order if s & NFA_ACCEPT}
    return SubsetDFA(names, order, delta, names[start], accepting, log, steps)


# ---------------------------------------------------------------------------
# 3. Minimization  (partition refinement / Moore's algorithm)
# ---------------------------------------------------------------------------
@dataclass
class Minimized:
    rounds: list[list[set[str]]]                 # partition after each round
    blocks: list[set[str]]                       # final partition
    rename: dict[str, str]                       # old DFA state -> new name
    delta: dict[str, dict[str, str]]
    start: str
    accepting: set[str]
    unreachable: list[str]


def _reachable(dfa: SubsetDFA) -> set[str]:
    seen, stack = {dfa.start}, [dfa.start]
    while stack:
        s = stack.pop()
        for t in dfa.delta[s].values():
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return seen


def minimize(dfa: SubsetDFA) -> Minimized:
    states = list(dfa.delta)
    reach = _reachable(dfa)
    unreachable = [s for s in states if s not in reach]
    states = [s for s in states if s in reach]

    final = {s for s in states if s in dfa.accepting}
    nonfinal = set(states) - final
    partition = [b for b in (nonfinal, final) if b]
    rounds = [[set(b) for b in partition]]

    while True:
        where = {s: i for i, b in enumerate(partition) for s in b}
        new: list[set[str]] = []
        for block in partition:
            groups: dict[tuple, set[str]] = {}
            for s in sorted(block):
                sig = tuple(where[dfa.delta[s][c]] for c in COLUMNS)
                groups.setdefault(sig, set()).add(s)
            new.extend(groups.values())
        rounds.append([set(b) for b in new])
        if len(new) == len(partition):
            break
        partition = new

    # Name blocks to match definitions.py: the trap block is qDead, the rest
    # are numbered q0, q1, ... in breadth-first order from the start block.
    block_of = {s: i for i, b in enumerate(partition) for s in b}

    def succ(i: int) -> list[int]:
        rep = sorted(partition[i])[0]
        return [block_of[dfa.delta[rep][c]] for c in COLUMNS]

    def is_trap(i: int) -> bool:
        rep = sorted(partition[i])[0]
        return rep not in dfa.accepting and all(j == i for j in succ(i))

    names: dict[int, str] = {}
    queue, k = [block_of[dfa.start]], 0
    while queue:
        i = queue.pop(0)
        if i in names:
            continue
        if is_trap(i):
            names[i] = d.DEAD_STATE
        else:
            names[i] = f"q{k}"
            k += 1
        queue.extend(j for j in succ(i) if j not in names)

    rename = {s: names[block_of[s]] for s in states}
    delta: dict[str, dict[str, str]] = {}
    for i, b in enumerate(partition):
        rep = sorted(b)[0]
        delta[names[i]] = {c: rename[dfa.delta[rep][c]] for c in COLUMNS}
    return Minimized(
        rounds=rounds,
        blocks=[set(b) for b in partition],
        rename=rename,
        delta=delta,
        start=rename[dfa.start],
        accepting={rename[s] for s in dfa.accepting},
        unreachable=unreachable,
    )


def matches_hand_written_dfa(m: Minimized) -> bool:
    """True if the computed minimized DFA equals definitions.DELTA."""
    if set(m.delta) != set(d.STATES):
        return False
    if m.start != d.START_STATE or m.accepting != set(d.ACCEPTING_STATES):
        return False
    return all(
        m.delta[s][c] == d.step(s, _REP[c]) for s in d.STATES for c in COLUMNS
    )


# ---------------------------------------------------------------------------
# 4. Everything above as plain data (used by the web "Automata Theory" page)
# ---------------------------------------------------------------------------
def theory_report() -> dict:
    dfa = subset_construction()
    m = minimize(dfa)
    by_name = {v: k for k, v in dfa.names.items()}
    nfa_rows = []
    for q in NFA_STATES:
        row = NFA_DELTA[q]
        nfa_rows.append({
            "state": q,
            "cells": {c: sorted(row.get(_REP[c], set())) for c in COLUMNS},
            "eps": sorted(row.get(EPS, set())),
            "meaning": NFA_MEANING[q],
        })
    blocks = sorted(m.blocks, key=lambda b: m.rename[next(iter(b))])
    return {
        "alphabet": list(d.LETTERS) + list(d.DIGITS),
        "regex": d.REGEX,
        "columns": list(COLUMNS),
        "nfa": {"states": list(NFA_STATES), "start": NFA_START,
                "accepting": sorted(NFA_ACCEPT), "rows": nfa_rows},
        "subset": {
            "start": dfa.start,
            "steps": dfa.steps,
            "states": [{"name": dfa.names[s], "subset": sorted(s),
                        "accepting": dfa.names[s] in dfa.accepting,
                        "row": dfa.delta[dfa.names[s]]} for s in dfa.order],
            "possible_subsets": 2 ** len(NFA_STATES),
        },
        "minimization": {
            "unreachable": m.unreachable,
            "rounds": [[sorted(b, key=lambda x: (x == "∅", x)) for b in r] for r in m.rounds],
            "merged": [sorted(b) for b in m.blocks if len(b) > 1],
            "blocks": [{"members": sorted(b, key=lambda x: (x == "∅", x)),
                        "name": m.rename[next(iter(b))]} for b in blocks],
            "states": [{"name": q, "row": m.delta[q], "accepting": q in m.accepting,
                        "start": q == m.start} for q in d.STATES],
        },
        "counts": {"nfa": len(NFA_STATES), "dfa": len(dfa.delta), "min": len(m.delta)},
        "matches_simulator": matches_hand_written_dfa(m),
        "subset_names": {n: sorted(s) for n, s in by_name.items()},
    }
