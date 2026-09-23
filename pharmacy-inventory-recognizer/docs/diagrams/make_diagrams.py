"""Regenerate the state diagrams in this folder (needs Graphviz `dot`).
Run from the project root:  python docs/diagrams/make_diagrams.py
The diagrams are drawn from the same code the simulator uses."""
import os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "backend"))
from app.automata import construction as cons  # noqa: E402
from app.automata import definitions as d      # noqa: E402

HEAD = ('digraph G {\n rankdir=LR; bgcolor="white"; nodesep=0.35; ranksep=0.55;\n'
        ' node [shape=circle fontname="Helvetica" fontsize=13 width=0.6 fixedsize=false];\n'
        ' edge [fontname="Helvetica" fontsize=11];\n start [shape=point width=0.08];\n')


def label(syms):
    order = ["M", "S", "C", "0-9", "ε"]
    syms = sorted(set(syms), key=order.index)
    return ", ".join(syms)


def edges_from(delta_rows, dead=None):
    grouped = {}
    for src, row in delta_rows:
        for sym, dst in row:
            grouped.setdefault((src, dst), []).append(sym)
    out = ""
    for (a, b), s in grouped.items():
        # Edges into the trap state are drawn light so the main path stands out.
        style = ' color="gray60" fontcolor="gray40"' if b == dead and a != dead else ""
        out += f' "{a}" -> "{b}" [label="{label(s)}"{style}];\n'
    return out


def nfa():
    g = HEAD + f' start -> "{cons.NFA_START}";\n'
    for q in cons.NFA_STATES:
        shape = "doublecircle" if q in cons.NFA_ACCEPT else "circle"
        g += f' "{q}" [shape={shape}];\n'
    rows = []
    for q in cons.NFA_STATES:
        r = []
        for sym, dsts in cons.NFA_DELTA[q].items():
            s = "0-9" if sym in d.DIGITS else sym
            r += [(s, t) for t in dsts]
        rows.append((q, r))
    return g + edges_from(rows) + "}\n"


def dfa_graph(delta, start, accepting, dead, captions=None):
    g = HEAD + f' start -> "{start}";\n'
    for q in delta:
        shape = "doublecircle" if q in accepting else "circle"
        extra = ' style=dashed color="gray40" fontcolor="gray30"' if q == dead else ""
        lab = f'{q}\\n{captions[q]}' if captions and q in captions else q
        g += f' "{q}" [shape={shape} label="{lab}"{extra}];\n'
    rows = [(q, [("0-9" if c == "D" else c, t) for c, t in row.items()]) for q, row in delta.items()]
    g += f' {{ rank=sink; "{dead}"; }}\n'
    return g + edges_from(rows, dead) + "}\n"


def render(name, src):
    with open(os.path.join(HERE, name + ".dot"), "w", encoding="utf-8") as f:
        f.write(src)
    # PNG at high DPI for the report; SVG without DPI (a DPI setting breaks
    # the SVG viewBox and makes the drawing appear zoomed and clipped).
    subprocess.run(["dot", "-Tpng", "-Gdpi=160", "-o", os.path.join(HERE, f"{name}.png")],
                   input=src.encode("utf-8"), check=True)
    subprocess.run(["dot", "-Tsvg", "-o", os.path.join(HERE, f"{name}.svg")],
                   input=src.encode("utf-8"), check=True)
    # The web app's Automata Theory page shows the same SVGs.
    web = os.path.join(HERE, "..", "..", "frontend", "public", "diagrams")
    if os.path.isdir(web):
        shutil.copy(os.path.join(HERE, f"{name}.svg"), web)


if __name__ == "__main__":
    sub = cons.subset_construction()
    inv = {v: k for k, v in sub.names.items()}
    caps = {n: cons.fmt(s) for n, s in inv.items() if n != "∅"}
    m = cons.minimize(sub)
    render("nfa", nfa())
    render("dfa_subset", dfa_graph(sub.delta, sub.start, sub.accepting, "∅", caps))
    render("dfa_minimized", dfa_graph(m.delta, m.start, m.accepting, d.DEAD_STATE))
    print("diagrams written to", HERE)
