import { useEffect, useMemo, useState } from "react";
import { getTheory, type Theory } from "../api";

/* Automata Theory page
   Shows RE -> ε-NFA -> subset construction -> minimization, step by step.
   All data comes from GET /api/recognizer/theory, which is computed live by
   backend/app/automata/construction.py (the same code behind the CLI --theory). */

const COLS = ["M", "S", "C", "D"] as const;
const colLabel = (c: string) => (c === "D" ? "0–9" : c);
const set = (xs: string[]) => (xs.length ? `{${xs.join(", ")}}` : "∅");
const BLOCK_COLORS = ["var(--c1)", "var(--c2)", "var(--c4)", "var(--c0)", "var(--c3)", "var(--c6)"];

type Tab = "nfa" | "subset" | "min" | "compare";

export default function TheoryPage() {
  const [t, setT] = useState<Theory | null>(null);
  const [err, setErr] = useState("");
  const [tab, setTab] = useState<Tab>("nfa");
  useEffect(() => { getTheory().then(setT).catch(e => setErr(String(e.message || e))); }, []);

  if (err) return (<>
    <Header />
    <div className="panel"><p style={{ color: "var(--bad)", margin: 0 }}>Could not load the automata data from the backend ({err}). Make sure the backend is running.</p></div>
  </>);
  if (!t) return (<><Header /><div className="panel"><p style={{ color: "var(--muted)", margin: 0 }}>Building the automata…</p></div></>);

  return (
    <>
      <Header />
      <div className="th-summary">
        <div className="panel th-re">
          <span className="th-k">Regular expression</span>
          <span className="mono th-big">(M|S|C) D D D</span>
          <span className="th-small">D = 0|1|2|…|9 · Σ = {"{"}{t.alphabet.join(", ")}{"}"}</span>
        </div>
        <div className="panel th-flow">
          <Count n={t.counts.nfa} l="ε-NFA states" />
          <span className="th-arrow">→</span>
          <Count n={t.counts.dfa} l="DFA states" />
          <span className="th-arrow">→</span>
          <Count n={t.counts.min} l="minimized" hi />
          <span className={`badge ${t.matches_simulator ? "b-ok" : "b-bad"}`} style={{ marginLeft: "auto", alignSelf: "center" }}>
            {t.matches_simulator ? "✓ matches the simulator's DFA" : "✗ does not match"}
          </span>
        </div>
      </div>

      <div className="tabs" style={{ margin: "16px 0" }}>
        {([["nfa", "1 · ε-NFA"], ["subset", "2 · Subset construction"], ["min", "3 · Minimization"], ["compare", "4 · Comparison"]] as [Tab, string][]).map(([k, l]) =>
          <button key={k} className={`tab ${tab === k ? "active" : ""}`} onClick={() => setTab(k)}>{l}</button>)}
      </div>

      {tab === "nfa" && <NfaView t={t} />}
      {tab === "subset" && <SubsetView t={t} />}
      {tab === "min" && <MinView t={t} />}
      {tab === "compare" && <CompareView t={t} />}
    </>
  );
}

function Header() {
  return (<>
    <h2 className="page-h">Automata Theory</h2>
    <p className="page-sub">CCAUTOMA · how the recognizer's DFA was built: RE → ε-NFA → DFA → minimized DFA</p>
  </>);
}

function Count({ n, l, hi }: { n: number; l: string; hi?: boolean }) {
  return <div className="th-count"><b style={{ color: hi ? "var(--accent2)" : undefined }}>{n}</b><span>{l}</span></div>;
}

function Diagram({ src, alt }: { src: string; alt: string }) {
  return <div className="th-diagram"><img src={src} alt={alt} /></div>;
}

/* ---------------- 1. NFA ---------------- */
function NfaView({ t }: { t: Theory }) {
  const n = t.nfa;
  return (<>
    <div className="panel">
      <h2>Formal definition</h2>
      <p className="mono th-tuple">M<sub>N</sub> = (Q, Σ, δ, q₀, F)</p>
      <ul className="th-list">
        <li><b>Q</b> = {set(n.states)}</li>
        <li><b>Σ</b> = {set(t.alphabet)}</li>
        <li><b>q₀</b> = {n.start}</li>
        <li><b>F</b> = {set(n.accepting)}</li>
        <li><b>δ</b> : Q × (Σ ∪ {"{ε}"}) → P(Q), in the table below</li>
      </ul>
      <p className="th-note">The union (M|S|C) becomes three branches, ε-moves join them, and D D D becomes a chain of three digit steps. It is an NFA because of the ε-moves and because many (state, symbol) pairs have no move at all.</p>
    </div>
    <div className="panel">
      <h2>Transition table</h2>
      <div className="th-scroll"><table className="th-table">
        <thead><tr><th>δ</th>{COLS.map(c => <th key={c}>{colLabel(c)}</th>)}<th>ε</th><th>Meaning</th></tr></thead>
        <tbody>{n.rows.map(r => (
          <tr key={r.state}>
            <td className="mono"><StateTag name={r.state} start={r.state === n.start} acc={n.accepting.includes(r.state)} /></td>
            {COLS.map(c => <td key={c} className={`mono ${r.cells[c].length ? "" : "th-dim"}`}>{set(r.cells[c])}</td>)}
            <td className={`mono ${r.eps.length ? "th-eps" : "th-dim"}`}>{set(r.eps)}</td>
            <td className="th-muted">{r.meaning}</td>
          </tr>))}</tbody>
      </table></div>
      <p className="th-note">→ start state · ★ accepting state</p>
    </div>
    <div className="panel"><h2>State diagram</h2><Diagram src="/diagrams/nfa.svg" alt="ε-NFA state diagram" /></div>
  </>);
}

