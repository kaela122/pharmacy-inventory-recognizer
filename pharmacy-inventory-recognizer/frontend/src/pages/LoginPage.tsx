import { useState } from "react";
import { login } from "../api";
import { saveAuth, type AuthUser } from "../lib/auth";

const DEMO = [
  { id:"ADMIN001", role:"System Admin", pw:"admin123" },
  { id:"PHARM001", role:"Pharmacist", pw:"pharma123" },
  { id:"INVMGR01", role:"Inventory Manager", pw:"invmgr123" },
];

export default function LoginPage({ onLogin }:{ onLogin:(u:AuthUser)=>void }){
  const [id,setId]=useState("ADMIN001");
  const [pw,setPw]=useState("admin123");
  const [show,setShow]=useState(false);
  const [err,setErr]=useState(""); const [busy,setBusy]=useState(false);

  async function submit(){
    setBusy(true); setErr("");
    try{ const u=await login(id.trim(),pw); saveAuth(u); onLogin(u); }
    catch(e){ setErr((e as Error).message); }
    finally{ setBusy(false); }
  }
  function pick(d:typeof DEMO[0]){ setId(d.id); setPw(d.pw); }

  return (
    <div className="login-wrap">
      <div className="login-box">
        <div className="login-logo">
          <div className="dot">💊</div>
          <h1>PharmaHub</h1><p>Inventory Management System</p>
        </div>
        <div className="panel">
          <h2 style={{textTransform:"none",fontSize:15,color:"var(--ink)",letterSpacing:0}}>🛡️ Terminal Sign In</h2>
          <p style={{color:"var(--muted)",fontSize:12.5,marginTop:-8,marginBottom:16}}>Access the inventory system from authorized terminals only.</p>
          {err && <div className="err">{err}</div>}
          <div className="field"><label>EMPLOYEE ID NUMBER</label>
            <input value={id} onChange={e=>setId(e.target.value)} onKeyDown={e=>e.key==="Enter"&&submit()}/></div>
          <div className="field"><label>SYSTEM PASSWORD</label>
            <div style={{position:"relative"}}>
              <input type={show?"text":"password"} value={pw} onChange={e=>setPw(e.target.value)} onKeyDown={e=>e.key==="Enter"&&submit()}/>
              <button onClick={()=>setShow(s=>!s)} style={{position:"absolute",right:10,top:9,background:"none",border:"none",color:"var(--faint)",cursor:"pointer"}}>{show?"🙈":"👁"}</button>
            </div></div>
          <button className="btn" style={{width:"100%",justifyContent:"center"}} onClick={submit} disabled={busy}>{busy?"Connecting…":"Authorize & Connect"}</button>
        </div>
        <div className="panel demo">
          <div className="dh">DEMO CREDENTIALS</div>
          {DEMO.map(d=>(
            <div className="demo-row" key={d.id} onClick={()=>pick(d)}>
              <span className="id">{d.id}</span><span className="rl">{d.role}</span>
            </div>
          ))}
        </div>
        <p style={{textAlign:"center",color:"var(--faint)",fontSize:10,marginTop:16,fontFamily:"var(--mono)"}}>CCAUTOMA · Automata-validated pharmacy inventory</p>
      </div>
    </div>
  );
}
