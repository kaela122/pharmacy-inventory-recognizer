# Defense Script (12–15 minutes)

Replace "Member 1" to "Member 8" with your names. Timings add up to about 9½ minutes, which leaves room inside the 8–10 minute limit.

## Before the defense

- Start the backend and frontend (`start.bat`) **before** you are called. Log in as `ADMIN001` so the dashboard is already open.
- Open a second Command Prompt in the project folder for the CLI demo.
- Open the **Automata Theory** page in a second browser tab, set to the "2 · Subset construction" tab, for Members 4 and 5.
- Have `docs/AUTOMATA_DESIGN.md` or the report open to the NFA and minimization pages in case the panel asks.
- Backup plan: if the web app will not start, the whole demo still works with `python cli/simulator.py`. It needs nothing installed besides Python.

## Presentation

| Time | Who | What to say or show |
|---|---|---|
| 0:00–1:00 | Member 1, Project Leader | Introduce the group and roles. The problem: mistyped pharmacy product codes create records that break stock counts. Our system decides ACCEPTED or REJECTED using a minimized DFA, and the inventory refuses any code the DFA rejects. |
| 1:00–2:00 | Member 2, Language Analyst | Σ = {M, S, C, 0–9}, 13 symbols. L = one category letter then exactly three digits. \|L\| = 3,000. Show two accepted (`M001`, `C500`) and two rejected (`MM123`, `m123`) examples and say why. Mention it is regular because checking needs only a fixed amount of memory. |
| 2:00–3:00 | Member 3, RE/NFA Designer | R = (M\|S\|C)DDD. Explain union and concatenation, and that there is no star, so length is fixed at 4. Show the NFA diagram: three branches joined by ε-moves, then three digit steps. p7 is accepting. |
| 3:00–4:15 | Member 4, DFA Designer | **Web app → Automata Theory → 2 · Subset construction.** Press "Next step" a few times while explaining, then "Show all". Subset construction. Start with ε-closure({p0}) = {p0} = T0. On M we reach {p1, p4} = T1, and so on. 8 reachable subsets out of 256. T6 = {p7} is accepting. Show the DFA diagram. |
| 4:15–5:30 | Member 5, Automata Optimizer | **Automata Theory → 3 · Minimization.** Press "Next round" for each split; the page names the symbol that separates the states. No unreachable states. P0 splits final and non-final. Refinement splits off T5, then T4, then separates T0 from the dead state. T1, T2 and T3 have identical rows, so they merge into q1. 8 states → 6. Show the minimized diagram. |
| 5:30–7:30 | Member 6, Programmer | **Live demo.** (1) CLI: run `python cli/simulator.py`, type `M001` (accepted, trace q0→q4), `MM123` (rejected, dead state), `quit`. (2) Run `python cli/simulator.py --theory` and scroll to the last line: "Computed minimized DFA == DFA used by the simulator: YES". (3) Web: Code Recognizer, type `S250` then `m123`. (4) Medicines → Add Medicine, type `X12` and show that Save is blocked. |
| 7:30–8:30 | Member 7, Tester/QA | 10 accepted + 10 rejected + 5 edge cases, all pass. Run `python cli/simulator.py --demo` (last line: ALL CORRECT). Mention the equivalence test: RE, NFA, DFA and minimized DFA agree on more than 30,000 strings. |
| 8:30–9:30 | Member 8, Documentation Lead | Summarize: RE → NFA → DFA → minimized DFA → simulator, all equivalent, connected to a real inventory. State the limitations (format only, 3 digits, 3 categories). Thank the panel and open for questions. |

## Likely questions and answers

Everyone should be able to answer these, not just the member whose part it is.

**Why is this a regular language?**
Checking a code only needs to remember how far along the pattern we are, which is a fixed number of situations. Also, L is finite (3,000 strings), and every finite language is regular.

**Why did you need an NFA if you could write the DFA directly?**
The brief requires the full path. The NFA is also the natural translation of the RE: each union becomes branches and each concatenation becomes a chain. Subset construction then gives a DFA mechanically, and minimization guarantees the smallest one.

**What does ε-closure mean?**
The set of states you can reach from a state using only ε-moves, without reading input. From p1 you can reach p4 for free, so ε-closure({p1}) = {p1, p4}.

**Why only 8 subsets out of 256?**
Subset construction only creates subsets that are actually reachable from the start state. Most combinations, such as {p0, p7}, can never happen.

**Why did T1, T2 and T3 merge?**
After reading M, S or C, the rest of a valid code is exactly the same: three digits. Their rows in the table are identical and no string can tell them apart.

**Did minimization improve the model?**
Yes. 8 states became 6 (25% fewer), with one state per step of the pattern. The minimized DFA is the smallest possible for L, because every remaining state accepts a different shortest string (ε, 0, 00, 000, M000, or nothing).

**What is the dead state for?**
A DFA needs a transition for every symbol from every state. When the input can no longer become valid, the machine goes to qDead and stays there. Reaching qDead means the input will be rejected.

**Why is `m123` rejected when the Add Medicine form accepts `m123`?**
Lowercase `m` is not in Σ, so the automaton rejects it. The Add Medicine form converts input to uppercase **before** running the DFA, as a convenience for staff. That is preprocessing by the application; the language itself does not change.

**Why does `M01` end in q3 and not qDead?**
Every symbol it read was valid for its position, so the machine is waiting for one more digit. The input simply ended early. q3 is not accepting, so the result is REJECTED.

**How do you know the RE, NFA, DFA and minimized DFA are equivalent?**
The automated test `test_equivalence.py` runs every string up to length 5 (over M, S, C, two digits and three invalid symbols) through all four and they agree on all of them. The `--theory` mode also rebuilds the minimized DFA from the NFA and checks it matches the one the simulator uses.

**How would you add a new category, such as `V` for vaccines?**
Add `V` to Σ, change the RE to (M|S|C|V)DDD, add one NFA branch, and add the transition q0 --V--> q1 in the minimized DFA. The minimized DFA still has 6 states because the new branch merges into q1.

**How would you allow 4-digit item numbers?**
The RE becomes (M|S|C)DDDD. The DFA gains one more state in the chain, so the minimized DFA would have 7 states.

**Is the simulator really symbol by symbol?**
Yes. `dfa.run` loops over the input one character at a time, records each transition, and never looks ahead. The trace printed on screen is that record.