function StateTag({ name, start, acc }: { name: string; start?: boolean; acc?: boolean }) {
  return <span>{start ? "→ " : ""}{name}{acc ? " ★" : ""}</span>;
}

/* ---------------- 2. Subset construction ---------------- */
function SubsetView({ t }: { t: Theory }) {
  const steps = t.subset.steps;
  const [k, setK] = useState(0);          // number of steps revealed
  const [auto, setAuto] = useState(false);
  useEffect(() => {
    if (!auto) return;
    if (k >= steps.length) { setAuto(false); return; }
    const id = setTimeout(() => setK(x => x + 1), 650);
    return () => clearTimeout(id);
  }, [auto, k, steps.length]);

  const shown = steps.slice(0, k);
  const cur = k > 0 ? steps[k - 1] : null;
  const known = useMemo(() => {
    const s = new Set([t.subset.start]);
    shown.forEach(x => s.add(x.result));
    return t.subset.states.filter(st => s.has(st.name));
  }, [k, t]); // eslint-disable-line react-hooks/exhaustive-deps
  const cell = (from: string, c: string) => shown.find(x => x.from === from && x.symbol === c);
  const done = k >= steps.length;
  const subsetOf = (n: string) => t.subset_names[n] ?? [];

  return (<>
    <div className="panel">
      <h2>Step through the construction <span className="th-muted" style={{ textTransform: "none", letterSpacing: 0 }}>step {k} of {steps.length}</span></h2>
      <p className="th-note" style={{ marginTop: -6 }}>Each DFA state is a set of NFA states. For a DFA state T and symbol a: <span className="mono">δ′(T, a) = ε-closure(move(T, a))</span>. Start: <span className="mono">ε-closure({"{p0}"}) = {"{p0}"} = T0</span>.</p>
      <div className="th-controls">
        <button className="btn ghost sm" onClick={() => { setAuto(false); setK(0); }} disabled={k === 0}>⟲ Reset</button>
        <button className="btn ghost sm" onClick={() => { setAuto(false); setK(x => Math.max(0, x - 1)); }} disabled={k === 0}>◀ Back</button>
        <button className="btn sm" onClick={() => { setAuto(false); setK(x => Math.min(steps.length, x + 1)); }} disabled={done}>Next step ▶</button>
        <button className="btn ghost sm" onClick={() => setAuto(a => !a)} disabled={done}>{auto ? "❚❚ Pause" : "▶ Play"}</button>
        <button className="btn ghost sm" onClick={() => { setAuto(false); setK(steps.length); }} disabled={done}>Show all</button>
      </div>
      <div className="th-step mono">
        {cur ? <>
          δ′({cur.from}, {colLabel(cur.symbol)}) = ε-closure(move({set(cur.subset)}, {colLabel(cur.symbol)})) = ε-closure({set(cur.move)}) = {cur.closure.length ? <>{set(cur.closure)} = <b className={cur.new ? "th-new" : ""}>{cur.result}</b></> : <b className={cur.new ? "th-new" : ""}>∅ (dead state)</b>}{cur.new ? "  — new state" : ""}
        </> : <span className="th-muted">Press “Next step” to start from T0 = {"{p0}"}.</span>}
      </div>
    </div>

    <div className="panel">
      <h2>DFA built so far <span className="th-muted" style={{ textTransform: "none", letterSpacing: 0 }}>{known.length} state{known.length === 1 ? "" : "s"} discovered</span></h2>
      <div className="th-scroll"><table className="th-table">
        <thead><tr><th>DFA state</th><th>NFA subset</th>{COLS.map(c => <th key={c}>{colLabel(c)}</th>)}</tr></thead>
        <tbody>{known.map(st => (
          <tr key={st.name} className={cur && cur.from === st.name ? "th-row-on" : ""}>
            <td className="mono"><StateTag name={st.name === "∅" ? "∅ (dead)" : st.name} start={st.name === t.subset.start} acc={st.accepting} /></td>
            <td className="mono th-muted">{set(subsetOf(st.name))}</td>
            {COLS.map(c => {
              const x = cell(st.name, c);
              const on = cur && x === cur;
              return <td key={c} className={`mono ${on ? "th-cell-on" : ""} ${x ? "" : "th-dim"}`}>{x ? x.result : "·"}</td>;
            })}
          </tr>))}</tbody>
      </table></div>
      {done && <p className="th-note">Done. Only <b>{t.subset.states.length}</b> of the {t.subset.possible_subsets} possible subsets are reachable. Accepting: <b>{t.subset.states.filter(s => s.accepting).map(s => s.name).join(", ")}</b> (the subsets containing {t.nfa.accepting.join(", ")}).</p>}
    </div>

    {done && <div className="panel"><h2>DFA state diagram</h2><Diagram src="/diagrams/dfa_subset.svg" alt="DFA from subset construction" /></div>}
  </>);
}

