import { useState } from "react";
import { runDFA, dfaReason, catName, START, DEAD } from "../lib/dfa";

const CHAIN = ["q0","q1","q2","q3","q4"];

export default function RecognizerPage(){
  const [code,setCode]=useState("M001"); const [active,setActive]=useState(START);
  const [res,setRes]=useState<ReturnType<typeof runDFA>|null>(null);
  function run(){
    const raw=code.trim().toUpperCase(); const r=runDFA(raw); setRes(r); setActive(START);
    if(!r.steps.length){ setActive(r.final); return; }
    let k=0; const t=setInterval(()=>{ if(k>=r.steps.length){clearInterval(t);return;} setActive(r.steps[k].to); k++; },460);
  }
  const raw=code.trim().toUpperCase(); const good=res?.accepted;
  return (
    <>
      <h2 className="page-h">Code Recognizer</h2><p className="page-sub">COM244 · minimized DFA</p>
      <div className="panel">
        <h2 style={{textTransform:"none",fontSize:14,color:"var(--ink)",letterSpacing:0}}>Validate a pharmacy product code</h2>
        <p style={{color:"var(--muted)",fontSize:13,marginTop:-8,marginBottom:12}}>Valid: a letter (M, S or C) then 3 digits — e.g. <span className="mono">M001</span>. Regex <span className="mono">(M|S|C)(0-9)(0-9)(0-9)</span></p>
        <div style={{display:"flex",gap:10}}>
          <input className="mono" value={code} maxLength={10} onChange={e=>setCode(e.target.value)} onKeyDown={e=>e.key==="Enter"&&run()}/>
          <button className="btn" onClick={run}>Validate</button></div>
        <div className="rec-chain">
          {CHAIN.map((s,i)=>(<span key={s} style={{display:"flex",alignItems:"center",gap:6}}>
            <span className={`node ${active===s?"on":""} ${s==="q4"?"acc":""}`}>{s}</span>
            {i<CHAIN.length-1 && <span className="arw">→</span>}</span>))}
          <span className="arw" style={{margin:"0 6px"}}>·</span>
          <span className={`node dead ${active===DEAD?"on":""}`}>dead</span>
        </div>
        {res && <div>
          <div style={{fontSize:20,fontWeight:800,color:good?"var(--ok)":"var(--bad)"}}>{good?"✓ ACCEPTED":"✗ REJECTED"}</div>
          <div style={{color:"var(--muted)",fontSize:14,margin:"2px 0 4px"}}>{dfaReason(raw,res)}</div>
          {good && <div style={{fontSize:14}}>Category <b>{catName(raw[0])}</b> · Item <b>{raw.slice(1)}</b></div>}
          <div style={{color:"var(--muted)",fontSize:13,marginTop:4}}>Final state: <b style={{color:"var(--ink)"}}>{res.final}</b></div>
          {res.steps.length>0 && <ul className="trace">{res.steps.map((s,i)=>(
            <li key={i} className={s.ok?"":"bad"}><span>read '{s.c}'</span><span>{s.from} → {s.to}{s.ok?"":" ✗"}</span></li>))}</ul>}
        </div>}
      </div>
      <div className="panel"><h2>Why it matters here</h2>
        <p style={{color:"var(--muted)",margin:0,fontSize:13.5}}>Every medicine added on the Medicines screen runs through this exact automaton before it can be saved. This links your COM244 automata theory to the pharmacy inventory system.</p></div>
    </>
  );
}