/* ---------------- 3. Minimization ---------------- */
function MinView({ t }: { t: Theory }) {
  const m = t.minimization;
  const last = m.rounds.length - 1;
  const [r, setR] = useState(0);
  const colorOf = useMemo(() => {
    // Colour every state by its FINAL block so you can watch the blocks separate.
    const map: Record<string, string> = {};
    m.blocks.forEach((b, i) => b.members.forEach(s => { map[s] = BLOCK_COLORS[i % BLOCK_COLORS.length]; }));
    return map;
  }, [m]);
  const rowOf = (st: string) => t.subset.states.find(x => x.name === st)!.row;
  const explain = (i: number) => {
    if (i === 0) return "Start by separating final states from non-final states.";
    const prev = m.rounds[i - 1], now = m.rounds[i];
    if (now.length === prev.length) return "No block splits: every state in a block moves into the same blocks on every symbol. The partition is stable, so the algorithm stops.";
    const blockIn = (st: string) => prev.findIndex(b => b.includes(st));
    const split = prev.filter(b => !now.some(n => n.length === b.length && n.every(x => b.includes(x))));
    return split.map(b => {
      const parts = now.filter(n => n.every(x => b.includes(x)));
      const [A, B] = parts;
      const c = COLS.find(col => blockIn(rowOf(A[0])[col]) !== blockIn(rowOf(B[0])[col])) ?? "D";
      const targets = (grp: string[]) => [...new Set(grp.map(x => rowOf(x)[c]))].join(", ");
      return `${set(b)} splits into ${parts.map(set).join(" and ")}. On ${colLabel(c)}, ${A.join(", ")} go${A.length === 1 ? "es" : ""} to ${targets(A)} but ${B.join(", ")} go${B.length === 1 ? "es" : ""} to ${targets(B)}, and those are in different blocks of P${i - 1}.`;
    }).join(" ");
  };
  const sym = (s: string) => (s === "∅" ? "∅" : s);

  return (<>
    <div className="panel">
      <h2>Partition refinement <span className="th-muted" style={{ textTransform: "none", letterSpacing: 0 }}>round P{r} of P{last}</span></h2>
      <p className="th-note" style={{ marginTop: -6 }}>Unreachable states removed: <b>{m.unreachable.length ? m.unreachable.join(", ") : "none"}</b>. Two states stay in the same block only if, for every symbol, their transitions lead into the same block.</p>
      <div className="th-controls">
        <button className="btn ghost sm" onClick={() => setR(x => Math.max(0, x - 1))} disabled={r === 0}>◀ Back</button>
        <button className="btn sm" onClick={() => setR(x => Math.min(last, x + 1))} disabled={r === last}>Next round ▶</button>
        <button className="btn ghost sm" onClick={() => setR(last)} disabled={r === last}>Show final</button>
      </div>
      <div className="th-rounds">
        {m.rounds.slice(0, r + 1).map((round, i) => (
          <div key={i} className={`th-round ${i === r ? "on" : ""}`}>
            <span className="mono th-pl">P{i}</span>
            <div className="th-blocks">{round.map((b, j) => (
              <span key={j} className="th-block">{b.map(s => <span key={s} className="th-chip mono" style={{ borderColor: colorOf[s], color: colorOf[s] }}>{sym(s)}</span>)}</span>
            ))}</div>
          </div>))}
      </div>
      <p className="th-explain">{explain(r)}</p>
    </div>

    {r === last && <>
      <div className="panel">
        <h2>Why T1, T2 and T3 are equivalent</h2>
        <div className="th-scroll"><table className="th-table">
          <thead><tr><th>State</th>{COLS.map(c => <th key={c}>{colLabel(c)}</th>)}<th>Final?</th></tr></thead>
          <tbody>{t.subset.states.filter(s => m.merged.flat().includes(s.name)).map(s => (
            <tr key={s.name}><td className="mono">{s.name}</td>{COLS.map(c => <td key={c} className="mono">{s.row[c]}</td>)}<td>{s.accepting ? "yes" : "no"}</td></tr>))}</tbody>
        </table></div>
        <p className="th-note">Identical rows and none is final. After reading M, S or C, the rest of a valid code is always exactly three digits, so no string can tell these states apart. They merge into one state.</p>
      </div>
      <div className="panel">
        <h2>State merging</h2>
        <div className="th-merge">{m.blocks.map((b, i) => (
          <div key={b.name} className="th-mrow">
            <span className="th-block">{b.members.map(s => <span key={s} className="th-chip mono" style={{ borderColor: BLOCK_COLORS[i % BLOCK_COLORS.length], color: BLOCK_COLORS[i % BLOCK_COLORS.length] }}>{sym(s)}</span>)}</span>
            <span className="th-arrow">→</span><b className="mono">{b.name}</b>
          </div>))}</div>
      </div>
      <div className="panel">
        <h2>Minimized DFA</h2>
        <p className="mono th-tuple">M<sub>min</sub> = (Q′, Σ, δ′, q0, F′) · F′ = {set(m.states.filter(x => x.accepting).map(x => x.name))}</p>
        <div className="th-scroll"><table className="th-table">
          <thead><tr><th>State</th>{COLS.map(c => <th key={c}>{colLabel(c)}</th>)}</tr></thead>
          <tbody>{m.states.map(s => (
            <tr key={s.name}><td className="mono"><StateTag name={s.name} start={s.start} acc={s.accepting} /></td>
              {COLS.map(c => <td key={c} className={`mono ${s.row[c] === "qDead" ? "th-dim" : ""}`}>{s.row[c]}</td>)}</tr>))}</tbody>
        </table></div>
        <p className="th-note">This is exactly the DFA the Code Recognizer and the Medicines form use.</p>
      </div>
      <div className="panel"><h2>Minimized DFA diagram</h2><Diagram src="/diagrams/dfa_minimized.svg" alt="Minimized DFA" /></div>
    </>}
  </>);
}

/* ---------------- 4. Comparison ---------------- */
function CompareView({ t }: { t: Theory }) {
  const c = t.counts;
  const saved = c.dfa - c.min;
  return (<>
    <div className="panel">
      <h2>NFA vs DFA vs minimized DFA</h2>
      <div className="th-scroll"><table className="th-table">
        <thead><tr><th></th><th>ε-NFA</th><th>DFA (subset construction)</th><th>Minimized DFA</th></tr></thead>
        <tbody>
          <tr><td>States</td><td className="mono">{c.nfa}</td><td className="mono">{c.dfa}</td><td className="mono"><b style={{ color: "var(--accent2)" }}>{c.min}</b></td></tr>
          <tr><td>ε-transitions</td><td className="mono">{t.nfa.rows.filter(r => r.eps.length).length}</td><td className="mono">0</td><td className="mono">0</td></tr>
          <tr><td>Deterministic</td><td>no</td><td>yes</td><td>yes</td></tr>
          <tr><td>Accepting</td><td className="mono">{set(t.nfa.accepting)}</td><td className="mono">{set(t.subset.states.filter(s => s.accepting).map(s => s.name))}</td><td className="mono">{set(t.minimization.states.filter(s => s.accepting).map(s => s.name))}</td></tr>
        </tbody>
      </table></div>
    </div>
    <div className="panel">
      <h2>Did minimization improve the model?</h2>
      <p style={{ margin: "0 0 10px", fontSize: 14 }}><b>Yes.</b> It removed {saved} of {c.dfa} states ({Math.round(100 * saved / c.dfa)}%). The subset DFA kept one state per category letter (T1, T2, T3) because the NFA had one branch per letter. They behave identically, so they merged into q1.</p>
      <p style={{ margin: 0, fontSize: 14, color: "var(--muted)" }}>The result is the smallest DFA for this language: each remaining state accepts a different shortest string (ε, 0, 00, 000, M000, or nothing), so no two can be merged.</p>
    </div>
    <div className="panel">
      <h2>Equivalence</h2>
      <p style={{ margin: 0, fontSize: 14 }}>The minimized DFA on this page is computed live from the ε-NFA by the backend. {t.matches_simulator
        ? <span style={{ color: "var(--ok)" }}><b>It is identical to the DFA used by the recognizer and the simulator.</b></span>
        : <span style={{ color: "var(--bad)" }}><b>It does not match the recognizer's DFA.</b></span>} The automated test <span className="mono">test_equivalence.py</span> also checks that the RE, NFA, DFA and minimized DFA agree on more than 30,000 strings.</p>
    </div>
  </>);
}
